# 🚀 Complete Vercel Deployment Guide

## Overview

**Vercel is perfect for your React frontend!** However, you'll need to host the Flask backend separately because:
- Vercel is optimized for serverless functions (short-lived)
- Your Flask app needs to run continuously
- **Solution**: Deploy frontend to Vercel, backend to Railway/Render

---

## 📋 Step-by-Step Guide

### Part 1: Deploy Backend First (Choose One Platform)

#### Option A: Railway (Easiest) ⭐ Recommended

1. **Sign up at [railway.app](https://railway.app)**
   - Use GitHub to sign in

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `analysis` repository

3. **Configure Backend**
   - Railway auto-detects Python
   - **Root Directory**: Leave empty (project root)
   - **Start Command**: `python api.py`
     - OR for production: `gunicorn -w 4 -b 0.0.0.0:$PORT api:app`

4. **Get Your Backend URL**
   - Railway will generate a URL like: `https://your-app.railway.app`
   - **Copy this URL** - you'll need it for the frontend!

5. **Test Backend**
   - Visit: `https://your-app.railway.app/api/health`
   - Should see: `{"status":"ok"}`

#### Option B: Render (100% Free)

1. **Sign up at [render.com](https://render.com)**
   - Use GitHub to sign in

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Settings**
   ```
   Name: data-analyst-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn api:app
   Plan: Free ⭐
   ```

4. **Get Your Backend URL**
   - Render provides: `https://your-app.onrender.com`
   - **Copy this URL**

---

### Part 2: Deploy Frontend to Vercel

1. **Sign up at [vercel.com](https://vercel.com)**
   - Use GitHub to sign in

2. **Import Your Project**
   - Click "Add New Project"
   - Select your GitHub repository (`analysis`)
   - Click "Import"

3. **Configure Project Settings** ⚠️ IMPORTANT
   
   **Root Directory:**
   - Click "Edit" next to "Root Directory"
   - Set to: `frontend`
   - Click "Continue"

   **Framework Preset:**
   - Should auto-detect: "Create React App"
   - If not, select it manually

   **Build Settings** (usually auto-detected):
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Install Command: `npm install`

4. **Add Environment Variable** 🔑
   
   Before deploying, add this:
   - Click "Environment Variables"
   - Click "Add"
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://your-backend-url.railway.app/api`
     - Replace with your actual backend URL from Part 1
     - Make sure it ends with `/api`
   - Click "Save"

5. **Deploy!**
   - Click "Deploy"
   - Wait 2-5 minutes for build to complete
   - Your app will be live at: `https://your-app.vercel.app`

---

### Part 3: Update Backend CORS

After Vercel deployment, update your backend to allow requests from Vercel:

1. **Go to your backend platform** (Railway or Render)

2. **Add Environment Variable**
   - Railway: Go to "Variables" tab
   - Render: Go to "Environment" tab
   - Add new variable:
     - **Name**: `ALLOWED_ORIGINS`
     - **Value**: `https://your-app.vercel.app`
       - Use your actual Vercel URL from Part 2
     - Click "Save"

3. **Backend will automatically redeploy** with new CORS settings

---

## ✅ Verify Everything Works

1. **Test Frontend**
   - Visit your Vercel URL: `https://your-app.vercel.app`
   - Should see your React app

2. **Test Backend Connection**
   - Open browser console (F12)
   - Check for any CORS errors
   - Try uploading a file

3. **Test Backend Directly**
   - Visit: `https://your-backend-url.railway.app/api/health`
   - Should see: `{"status":"ok"}`

---

## 🔧 Troubleshooting

### Frontend Shows "Cannot connect to backend"

**Check:**
1. Is `REACT_APP_API_URL` set correctly in Vercel?
   - Go to Vercel → Settings → Environment Variables
   - Should be: `https://your-backend-url.railway.app/api`

2. Is backend running?
   - Check Railway/Render dashboard
   - Look at logs for errors

### CORS Errors in Browser Console

**Fix:**
1. Add your Vercel URL to backend `ALLOWED_ORIGINS`
2. Make sure backend has redeployed after adding the variable

### Build Fails on Vercel

**Check:**
1. Root Directory is set to `frontend` (not empty)
2. All dependencies are in `frontend/package.json`
3. Check Vercel build logs for specific errors

### Backend Not Starting

**Check:**
1. Start command is correct: `python api.py` or `gunicorn api:app`
2. All dependencies installed: `pip install -r requirements.txt`
3. Check backend logs in Railway/Render dashboard

---

## 📝 Quick Checklist

Before deploying:
- [ ] Backend deployed to Railway/Render
- [ ] Backend URL copied
- [ ] Backend health check works (`/api/health`)

During Vercel setup:
- [ ] Root Directory set to `frontend`
- [ ] `REACT_APP_API_URL` environment variable added
- [ ] Build completes successfully

After deployment:
- [ ] Frontend loads at Vercel URL
- [ ] `ALLOWED_ORIGINS` added to backend
- [ ] Backend redeployed with new CORS settings
- [ ] Can upload files and use the app

---

## 💰 Cost

- **Vercel**: Free forever (unlimited deployments)
- **Railway**: Free tier (500 hours/month), then $5/month
- **Render**: Free tier (spins down after 15 min inactivity)

**Total for light usage**: $0/month! 🎉

---

## 🆘 Need Help?

- Check build logs in Vercel dashboard
- Check backend logs in Railway/Render dashboard
- See `VERCEL_DEPLOYMENT.md` for more details
- See `QUICK_FREE_DEPLOY.md` for fastest setup

---

## 🎉 You're Done!

Your app is now live:
- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend-url.railway.app/api`

Share your Vercel URL with others! 🚀

