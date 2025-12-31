# Freelancer Recommendation System

A simple machine learning system that recommends freelancers based on skills, rating, and experience.

## Features

- **TF-IDF + Cosine Similarity** for skill matching
- **Weighted scoring** (Skills 50%, Rating 30%, Experience 20%)
- **Real-time data** from Supabase
- **FastAPI** backend for easy integration

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Supabase

Create `.env` file (use `env.example` as template):

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_TABLE=freelancers
PORT=8000
```

### 3. Database Setup

Your Supabase needs two tables:

**freelancers table:**
- `id` (uuid)
- `username` (text)
- `skills` (text[] array)
- `experience` (integer)

**freelancer_reviews table:**
- `freelancer` (uuid, foreign key to freelancers.id)
- `stars` (float)

**Enable RLS policies for anonymous read access:**

```sql
CREATE POLICY "Allow anonymous read freelancers"
ON freelancers FOR SELECT TO anon USING (true);

CREATE POLICY "Allow anonymous read reviews"
ON freelancer_reviews FOR SELECT TO anon USING (true);
```

### 4. Train Model

```bash
python train.py
```

This creates `models/model.pkl` from `final_dataset.csv`.

### 5. Start Server

```bash
python main.py
```

Server runs on `http://localhost:8000`

## API Usage

### Request

```bash
POST /recommend
Content-Type: application/json

{
  "skills": ["Python", "Django", "React"],
  "top_n": 5
}
```

### Response

```json
{
  "success": true,
  "total": 5,
  "recommendations": [
    {
      "id": "uuid",
      "name": "John Doe",
      "score": 0.95,
      "match": 92.5,
      "rating": 5.0,
      "experience": 10,
      "completed_projects": 25,
      "skills": "Python, Django, React, Node.js"
    }
  ]
}
```

## Integration

### Mobile App (React Native)

```javascript
const response = await fetch('http://YOUR_SERVER/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    skills: ["Python", "Django"],
    top_n: 5
  })
});
const data = await response.json();
```

### Web App (JavaScript)

```javascript
const response = await axios.post('http://YOUR_SERVER/recommend', {
  skills: ["Python", "Django"],
  top_n: 5
});
console.log(response.data.recommendations);
```

## Deployment (Render.com)

1. Push code to GitHub
2. Create new Web Service on Render.com
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables (SUPABASE_URL, SUPABASE_KEY, SUPABASE_TABLE)

## Files

- `train.py` - Train TF-IDF model on CSV dataset
- `main.py` - FastAPI server that fetches live Supabase data
- `config.py` - Configuration and weights
- `final_dataset.csv` - Training dataset
- `models/model.pkl` - Trained TF-IDF vectorizer

## How It Works

1. **Training (Offline):** TF-IDF learns vocabulary from CSV dataset
2. **Prediction (Real-time):**
   - Fetch freelancers from Supabase
   - JOIN with reviews to calculate average rating
   - Calculate skill similarity using trained TF-IDF
   - Score = (0.5 × skills) + (0.3 × rating) + (0.2 × experience)
   - Return top N freelancers

## License

MIT
