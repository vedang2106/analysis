# 🚀 Quick Free Deployment (15 Minutes)

**Recommended: Vercel (Frontend) + Render (Backend)**
- ✅ Both 100% free forever
- ✅ No credit card required
- ✅ Easy setup

---

## Step 1: Deploy Backend to Render (5 min)

1. Go to [render.com](https://render.com) → Sign up with GitHub

2. Click **"New +"** → **"Web Service"**

3. Connect your GitHub repository

4. Fill in:
   ```
   Name: data-analyst-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn api:app
   Plan: Free ⭐
   ```

5. Click **"Create Web Service"**

6. Wait 5-10 minutes for first deploy

7. **Copy your URL**: `https://your-app.onrender.com` ⬅️ Save this!

---

## Step 2: Deploy Frontend to Vercel (5 min)

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub

2. Click **"Add New Project"**

3. Import your GitHub repository

4. Configure:
   ```
   Root Directory: frontend
   Framework Preset: Create React App (auto)
   Build Command: npm run build (auto)
   Output Directory: build (auto)
   ```

5. **Add Environment Variable**:
   - Click "Environment Variables"
   - Name: `REACT_APP_API_URL`
   - Value: `https://your-app.onrender.com/api` (use your Render URL from Step 1)

6. Click **"Deploy"**

7. **Copy your Vercel URL**: `https://your-app.vercel.app` ⬅️ Save this!

---

## Step 3: Update Backend CORS (2 min)

1. Go back to Render dashboard

2. Go to your service → **"Environment"** tab

3. Add new variable:
   ```
   Key: ALLOWED_ORIGINS
   Value: https://your-app.vercel.app
   ```
   (Use your actual Vercel URL from Step 2)

4. Click **"Save Changes"** → Render will redeploy automatically

---

## Step 4: Update Frontend (if needed) (1 min)

1. Go back to Vercel dashboard

2. If you need to update the API URL:
   - Go to **Settings** → **Environment Variables**
   - Update `REACT_APP_API_URL` if needed
   - Click **"Redeploy"**

---

## ✅ Done!

Your app is now live:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-app.onrender.com/api`

---

## 🧪 Test It

1. Visit your Vercel URL
2. Try uploading a CSV file
3. Check if it works!

---

## ⚠️ Important Notes

### Render Free Tier:
- Spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds (cold start)
- Subsequent requests are fast
- Perfect for demos and personal projects

### Keep Render Alive (Optional):
- Use [cron-job.org](https://cron-job.org) (free)
- Set up a job to ping your Render URL every 10 minutes
- Keeps your backend always warm

---

## 🆘 Troubleshooting

**Backend not responding?**
- Check Render logs in dashboard
- Wait 30 seconds for cold start
- Verify environment variables are set

**CORS errors?**
- Make sure `ALLOWED_ORIGINS` includes your Vercel URL
- Check backend logs in Render

**Frontend can't connect?**
- Verify `REACT_APP_API_URL` in Vercel environment variables
- Make sure it ends with `/api`
- Check browser console for errors

---

## 📚 More Options

See `FREE_HOSTING.md` for:
- Other free platform combinations
- Detailed comparisons
- Alternative setups

---

**Total Cost: $0/month** 💰
**Setup Time: ~15 minutes** ⏱️

Enjoy your free hosting! 🎉

