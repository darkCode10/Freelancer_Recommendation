# Simple Configuration File

DATA_PATH = "final_dataset.csv"
MODEL_PATH = "models/model.pkl"

# How important is each factor?
WEIGHTS = {
    "skills": 0.5,      # 50% - Skills match
    "rating": 0.3,      # 30% - Rating
    "experience": 0.2   # 20% - Experience
}

# API settings
API_PORT = 8000
