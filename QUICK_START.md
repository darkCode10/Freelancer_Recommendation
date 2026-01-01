# ⚡ Quick Start - Railway Deployment

## 📦 What You Have Now

Clean, simple project with:
- ✅ Main API (`main.py`) - `/recommend` and `/retrain` endpoints
- ✅ Training script (`train.py`) - Trains on Supabase data
- ✅ Auto-retrain script (`auto_retrain.py`) - For cron jobs
- ✅ Skills are 70% priority, filters zero matches

---

## 🚀 Deploy to Railway (2 Steps)

### **Step 1: Main API Service**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push
   ```

2. **In Railway Dashboard:**
   - New Project → Deploy from GitHub
   - Select your repo
   
3. **Add Variables:**
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_TABLE=freelancers
   PORT=8000
   ```

4. **Set Start Command:**
   ```
   python train.py && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

5. **Deploy** → Wait 2-3 mins → Get your URL

---

### **Step 2: Cron Job (Auto-Retrain)**

1. **In Railway:** Click "+ New" → "Cron Job"

2. **Configure:**
   - Schedule: `0 2 * * *` (daily at 2 AM)
   - Command: `python auto_retrain.py`

3. **Add Same Variables:**
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_TABLE`

4. **Deploy** → Done!

---

## 📱 Use in Your App

```javascript
// Get recommendations
const response = await fetch('https://your-app.railway.app/recommend', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    skills: ['Medicine', 'Surgery'],
    top_n: 5
  })
});

const data = await response.json();
// data.recommendations = [{ name, match, rating, experience, skills }, ...]

// Manual retrain after adding freelancers
await fetch('https://your-app.railway.app/retrain', { 
  method: 'POST' 
});
```

---

## 🔄 How It Works

**Daily (Automatic):**
```
2 AM UTC → Cron Job → Retrains model → Updates with new freelancers
```

**Manual (When Needed):**
```
Your App → POST /retrain → Immediate model update
```

**Recommendations:**
```
User searches → API fetches Supabase data → Filters matches → Returns top results
```

---

## ✅ That's It!

- Cron job handles daily updates automatically
- `/retrain` endpoint for immediate updates
- Model always knows latest freelancers
- Works for any field (medicine, tech, design, etc.)

**Full details:** See `RAILWAY_SETUP.md`

