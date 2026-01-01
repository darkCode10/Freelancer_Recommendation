# Simple FastAPI App - Fetches live data from Supabase for predictions

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config import MODEL_PATH, API_PORT, SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE, WEIGHTS, MIN_SKILL_MATCH

# Create app
app = FastAPI(title="Freelancer Recommendations")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load trained model (vectorizer only)
model_data = None

@app.on_event("startup")
def load_model():
    global model_data
    print("Loading trained model...")
    with open(MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)
    print("Model loaded! Will fetch fresh data from Supabase for each request.")


# Request format
class RecommendRequest(BaseModel):
    skills: List[str]
    top_n: int = 5


# Main endpoint - Fetches LIVE data from Supabase!
@app.post("/recommend")
def get_recommendations(request: RecommendRequest):
    """
    Get freelancer recommendations from Supabase
    
    Training: Done on CSV dataset (offline)
    Prediction: Fetches LIVE data from Supabase (real-time)
    Joins freelancers with freelancer_reviews to calculate ratings
    """
    
    try:
        print("Fetching live data from Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Fetch freelancers
        freelancers_response = supabase.table("freelancers").select("id, username, skills, experience").execute()
        
        if not freelancers_response.data:
            return {
                "success": False,
                "total": 0,
                "recommendations": [],
                "message": "No freelancers found in Supabase"
            }
        
        # Debug: Print first freelancer
        print(f"Sample freelancer: {freelancers_response.data[0]}")
        
        # Fetch reviews
        reviews_response = supabase.table("freelancer_reviews").select("freelancer, stars").execute()
        
        # Convert to DataFrames
        df_freelancers = pd.DataFrame(freelancers_response.data)
        df_reviews = pd.DataFrame(reviews_response.data) if reviews_response.data else pd.DataFrame(columns=['freelancer', 'stars'])
        
        print(f"Fetched {len(df_freelancers)} freelancers from Supabase")
    
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Error fetching data: {str(e)}"
        }
    
    try:
        # Calculate average rating and completed projects for each freelancer
        if not df_reviews.empty:
            df_reviews['stars'] = pd.to_numeric(df_reviews['stars'], errors='coerce')
            rating_stats = df_reviews.groupby('freelancer').agg(
                rating=('stars', 'mean'),
                completed_projects=('stars', 'count')
            ).reset_index()
        else:
            rating_stats = pd.DataFrame(columns=['freelancer', 'rating', 'completed_projects'])
        
        # Merge freelancers with their ratings
        df = df_freelancers.merge(
            rating_stats, 
            left_on='id', 
            right_on='freelancer', 
            how='left'
        )
        
        # Clean and rename columns
        df['rating'] = df['rating'].fillna(0)
        df['completed_projects'] = df['completed_projects'].fillna(0)
        df['experience'] = pd.to_numeric(df['experience'], errors='coerce').fillna(0)
        
        # Handle skills - convert array to string if needed
        def process_skills(skills):
            if skills is None or skills == '':
                return ''
            # If it's a list/array, join it
            if isinstance(skills, list):
                return ' '.join([str(s).lower() for s in skills])
            # If it's a string, just clean it
            return str(skills).lower().replace(';', ' ').replace(',', ' ')
        
        df['skills_clean'] = df['skills'].apply(process_skills)
        df['skills_display'] = df['skills'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x) if x else '')
        
        # Rename to match model expectations
        df['name'] = df['username']
        df['years_of_experience'] = df['experience']
        
        print(f"Processed {len(df)} freelancers")
        
        # Normalize features
        scaler = MinMaxScaler()
        df[['rating_norm', 'experience_norm']] = scaler.fit_transform(df[['rating', 'years_of_experience']])
        
        # Use trained vectorizer to transform Supabase skills
        vectorizer = model_data['vectorizer']
        weights = model_data['weights']
        
        skill_matrix = vectorizer.transform(df['skills_clean'])
        
        # Process user skills with trained vectorizer
        user_skills = ' '.join(request.skills).lower()
        user_vector = vectorizer.transform([user_skills])
        
        # Calculate similarity
        similarities = cosine_similarity(user_vector, skill_matrix).flatten()
        
        # ⚠️ CRITICAL: Filter out freelancers with 0 or very low skill match!
        print(f"User searching for: {user_skills}")
        print(f"Skill matches before filter: min={similarities.min():.3f}, max={similarities.max():.3f}")
        
        # Only keep freelancers with at least MIN_SKILL_MATCH similarity
        valid_mask = similarities >= MIN_SKILL_MATCH
        
        if not valid_mask.any():
            return {
                "success": False,
                "total": 0,
                "recommendations": [],
                "message": f"No freelancers found with matching skills for: {', '.join(request.skills)}"
            }
        
        # Filter dataframe and similarities
        df_filtered = df[valid_mask].copy()
        similarities_filtered = similarities[valid_mask]
        
        print(f"✅ {len(df_filtered)} freelancers have matching skills (>= {MIN_SKILL_MATCH*100:.0f}%)")
        
        # Calculate final score (skills is 70% weight now!)
        scores = (
            weights['skills'] * similarities_filtered +
            weights['rating'] * df_filtered['rating_norm'].values +
            weights['experience'] * df_filtered['experience_norm'].values
        )
        
        # Get top N from filtered results
        top_indices = scores.argsort()[-min(request.top_n, len(scores)):][::-1]
        
        # Format results (use filtered data!)
        results = []
        for idx in top_indices:
            row = df_filtered.iloc[idx]
            # Get the original index to access similarities_filtered correctly
            original_idx = df_filtered.index[idx]
            filtered_idx = list(df[valid_mask].index).index(original_idx)
            
            results.append({
                "id": str(row['id']),
                "name": row['name'],
                "score": float(scores[idx]),
                "match": float(similarities_filtered[idx] * 100),  # Show actual match percentage
                "rating": float(row['rating']),
                "experience": int(row['years_of_experience']),
                "completed_projects": int(row['completed_projects']),
                "skills": row['skills_display']
            })
        
        return {
            "success": True,
            "total": len(results),
            "recommendations": results
        }
        
    except Exception as e:
        print(f"Error processing recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Error processing recommendations: {str(e)}"
        }


@app.get("/")
def home():
    return {
        "message": "Freelancer Recommendation API",
        "info": "Training: Supabase data | Predictions: Live Supabase data",
        "skill_priority": "70% (HIGHEST)",
        "min_match_required": f"{MIN_SKILL_MATCH*100:.0f}%",
        "endpoint": "/recommend",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/retrain")
def retrain_model():
    """
    Retrain the model on current Supabase data
    Call this endpoint when you add new freelancers
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        import os
        
        print("🔄 Retraining model on latest Supabase data...")
        
        # Connect to Supabase
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Fetch all freelancers
        response = supabase.table("freelancers").select("skills").execute()
        
        if not response.data:
            return {
                "success": False,
                "message": "No data found in Supabase"
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(response.data)
        
        # Process skills
        def process_skills(skills):
            if skills is None or skills == '':
                return ''
            if isinstance(skills, list):
                return ' '.join([str(s).lower() for s in skills])
            return str(skills).lower().replace(';', ' ').replace(',', ' ')
        
        df['skills_clean'] = df['skills'].apply(process_skills)
        df = df[df['skills_clean'].str.strip() != '']
        
        # Train new vectorizer
        vectorizer = TfidfVectorizer(lowercase=True, max_features=500)
        vectorizer.fit(df['skills_clean'])
        
        # Save model
        os.makedirs('models', exist_ok=True)
        new_model_data = {
            'vectorizer': vectorizer,
            'weights': WEIGHTS
        }
        
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(new_model_data, f)
        
        # Reload model in memory
        global model_data
        model_data = new_model_data
        
        return {
            "success": True,
            "message": "Model retrained successfully",
            "freelancers_count": len(df),
            "vocabulary_size": len(vectorizer.vocabulary_)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
