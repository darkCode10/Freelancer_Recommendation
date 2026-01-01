# Simple Configuration File
import os

# Supabase credentials (from environment variables)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'your-supabase-url')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-supabase-key')
SUPABASE_TABLE = os.getenv('SUPABASE_TABLE', 'freelancers')

# Model settings
MODEL_PATH = "models/model.pkl"

# How important is each factor? (Skills is HIGHEST priority!)
WEIGHTS = {
    "skills": 0.75,      # 70% - Skills match (HIGHEST PRIORITY!)
    "rating": 0.15,      # 20% - Rating
    "experience": 0.10   # 10% - Experience
}

# Minimum skill match required (0-1, where 0.1 = 10%)
MIN_SKILL_MATCH = 0.1  # Must have at least 10% skill match to appear

# API settings
API_PORT = int(os.getenv('PORT', 8000))
