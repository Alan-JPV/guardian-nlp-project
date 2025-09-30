import pandas as pd
import re
from sklearn.model_selection import train_test_split

# --- 1. LOAD AND PREPROCESS DATA ---
# Load the dataset
df = pd.read_csv('data/train.csv')

# Define the text cleaning function
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Apply the function to create a new 'cleaned_text' column
df['cleaned_text'] = df['comment_text'].apply(preprocess_text)
print("✅ Data loaded and cleaned successfully.")


# --- 2. SPLIT THE DATA ---
# Define features (X) and target (y)
X = df['cleaned_text']
y = df['toxic']

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print("✅ Data split complete.")
print(f"   - Training samples: {len(X_train)}")
print(f"   - Testing samples: {len(X_test)}")