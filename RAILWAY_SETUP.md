# 🚂 Railway Setup Guide

Complete step-by-step guide to deploy your Freelancer Recommendation System on Railway.

---

## 📋 Prerequisites

- ✅ GitHub account with your code pushed
- ✅ Railway account (railway.app)
- ✅ Supabase project with data
- ✅ Environment variables ready

---

## 🚀 Part 1: Deploy Main API

### Step 1: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `Freelancer_Recommendation`
5. Click **"Deploy Now"**

### Step 2: Add Environment Variables

1. Click on your service
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add these one by one:

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_TABLE=freelancers
PORT=8000
```

⚠️ **Important:** Replace with YOUR actual Supabase credentials!

### Step 3: Configure Start Command

1. Click **"Settings"** tab
2. Scroll to **"Deploy"** section
3. Find **"Start Command"**
4. Enter:
   ```bash
   python train.py && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

This will:
- Train model on Supabase data first
- Then start the API server

### Step 4: Deploy

1. Railway will auto-deploy
2. Wait 2-3 minutes
3. You'll see a URL like: `https://your-app.up.railway.app`

### Step 5: Test API

```bash
# Health check
curl https://your-app.up.railway.app/health

# Test recommendation
curl -X POST https://your-app.up.railway.app/recommend \
  -H "Content-Type: application/json" \
  -d '{"skills": ["Python", "Django"], "top_n": 3}'
```

**Expected response:**
```json
{
  "success": true,
  "total": 3,
  "recommendations": [...]
}
```

✅ **Part 1 Complete!** Your API is live.

---

## ⏰ Part 2: Add Cron Job for Auto-Retrain

### Step 1: Create Cron Job Service

1. In Railway dashboard, click your project name (top left)
2. Click **"+ New"**
3. Select **"Cron Job"**

### Step 2: Configure Cron Job

You'll see a configuration form:

**Service Name:** `Model Auto-Retrain`

**Schedule:** 
```
0 2 * * *
```
(This means: Daily at 2:00 AM UTC)

**Command:**
```bash
python auto_retrain.py
```

### Step 3: Add Environment Variables

The cron job needs same variables as main app:

1. Click the cron job service
2. Go to **"Variables"** tab
3. Add these variables:

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_TABLE=freelancers
```

⚠️ Copy exact values from your main service!

### Step 4: Deploy Cron Job

1. Railway will automatically set it up
2. Check **"Deployments"** tab to verify

### Step 5: Test Cron Job (Optional)

Railway doesn't have a "run now" button, but you can:

**Option A: Trigger from API**
```bash
curl -X POST https://your-app.up.railway.app/retrain
```

**Option B: Check logs**
- Wait until next scheduled run (2 AM UTC)
- Check cron job logs to verify it ran

✅ **Part 2 Complete!** Auto-retrain is set up.

---

## 📅 Cron Schedule Options

Change the schedule based on your needs:

| Schedule | Meaning | Use Case |
|----------|---------|----------|
| `0 2 * * *` | Daily at 2 AM | Standard (recommended) |
| `0 */6 * * *` | Every 6 hours | High-traffic apps |
| `0 0 * * 0` | Weekly (Sunday midnight) | Low-traffic apps |
| `*/30 * * * *` | Every 30 minutes | Testing only |

---

## 🔄 Part 3: Manual Retrain (Bonus)

You can also trigger retrain manually or from your app.

### From Your Mobile/Web App

```javascript
// After adding new freelancer to Supabase
async function addFreelancer(data) {
  // 1. Add to Supabase
  await supabase.from('freelancers').insert(data);
  
  // 2. Update model
  await fetch('https://your-app.railway.app/retrain', {
    method: 'POST'
  });
  
  console.log('✅ Freelancer added and model updated');
}
```

### Admin Panel Button

```javascript
function AdminPanel() {
  const handleRetrain = async () => {
    const response = await fetch('https://your-app.railway.app/retrain', {
      method: 'POST'
    });
    
    const data = await response.json();
    
    if (data.success) {
      alert(`✅ Model updated! ${data.freelancers_count} freelancers`);
    }
  };
  
  return (
    <button onClick={handleRetrain}>
      🔄 Update Model
    </button>
  );
}
```

---

## 🎯 Final Setup Summary

Your Railway project now has:

1. ✅ **Main API Service**
   - URL: `https://your-app.railway.app`
   - Endpoints: `/recommend`, `/retrain`, `/health`
   - Auto-deploys on git push

2. ✅ **Cron Job Service**
   - Runs daily at 2 AM
   - Retrains model with latest Supabase data
   - Keeps model always updated

3. ✅ **Manual Trigger**
   - POST to `/retrain` endpoint
   - Use from app or admin panel
   - Immediate updates when needed

---

## 🔍 Troubleshooting

### "Application failed to respond"
- Check **Logs** tab in Railway
- Verify environment variables are set
- Make sure Supabase credentials are correct

### "No data found in Supabase"
- Check Supabase RLS policies
- Make sure anonymous read is enabled
- Test Supabase connection locally first

### "Model file not found"
- Start command should run `python train.py` first
- Check if start command is: `python train.py && uvicorn main:app --host 0.0.0.0 --port $PORT`

### Cron job not running
- Check cron service logs
- Verify environment variables are set on cron service
- Wait for next scheduled run (2 AM UTC)

### Retrain takes too long
- Normal for large datasets (100+ freelancers)
- Railway timeout is 10 minutes (should be enough)
- If timeout occurs, use cron job instead of `/retrain` endpoint

---

## 📝 Environment Variables Checklist

Make sure both services (API + Cron) have these:

- [ ] `SUPABASE_URL` - Your Supabase project URL
- [ ] `SUPABASE_KEY` - Anon/public key (not service role key!)
- [ ] `SUPABASE_TABLE` - Usually `freelancers`
- [ ] `PORT` - Only needed for main API (use `8000`)

---

## 🎉 You're Done!

Your system is now:
- ✅ Live on Railway
- ✅ Auto-retrains daily
- ✅ Can be manually updated via API
- ✅ Works with ANY freelancer field (medicine, design, tech, etc.)

**Test it:**
```bash
curl -X POST https://your-app.railway.app/recommend \
  -H "Content-Type: application/json" \
  -d '{"skills": ["Medicine", "Surgery"], "top_n": 5}'
```

Need help? Check main `README.md` or raise an issue!

