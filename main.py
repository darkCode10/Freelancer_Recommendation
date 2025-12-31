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

from config import MODEL_PATH, API_PORT, SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE, WEIGHTS

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
        
        # Calculate final score
        scores = (
            weights['skills'] * similarities +
            weights['rating'] * df['rating_norm'].values +
            weights['experience'] * df['experience_norm'].values
        )
        
        # Get top N
        top_indices = scores.argsort()[-request.top_n:][::-1]
        
        # Format results
        results = []
        for idx in top_indices:
            row = df.iloc[idx]
            results.append({
                "id": str(row['id']),
                "name": row['name'],
                "score": float(scores[idx]),
                "match": float(similarities[idx] * 100),
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
        "info": "Training: CSV dataset | Predictions: Live Supabase data",
        "endpoint": "/recommend",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
