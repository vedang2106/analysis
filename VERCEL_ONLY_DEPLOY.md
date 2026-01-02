# 🚀 Deploy Frontend + Backend on Vercel Only

This guide shows you how to deploy **both** your React frontend and Flask backend on Vercel as a single project.

## ✅ What's Already Set Up

I've configured your project for Vercel deployment:
- ✅ `vercel.json` in root - handles both frontend and backend
- ✅ `api/index.py` - serverless function wrapper for Flask
- ✅ `mangum` added to requirements.txt - enables Flask on Vercel
- ✅ CORS configured to work with Vercel domains

## 📋 Deployment Steps

### Step 1: Push Code to GitHub

Make sure all changes are committed and pushed:

```bash
git add .
git commit -m "Configure for Vercel deployment"
git push
```

### Step 2: Deploy to Vercel

1. **Go to [vercel.com](https://vercel.com)**
   - Sign up or log in with GitHub

2. **Import Your Project**
   - Click "Add New Project"
   - Select your GitHub repository (`analysis`)
   - Click "Import"

3. **Configure Project Settings** ⚠️ IMPORTANT

   **Root Directory:**
   - Leave **EMPTY** (don't set to `frontend`)
   - Vercel needs to see the entire project structure

   **Framework Preset:**
   - Select "Other" (or leave as auto-detected)
   - Don't use "Create React App" preset

   **Build & Development Settings:**
   - **DO NOT** override any settings
   - Let `vercel.json` handle everything
   - If you see toggles for Build Command/Output Directory, **turn them OFF**

4. **Environment Variables (Optional)**
   - You can add `ALLOWED_ORIGINS` if needed
   - Usually not required - CORS is auto-configured

5. **Click "Deploy"**
   - Wait 3-5 minutes for build to complete
   - Vercel will build both frontend and deploy backend as serverless functions

### Step 3: Verify Deployment

1. **Check Build Logs**
   - Go to Deployments → Latest
   - Should see:
     - ✅ Frontend build completing
     - ✅ Python function deploying

2. **Test Your App**
   - Visit your Vercel URL: `https://your-app.vercel.app`
   - Should see your React app
   - Try uploading a file to test backend

3. **Test API Directly**
   - Visit: `https://your-app.vercel.app/api/health`
   - Should see: `{"status":"ok"}`

## 🎯 How It Works

- **Frontend**: Built from `frontend/` directory, served as static files
- **Backend**: Flask app wrapped in `api/index.py`, runs as Vercel serverless functions
- **Routes**: All `/api/*` requests go to Python functions, everything else serves React app

## 🔧 Project Structure

```
analysis/
├── vercel.json          # Root config (handles both frontend & backend)
├── api/
│   └── index.py        # Serverless function handler
├── api.py              # Your Flask app
├── frontend/
│   ├── package.json
│   ├── vercel.json     # (not used, root vercel.json takes precedence)
│   └── src/            # React app
└── requirements.txt    # Python dependencies (includes mangum)
```

## ⚠️ Important Notes

### Root Directory Setting
- **MUST be empty** (project root)
- **NOT** `frontend`
- Vercel needs to see both `api/` and `frontend/` directories

### Build Settings
- **Don't override** Build Command, Output Directory, or Install Command
- Let `vercel.json` handle everything
- If you see toggles in Settings, **turn them OFF**

### Environment Variables
- `VERCEL_URL` is automatically set by Vercel
- CORS automatically allows your Vercel domain
- No need to set `REACT_APP_API_URL` - frontend uses relative URLs

## 🆘 Troubleshooting

### Build Fails

**Check:**
1. Root Directory is empty (not `frontend`)
2. All files are committed to GitHub
3. `requirements.txt` includes `mangum`
4. `api/index.py` exists

**Common Errors:**
- "Cannot find module" → Check `requirements.txt` has all dependencies
- "api/index.py not found" → Make sure file exists and is committed
- Build timeout → Large dependencies might need optimization

### 404 on API Routes

**Check:**
1. Build logs show Python function deploying
2. Visit `/api/health` directly
3. Check Functions tab in Vercel dashboard

### CORS Errors

**Fix:**
- CORS is auto-configured for Vercel domains
- If you have custom domain, add it to `ALLOWED_ORIGINS` environment variable

### Frontend Shows but API Doesn't Work

**Check:**
1. Go to Vercel Dashboard → Deployments → Latest → Functions
2. Should see `api/index.py` listed
3. Check function logs for errors

## 📊 Vercel Limits (Free Tier)

- **Serverless Functions**: 100GB-hours/month
- **Bandwidth**: 100GB/month
- **Build Time**: 45 minutes/month
- **Function Execution**: 10 seconds (Hobby plan)

**Note**: For longer-running operations (like large file processing), you might hit the 10-second limit. Consider:
- Processing files in chunks
- Using background jobs
- Upgrading to Pro plan (60 seconds)

## ✅ Quick Checklist

Before deploying:
- [ ] Code pushed to GitHub
- [ ] `vercel.json` exists in root
- [ ] `api/index.py` exists
- [ ] `requirements.txt` includes `mangum`

During deployment:
- [ ] Root Directory is **empty**
- [ ] Build overrides are **disabled**
- [ ] Framework preset is "Other" or auto

After deployment:
- [ ] Frontend loads at Vercel URL
- [ ] `/api/health` returns `{"status":"ok"}`
- [ ] Can upload files and use app

## 🎉 You're Done!

Your app is now live on Vercel with both frontend and backend:
- **URL**: `https://your-app.vercel.app`
- **Frontend**: React app
- **Backend**: Flask API as serverless functions

Everything is on one platform! 🚀

