# Simple Configuration File
import os

# Supabase credentials (from environment variables)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'your-supabase-url')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-supabase-key')
SUPABASE_TABLE = os.getenv('SUPABASE_TABLE', 'freelancers')

# Model settings
MODEL_PATH = "models/model.pkl"

# How important is each factor?
WEIGHTS = {
    "skills": 0.5,      # 50% - Skills match
    "rating": 0.3,      # 30% - Rating
    "experience": 0.2   # 20% - Experience
}

# API settings
API_PORT = int(os.getenv('PORT', 8000))
