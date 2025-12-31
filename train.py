# Simple Training Script - Trains on CSV Dataset

import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from config import MODEL_PATH, WEIGHTS

print("Loading data from CSV...")
df = pd.read_csv('final_dataset.csv')

print(f"Found {len(df)} freelancers")

print("Cleaning data...")
# Clean data
df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
df['years_of_experience'] = pd.to_numeric(df['years_of_experience'], errors='coerce').fillna(0)
df['Skills'] = df['Skills'].fillna('')

# Process skills
print("Processing skills...")
df['skills_clean'] = df['Skills'].str.lower().str.replace(';', ' ')

# Train TF-IDF on skills
print("Training TF-IDF on dataset...")
vectorizer = TfidfVectorizer(max_features=100, lowercase=True)
vectorizer.fit(df['skills_clean'])

# Save model (only vectorizer and weights, not the data!)
print("Saving model...")
import os
os.makedirs('models', exist_ok=True)

model_data = {
    'vectorizer': vectorizer,
    'weights': WEIGHTS
}

with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model_data, f)

print("Done! Model trained on CSV dataset.")
print(f"Total records used for training: {len(df)}")
print("Model will fetch fresh data from Supabase during predictions!")
