# Simple FastAPI App for Freelancer Recommendations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from config import MODEL_PATH, API_PORT

# Create app
app = FastAPI(title="Freelancer Recommendations")

# Allow CORS for mobile/web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Load model on startup
model_data = None

@app.on_event("startup")
def load_model():
    global model_data
    print("Loading model...")
    with open(MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)
    print("Model loaded!")


# Request format
class RecommendRequest(BaseModel):
    skills: List[str]
    top_n: int = 5


# Main endpoint for your app!
@app.post("/recommend")
def get_recommendations(request: RecommendRequest):
    """
    Get freelancer recommendations
    
    Example:
    POST /recommend
    {
        "skills": ["python", "machine learning"],
        "top_n": 5
    }
    """
    
    # Get data from model
    df = model_data['df']
    vectorizer = model_data['vectorizer']
    skill_matrix = model_data['skill_matrix']
    weights = model_data['weights']
    
    # Process user skills
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
            "id": row['freelancer_ID'],
            "name": row.get('name', 'N/A'),
            "title": row.get('Title', 'N/A'),
            "score": float(scores[idx]),
            "match": float(similarities[idx] * 100),
            "rating": float(row['rating_original']),
            "experience": int(row['experience_original']),
            "skills": row['Skills']
        })
    
    return {
        "success": True,
        "total": len(results),
        "recommendations": results
    }


@app.get("/")
def home():
    return {
        "message": "Freelancer Recommendation API",
        "endpoint": "/recommend",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
