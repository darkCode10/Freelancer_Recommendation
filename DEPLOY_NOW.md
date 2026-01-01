# 🚀 READY TO DEPLOY!

## ✅ Pre-Deployment Checklist

### **Code Status:**
- ✅ Model trains from Supabase (not CSV)
- ✅ Filters zero-match freelancers (min 10%)
- ✅ Prioritizes skills (70% weight)
- ✅ Supports all skills (Medicine, ReactJS, etc.)
- ✅ Auto-retrain available (cron + API endpoint)
- ✅ Simple, clean code (no classes)
- ✅ All unnecessary files deleted

### **Files:**
- ✅ `main.py` - FastAPI server
- ✅ `train.py` - Model training (from Supabase)
- ✅ `config.py` - Configuration
- ✅ `auto_retrain.py` - Cron job script
- ✅ `requirements.txt` - Dependencies
- ✅ `.gitignore` - Protects .env

### **Configuration:**
- ✅ Environment variables in `config.py`
- ✅ `.env` is gitignored (won't be pushed)
- ✅ PORT reads from Railway's $PORT

---

## 🚂 Deploy to Railway (5 Minutes)

### **Step 1: Push to GitHub**

```bash
# If not already pushed
git add .
git commit -m "Ready for deployment - Supabase integration complete"
git push origin main
```

### **Step 2: Create Railway Project**

1. Go to: https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose: `Freelancer_Recommendation`
5. Click **"Deploy Now"**

### **Step 3: Add Environment Variables**

Click on your service → **Variables** tab → Add these:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_TABLE=freelancers
PORT=8000
```

⚠️ **Replace with YOUR actual Supabase credentials!**

### **Step 4: Set Start Command**

Click **Settings** → Find **"Start Command"** → Enter:

```bash
python train.py && uvicorn main:app --host 0.0.0.0 --port $PORT
```

This will:
1. Train model from Supabase on startup
2. Start the API server

### **Step 5: Get Your URL**

1. Go to **Settings** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. Copy your URL: `https://your-app.railway.app`

---

## 🧪 Test Your Deployment

### **Test 1: Health Check**

```bash
curl https://your-app.railway.app/health
```

Expected: `{"status": "ok", "message": "Recommendation API is running"}`

### **Test 2: Get Recommendations**

```bash
curl -X POST https://your-app.railway.app/recommend \
  -H "Content-Type: application/json" \
  -d '{"skills": ["Python", "Machine Learning"], "top_n": 5}'
```

### **Test 3: From Your App**

```javascript
const response = await fetch('https://your-app.railway.app/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    skills: ['Python', 'Machine Learning'],
    top_n: 5
  })
});

const data = await response.json();
console.log(data.recommendations);
```

---

## 🔄 Setup Auto-Retrain (Optional - 2 Minutes)

### **Option A: Cron Job (Recommended)**

1. In Railway, click **"New"** → **"Cron Job"**
2. Set schedule: `0 2 * * *` (daily 2 AM)
3. Command: `python auto_retrain.py`
4. Add same environment variables as main service

### **Option B: Manual Trigger**

Call `/retrain` from your app after adding freelancers:

```javascript
// After adding freelancer to Supabase
await fetch('https://your-app.railway.app/retrain', { 
  method: 'POST' 
});
```

---

## 📱 Integrate in Your App

### **Mobile/Web App Example:**

```javascript
// config.js
export const API_URL = 'https://your-app.railway.app';

// freelancer.service.js
export async function addFreelancer(data) {
  // 1. Add to Supabase
  const { error } = await supabase
    .from('freelancers')
    .insert(data);
  
  if (error) throw error;
  
  // 2. Update model (immediate)
  await fetch(`${API_URL}/retrain`, { method: 'POST' });
}

export async function searchFreelancers(skills, topN = 5) {
  const response = await fetch(`${API_URL}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ skills, top_n: topN })
  });
  
  return await response.json();
}
```

---

## 🎯 What Happens After Deployment?

1. **On First Deploy:**
   - Railway installs dependencies from `requirements.txt`
   - Runs `python train.py` (trains model from Supabase)
   - Starts FastAPI server
   - Your API is live! 🎉

2. **When You Add Freelancer:**
   - Option A: Call `/retrain` → Updates in 10-30 seconds
   - Option B: Wait for cron (2 AM) → Auto-updates daily

3. **When You Call `/recommend`:**
   - Fetches live data from Supabase
   - Uses trained model for skill matching
   - Returns top recommendations
   - Filters out <10% skill matches

---

## 🐛 Troubleshooting

### **Issue: "No freelancers found"**
**Fix:** Check Supabase has data with `experience` column

```sql
-- In Supabase SQL Editor
SELECT COUNT(*) FROM freelancers WHERE experience IS NOT NULL;
```

### **Issue: "Application failed to respond"**
**Fix:** Check Railway logs → Service → **"Deployments"** → View logs

### **Issue: "Model training failed"**
**Fix:** 
1. Verify environment variables are correct
2. Check Supabase table has data
3. Ensure `experience` column exists

### **Issue: Port conflicts locally**
**Fix:**
```bash
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

---

## 📊 Current System Overview

```
┌─────────────────┐
│  Your App       │
│  (Mobile/Web)   │
└────────┬────────┘
         │
         │ POST /recommend
         │ POST /retrain
         ▼
┌─────────────────────────────────┐
│  Railway (FastAPI Server)       │
│  ┌─────────────────────────┐   │
│  │ Trained TF-IDF Model    │   │
│  │ - 70% Skills            │   │
│  │ - 20% Rating            │   │
│  │ - 10% Experience        │   │
│  └─────────────────────────┘   │
└────────┬────────────────────────┘
         │
         │ Fetch Data
         ▼
┌─────────────────────┐
│  Supabase           │
│  ┌───────────────┐  │
│  │ freelancers   │  │
│  │ - id          │  │
│  │ - username    │  │
│  │ - skills []   │  │
│  │ - experience  │  │
│  └───────────────┘  │
│                     │
│  ┌────────────────────┐  │
│  │ freelancer_reviews │  │
│  │ - stars (rating)   │  │
│  │ - freelancer (FK)  │  │
│  └────────────────────┘  │
└─────────────────────┘

Auto-Update:
- Cron: Daily 2 AM
- API: /retrain anytime
```

---

## ✅ Final Checks Before Deploy

```bash
# 1. Test locally one more time
python train.py
python main.py

# In another terminal
python test_react.py

# 2. Commit and push
git status
git add .
git commit -m "Production ready"
git push

# 3. Deploy on Railway
# Follow steps above

# 4. Test deployed API
curl https://your-app.railway.app/health
```

---

## 🎉 You're Ready!

**Everything is configured and tested!**

Just follow the steps above and you'll have your API live in 5 minutes! 🚀

**Need help?** Check:
- `RAILWAY_SETUP.md` - Detailed Railway guide
- `APP_INTEGRATION.md` - App integration examples
- `README.md` - Project overview

