# Simple Training Script - Run this first!

import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from config import DATA_PATH, MODEL_PATH, WEIGHTS

print("Loading data...")
df = pd.read_csv(DATA_PATH)

# Clean data
print("Cleaning data...")
df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
df['years_of_experience'] = pd.to_numeric(df['years_of_experience'], errors='coerce').fillna(0)
df['Skills'] = df['Skills'].fillna('')

# Process skills - make lowercase and clean
print("Processing skills...")
df['skills_clean'] = df['Skills'].str.lower().str.replace(';', ' ')

# Normalize rating and experience to 0-1
print("Normalizing features...")
scaler = MinMaxScaler()
df[['rating_norm', 'experience_norm']] = scaler.fit_transform(df[['rating', 'years_of_experience']])

# Keep original values too
df['rating_original'] = df['rating']
df['experience_original'] = df['years_of_experience']

# Train TF-IDF on skills
print("Training TF-IDF...")
vectorizer = TfidfVectorizer(max_features=100, lowercase=True)
skill_matrix = vectorizer.fit_transform(df['skills_clean'])

# Save everything
print("Saving model...")
import os
os.makedirs('models', exist_ok=True)

model_data = {
    'df': df,
    'vectorizer': vectorizer,
    'skill_matrix': skill_matrix,
    'weights': WEIGHTS
}

with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model_data, f)

print("Done! Model trained and saved.")
print(f"Total freelancers: {len(df)}")

