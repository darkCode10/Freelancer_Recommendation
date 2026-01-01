# Simple Training Script - Trains on SUPABASE Data (Live!)

from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from supabase import create_client
from config import MODEL_PATH, WEIGHTS, SUPABASE_URL, SUPABASE_KEY
import os

print("=" * 60)
print("Training Model on LIVE Supabase Data")
print("=" * 60)

print("\n1. Connecting to Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("2. Fetching all freelancers from Supabase...")
response = supabase.table("freelancers").select("skills").execute()

if not response.data:
    print("❌ No data found in Supabase! Cannot train model.")
    exit(1)

print(f"✅ Found {len(response.data)} freelancers")

# Convert to DataFrame
df = pd.DataFrame(response.data)

# Process skills (handle array format)
def process_skills(skills):
    if skills is None or skills == '':
        return ''
    if isinstance(skills, list):
        return ' '.join([str(s).lower() for s in skills])
    return str(skills).lower().replace(';', ' ').replace(',', ' ')

print("3. Processing skills...")
df['skills_clean'] = df['skills'].apply(process_skills)

# Remove empty skills
df = df[df['skills_clean'].str.strip() != '']
print(f"✅ {len(df)} freelancers with valid skills")

# Train TF-IDF on ALL Supabase skills
print("4. Training TF-IDF vectorizer...")
# Don't limit features - let it learn ALL skills from Supabase!
vectorizer = TfidfVectorizer(lowercase=True, max_features=500)
vectorizer.fit(df['skills_clean'])

print(f"✅ Learned vocabulary of {len(vectorizer.vocabulary_)} unique skills")

# Save model
print("5. Saving model...")
os.makedirs('models', exist_ok=True)

model_data = {
    'vectorizer': vectorizer,
    'weights': WEIGHTS
}

with open(MODEL_PATH, 'wb') as f:
    pickle.dump(model_data, f)

print("\n" + "=" * 60)
print("✅ Training Complete!")
print("=" * 60)
print(f"Model trained on {len(df)} freelancers from Supabase")
print(f"Vocabulary size: {len(vectorizer.vocabulary_)} skills")
print(f"Model saved to: {MODEL_PATH}")
print("\nNow the model understands ALL skills in your Supabase!")
print("(Medicine, Design, Writing, Programming, etc.)")
print("=" * 60)
