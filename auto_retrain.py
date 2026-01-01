"""
Auto-Retrain Script for Railway Cron Jobs

This script automatically retrains the model on latest Supabase data.
Run this periodically (e.g., daily) to keep model updated with new freelancers.

Usage:
  python auto_retrain.py
"""

from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from supabase import create_client
from config import MODEL_PATH, WEIGHTS, SUPABASE_URL, SUPABASE_KEY
import os
from datetime import datetime

def retrain():
    print("=" * 70)
    print(f"Auto-Retrain Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        print("1. Connecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("2. Fetching all freelancers...")
        response = supabase.table("freelancers").select("skills").execute()
        
        if not response.data:
            print("[ERROR] No data found in Supabase!")
            return False
        
        print(f"[OK] Found {len(response.data)} freelancers")
        
        # Convert to DataFrame
        df = pd.DataFrame(response.data)
        
        # Process skills
        def process_skills(skills):
            if skills is None or skills == '':
                return ''
            if isinstance(skills, list):
                return ' '.join([str(s).lower() for s in skills])
            return str(skills).lower().replace(';', ' ').replace(',', ' ')
        
        print("3. Processing skills...")
        df['skills_clean'] = df['skills'].apply(process_skills)
        df = df[df['skills_clean'].str.strip() != '']
        print(f"[OK] {len(df)} freelancers with valid skills")
        
        # Train TF-IDF
        print("4. Training TF-IDF vectorizer...")
        vectorizer = TfidfVectorizer(lowercase=True, max_features=500)
        vectorizer.fit(df['skills_clean'])
        
        print(f"[OK] Learned vocabulary of {len(vectorizer.vocabulary_)} unique skills")
        
        # Save model
        print("5. Saving model...")
        os.makedirs('models', exist_ok=True)
        
        model_data = {
            'vectorizer': vectorizer,
            'weights': WEIGHTS
        }
        
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model_data, f)
        
        print("\n" + "=" * 70)
        print("[SUCCESS] Auto-Retrain Complete!")
        print("=" * 70)
        print(f"Freelancers: {len(df)}")
        print(f"Vocabulary: {len(vectorizer.vocabulary_)} skills")
        print(f"Model saved: {MODEL_PATH}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error during retraining: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = retrain()
    exit(0 if success else 1)

