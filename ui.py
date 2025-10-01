import streamlit as st
import whisper
import requests
import os
import av # Replaced moviepy with PyAV

# --- App Configuration ---
st.set_page_config(page_title="AudioTox Guard", page_icon="🎙️", layout="centered")

# --- App Title and Description ---
st.title("🎙️ AudioTox Guard")
st.write("Upload a video or audio file to detect toxic speech.")
st.info("This UI transcribes audio using OpenAI's Whisper, then sends the text to the Guardian NLP backend API for toxicity analysis.")

# --- Cached Function to Load Whisper Model ---
@st.cache_resource
def load_whisper_model():
    model = whisper.load_model("tiny")
    return model

model = load_whisper_model()

# --- Helper Functions ---
def save_uploaded_file(uploaded_file):
    """Saves the uploaded file to a temporary directory."""
    try:
        os.makedirs("temp", exist_ok=True)
        file_path = os.path.join("temp", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def extract_audio_from_video(video_path):
    """Extracts audio from a video file using PyAV and saves it as a temporary mp3."""
    try:
        audio_path = os.path.join("temp", "extracted_audio.mp3")
        with av.open(video_path) as container:
            # Find the first audio stream
            audio_stream = next((s for s in container.streams if s.type == 'audio'), None)
            if audio_stream is None:
                st.error("No audio stream found in the video.")
                return None
            
            # Open a new container to write the output audio file
            with av.open(audio_path, 'w') as out_container:
                # Add a new audio stream to the output container (encoding to mp3)
                out_stream = out_container.add_stream('mp3')
                # Decode and encode the audio frames
                for frame in container.decode(audio_stream):
                    for packet in out_stream.encode(frame):
                        out_container.mux(packet)
        return audio_path
    except Exception as e:
        st.error(f"Failed to extract audio with PyAV: {e}")
        return None

# --- Main Application Logic ---
uploaded_file = st.file_uploader(
    "Choose a video or audio file...", 
    type=["mp4", "mov", "avi", "mp3", "wav", "m4a"]
)

if uploaded_file:
    temp_file_path = save_uploaded_file(uploaded_file)
    
    if temp_file_path:
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        is_video = file_extension in ['.mp4', '.mov', '.avi']
        
        if is_video:
            st.video(temp_file_path)
        else:
            st.audio(temp_file_path)
        
        if st.button("Analyze Speech"):
            audio_path_for_transcription = None
            
            with st.spinner("Step 1/3: Preparing audio..."):
                if is_video:
                    audio_path_for_transcription = extract_audio_from_video(temp_file_path)
                else:
                    audio_path_for_transcription = temp_file_path
            
            if audio_path_for_transcription:
                with st.spinner("Step 2/3: Transcribing audio to text..."):
                    try:
                        result = model.transcribe(audio_path_for_transcription, fp16=False)
                        transcribed_text = result["text"]
                        st.subheader("📝 Transcribed Text")
                        st.write(transcribed_text)
                    except Exception as e:
                        st.error(f"Audio transcription failed: {e}")
                        transcribed_text = None
                
                if transcribed_text:
                    with st.spinner("Step 3/3: Analyzing text for toxicity..."):
                        try:
                            api_url = "http://backend:5000/predict"
                            response = requests.post(api_url, json={"comment": transcribed_text})
                            response.raise_for_status()
                            api_result = response.json()
                            
                            label = api_result['label']
                            confidence = float(api_result['confidence']) * 100
                            
                            st.subheader("🔬 Analysis Result")
                            if label.lower() == 'toxic':
                                st.error(f"**Result: {label.capitalize()}** (Confidence: {confidence:.2f}%)")
                            else:
                                st.success(f"**Result: {label.capitalize()}** (Confidence: {confidence:.2f}%)")
                        
                        except requests.exceptions.RequestException as e:
                            st.error(f"Could not connect to the backend API. Is it running? Error: {e}")

            # Clean up temporary files
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if is_video and audio_path_for_transcription and os.path.exists(audio_path_for_transcription):
                os.remove(audio_path_for_transcription)