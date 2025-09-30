import pickle
import re
from flask import Flask, request, jsonify

# Initialize the Flask application
app = Flask(__name__)

# --- 1. LOAD THE SAVED MODEL AND VECTORIZER ---
with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

# --- 2. DEFINE THE PREPROCESSING FUNCTION ---
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- 3. CREATE THE PREDICTION API ENDPOINT ---
@app.route('/predict', methods=['POST'])
def predict():
    # Get the JSON data from the request body
    data = request.get_json(force=True)
    comment = data['comment']
    
    # Process the comment
    cleaned_comment = preprocess_text(comment)
    comment_tfidf = vectorizer.transform([cleaned_comment])
    
    # Make prediction
    prediction = model.predict(comment_tfidf)[0]
    probability = model.predict_proba(comment_tfidf)[0]
    
    # Determine the label and confidence
    if prediction == 1:
        label = 'toxic'
        confidence = probability[1]
    else:
        label = 'not-toxic'
        confidence = probability[0]
        
    # Return the result as JSON
    return jsonify({
        'comment': comment,
        'label': label,
        'confidence': confidence
    })

# --- 4. RUN THE FLASK APP ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)