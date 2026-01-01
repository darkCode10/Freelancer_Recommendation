# 🎯 Freelancer Recommendation System

**Open-Source Freelancer Recommender for ANY Field** (Medicine, Design, Programming, Writing, etc.)

## ✨ Key Features

- ✅ **Trained on YOUR Supabase data** - Learns ALL skills in your database
- ✅ **Smart skill matching** - Uses TF-IDF + Cosine Similarity
- ✅ **Zero-match filtering** - Only shows relevant freelancers
- ✅ **Skills prioritized** - 70% weight on skill match
- ✅ **Live data** - Fetches current freelancers from Supabase
- ✅ **Multi-field support** - Works for any industry

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create `.env` file:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_TABLE=freelancers
PORT=8000
```

### 3. Train Model on Supabase Data

```bash
python train.py
```

This will:
- Fetch ALL freelancers from Supabase
- Learn their skills (medicine, design, programming, etc.)
- Save model to `models/model.pkl`

### 4. Start API Server

```bash
python main.py
```

Server runs at: `http://localhost:8000`

## 📊 How It Works

### Training (One-Time)
1. Connects to Supabase
2. Fetches all freelancer skills
3. Trains TF-IDF vectorizer on real skills
4. Saves model

### Prediction (Real-Time)
1. User sends skills (e.g., "Medicine", "Nursing")
2. Fetches live freelancers from Supabase
3. Joins with `freelancer_reviews` for ratings
4. Calculates skill similarity
5. **Filters out <10% matches** (critical!)
6. Ranks by: Skills (70%) + Rating (20%) + Experience (10%)
7. Returns top matches

## 🔄 Auto-Update When New Freelancers Added

### 1. **API Endpoint** - Trigger manually or from your app
```bash
curl -X POST https://your-app.railway.app/retrain
```

### 2. **Railway Cron Job** - Automatic daily retraining
See **Railway Setup** section below for instructions.

---

## 🔧 API Usage

### Request

```bash
POST http://localhost:8000/recommend
Content-Type: application/json

{
  "skills": ["Medicine", "Surgery", "Pediatrics"],
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
      "id": "123",
      "name": "Dr. Smith",
      "match": 85.5,
      "rating": 4.8,
      "experience": 10,
      "completed_projects": 45,
      "skills": "Medicine, Surgery, Pediatrics, Emergency Care"
    }
  ]
}
```

### No Match Response

```json
{
  "success": false,
  "total": 0,
  "recommendations": [],
  "message": "No freelancers found with matching skills for: XYZ"
}
```

## ⚙️ Configuration

Edit `config.py`:

```python
# Skill matching priority
WEIGHTS = {
    "skills": 0.7,      # 70% - HIGHEST priority
    "rating": 0.2,      # 20%
    "experience": 0.1   # 10%
}

# Minimum match threshold (don't show if < 10%)
MIN_SKILL_MATCH = 0.1
```

## 🏗️ Supabase Schema

### `freelancers` table:
- `id` (uuid)
- `username` (text)
- `skills` (text[] array) - e.g., `['Java', 'Python']`
- `experience` (int)

### `freelancer_reviews` table:
- `freelancer` (uuid, FK to freelancers.id)
- `stars` (float)

### RLS Policies:
Must allow anonymous read access:

```sql
CREATE POLICY "Allow anonymous read freelancers"
ON freelancers FOR SELECT TO anon USING (true);

CREATE POLICY "Allow anonymous read reviews"
ON freelancer_reviews FOR SELECT TO anon USING (true);
```

## 🚂 Railway Setup (Complete Guide)

### **Step 1: Deploy Main API**

1. **Connect your GitHub repo to Railway**
   - Go to Railway.app
   - New Project → Deploy from GitHub
   - Select your repository

2. **Set Environment Variables**
   
   Go to your service → Variables tab, add:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-anon-key-here
   SUPABASE_TABLE=freelancers
   PORT=8000
   ```

3. **Set Start Command**
   
   Settings → Deploy → Start Command:
   ```
   python train.py && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   
   This trains the model on first deploy, then starts the API.

4. **Deploy**
   
   Railway will auto-deploy. Wait for it to finish.

5. **Test Your API**
   ```bash
   curl https://your-app.railway.app/health
   ```

---

### **Step 2: Add Cron Job for Auto-Retrain**

1. **In Railway Dashboard**
   - Click your project
   - Click "+ New" → "Cron Job"

2. **Configure Cron Job**
   
   **Name:** `Model Auto-Retrain`
   
   **Schedule:** `0 2 * * *` (daily at 2 AM UTC)
   
   **Command:** `python auto_retrain.py`

3. **Add Same Environment Variables**
   
   Copy these from your main service:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_TABLE`

4. **Deploy Cron Job**
   
   Railway will run it automatically on schedule.

---

### **Step 3: Manual Retrain (Optional)**

If you add freelancers and want immediate update:

```bash
# From your app or terminal
curl -X POST https://your-app.railway.app/retrain
```

Or add a button in your admin panel:
```javascript
await fetch('https://your-app.railway.app/retrain', { 
  method: 'POST' 
});
```

## 📱 Use in Mobile/Web App

```javascript
const response = await fetch('https://your-app.up.railway.app/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    skills: ['Medicine', 'Surgery'],
    top_n: 5
  })
});

const data = await response.json();
if (data.success) {
  // Show recommendations
  data.recommendations.forEach(freelancer => {
    console.log(`${freelancer.name} - ${freelancer.match}% match`);
  });
} else {
  console.log(data.message); // "No matching freelancers"
}
```

## 🎯 Key Improvements

### Before ❌
- Trained on old CSV data
- Showed freelancers with 0% skill match
- Experience/rating weighted too high
- Only worked for tech skills

### After ✅
- Trains on live Supabase data
- Filters out non-matching freelancers
- Skills are 70% of the score
- Works for ANY field (medicine, design, etc.)

## 📁 Project Structure

```
Freelancer_Recommendation/
├── train.py           # Train model on Supabase data
├── auto_retrain.py    # Auto-retrain script (for cron)
├── main.py            # FastAPI app with /recommend and /retrain
├── config.py          # Settings & weights
├── requirements.txt   # Dependencies
├── .env              # Credentials (not in git!)
├── .gitignore        # Git ignore rules
├── README.md         # This file
└── models/
    └── model.pkl     # Trained model (created by train.py)
```

## 🔍 Troubleshooting

**"No matching freelancers"**
- Model learned from Supabase skills
- If user searches for skills not in DB, no match
- Solution: Add diverse skills to Supabase

**"Invalid URL"**
- Check `.env` file exists
- Verify `SUPABASE_URL` is correct
- No quotes or spaces in `.env`

**Model not updating**
- Re-run `python train.py` after adding new freelancers
- This updates the vocabulary

## 📝 License

MIT - Free for any use
