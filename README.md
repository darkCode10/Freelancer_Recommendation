# Freelancer Recommendation System

Simple recommendation system for finding freelancers based on skills.

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Train
python train.py

# 3. Run
python main.py
```

Server runs at: **http://localhost:8000**

## API Usage

### Endpoint: POST /recommend

**Request:**
```json
{
  "skills": ["python", "machine learning"],
  "top_n": 5
}
```

**Response:**
```json
{
  "success": true,
  "total": 5,
  "recommendations": [
    {
      "id": "FL250879",
      "name": "John Doe",
      "title": "Software Engineer",
      "score": 0.85,
      "match": 90.5,
      "rating": 4.8,
      "experience": 25,
      "skills": "Python; Machine Learning; ..."
    }
  ]
}
```

## Integration Examples

### JavaScript (Web/Mobile)
```javascript
const response = await fetch('http://localhost:8000/recommend', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    skills: ['python', 'machine learning'],
    top_n: 5
  })
});
const data = await response.json();
console.log(data.recommendations);
```

### React Native (Mobile)
```javascript
fetch('http://YOUR_SERVER:8000/recommend', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    skills: ['python', 'machine learning'],
    top_n: 5
  })
})
.then(res => res.json())
.then(data => {
  setFreelancers(data.recommendations);
});
```

### Python
```python
import requests

response = requests.post('http://localhost:8000/recommend', json={
    'skills': ['python', 'machine learning'],
    'top_n': 5
})
print(response.json())
```

### cURL
```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"skills": ["python", "machine learning"], "top_n": 5}'
```

## Files

- `train.py` - Train the model (run once)
- `main.py` - FastAPI server
- `config.py` - Settings
- `requirements.txt` - Dependencies

## Deployment

Replace `localhost:8000` with your server URL:
- `http://your-server.com:8000`
- `https://api.yourapp.com`

---

Simple and ready to use! 🚀
