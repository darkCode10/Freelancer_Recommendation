# ✅ Railway Deployment Checklist

## 📋 Pre-Deployment Checklist

- [x] Code cleaned and tested locally
- [x] Dependencies in `requirements.txt`
- [x] Environment variables in `.env` (not committed)
- [x] `.gitignore` configured correctly
- [x] Model trains on Supabase data
- [x] Zero-match filtering works
- [x] Skills prioritized at 70%
- [x] No emoji/unicode errors
- [x] `/retrain` endpoint working
- [x] Auto-retrain script ready for cron

---

## 🚀 Deployment Steps

### **Step 1: Push to GitHub**

```bash
git push origin main
```

### **Step 2: Railway - Main API Service**

1. **Go to Railway Dashboard**
   - https://railway.app

2. **Deploy from GitHub**
   - New Project → Deploy from GitHub repo
   - Select: `Freelancer_Recommendation`

3. **Add Environment Variables**
   
   Go to Variables tab, add:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-anon-key-here
   SUPABASE_TABLE=freelancers
   PORT=8000
   ```

4. **Set Start Command**
   
   Settings → Deploy → Start Command:
   ```
   python train.py && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   
   This will:
   - Train model on first deploy
   - Start the API server

5. **Deploy**
   - Railway auto-deploys
   - Wait 2-3 minutes
   - Get your URL: `https://your-app.up.railway.app`

6. **Test Deployment**
   ```bash
   curl https://your-app.up.railway.app/health
   ```

---

### **Step 3: Railway - Cron Job (Auto-Retrain)**

1. **Add Cron Service**
   - Click "+ New" → "Cron Job"

2. **Configure**
   - **Name:** Model Auto-Retrain
   - **Schedule:** `0 2 * * *` (daily at 2 AM UTC)
   - **Command:** `python auto_retrain.py`

3. **Add Environment Variables**
   
   Copy from main service:
   ```
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-anon-key-here
   SUPABASE_TABLE=freelancers
   ```

4. **Deploy Cron**
   - Railway will run it on schedule

---

## 🧪 Testing Your Deployment

### **Test 1: Health Check**
```bash
curl https://your-app.railway.app/health
```

**Expected:** `{"status":"ok"}`

### **Test 2: Get Recommendations**
```bash
curl -X POST https://your-app.railway.app/recommend \
  -H "Content-Type: application/json" \
  -d '{"skills": ["Python", "Machine Learning"], "top_n": 5}'
```

**Expected:** JSON with recommendations

### **Test 3: Manual Retrain**
```bash
curl -X POST https://your-app.railway.app/retrain
```

**Expected:** 
```json
{
  "success": true,
  "freelancers_count": 8,
  "vocabulary_size": 30
}
```

---

## 📱 Update Your App

Replace localhost with Railway URL:

```javascript
// Before
const API_URL = 'http://localhost:8000';

// After
const API_URL = 'https://your-app.up.railway.app';
```

---

## 🔍 Troubleshooting

### Issue: "Application failed to respond"
**Solution:**
- Check Railway logs
- Verify environment variables
- Ensure Supabase credentials are correct

### Issue: "No data found in Supabase"
**Solution:**
- Check Supabase RLS policies
- Run this in Supabase SQL Editor:
  ```sql
  CREATE POLICY "Allow anonymous read freelancers"
  ON freelancers FOR SELECT TO anon USING (true);
  
  CREATE POLICY "Allow anonymous read reviews"
  ON freelancer_reviews FOR SELECT TO anon USING (true);
  ```

### Issue: "Model file not found"
**Solution:**
- Make sure start command includes `python train.py &&`
- Check Railway deployment logs for training output

### Issue: Cron job not running
**Solution:**
- Check cron service logs
- Verify environment variables on cron service
- Wait for next scheduled run (2 AM UTC)

---

## ✅ Post-Deployment Checklist

- [ ] API health check passes
- [ ] Recommendations endpoint works
- [ ] Retrain endpoint works
- [ ] Cron job is scheduled
- [ ] Mobile/web app updated with Railway URL
- [ ] Test adding freelancer → retrain → search flow

---

## 📊 What You Have Now

### **Features:**
✅ Trains on live Supabase data  
✅ Filters zero-match freelancers  
✅ Skills prioritized at 70%  
✅ Works for ANY field (medicine, tech, design, etc.)  
✅ Auto-updates daily at 2 AM  
✅ Manual update via `/retrain` endpoint  
✅ Fast recommendations (1-5 seconds)  

### **Endpoints:**
- `GET /` - API info
- `GET /health` - Health check
- `POST /recommend` - Get recommendations
- `POST /retrain` - Update model

### **Maintenance:**
- Automatic: Cron job daily at 2 AM
- Manual: Call `/retrain` after adding freelancers
- No manual intervention needed!

---

## 🎉 You're Ready!

Run this command and you're live:

```bash
git push origin main
```

Railway will automatically deploy! 🚀

---

## 📚 Documentation

- **Quick Start:** `QUICK_START.md`
- **Full Setup:** `RAILWAY_SETUP.md`
- **App Integration:** `APP_INTEGRATION.md`
- **Main Docs:** `README.md`

---

## 🆘 Need Help?

Check Railway logs:
1. Go to Railway dashboard
2. Click your service
3. Click "Deployments"
4. Click latest deployment
5. View logs

Common log messages:
- `[SUCCESS] Training Complete!` ✅ Good
- `[OK] Found X freelancers` ✅ Good
- `[ERROR] No data found` ❌ Check Supabase RLS
- `Invalid URL` ❌ Check environment variables

