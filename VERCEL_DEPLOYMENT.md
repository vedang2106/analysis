# Quick Vercel Deployment Guide

## Yes, you can host the frontend on Vercel! 🎉

However, you'll need to host the backend separately (Railway, Render, or Fly.io).

## Quick Steps

### 1. Deploy Backend First (Choose One)

#### Option A: Railway (Easiest) ⭐ Recommended
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Python
5. Set start command: `python api.py` (or use `gunicorn -w 4 -b 0.0.0.0:$PORT api:app` for production)
6. Copy your Railway URL (e.g., `https://your-app.railway.app`)

#### Option B: Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect GitHub repo
4. Build: `pip install -r requirements.txt`
5. Start: `gunicorn api:app`
6. Copy your Render URL

### 2. Update Backend CORS

Before deploying, update `api.py` to include your Vercel URL:

```python
# In api.py, the CORS origins are now configurable via environment variable
# Set ALLOWED_ORIGINS=https://your-app.vercel.app in Railway/Render settings
```

Or manually edit the `allowed_origins` list in `api.py` to include your Vercel URL.

### 3. Deploy Frontend to Vercel

1. **Go to [vercel.com](https://vercel.com)** and sign up with GitHub

2. **Import Project**
   - Click "Add New Project"
   - Select your GitHub repository
   - **Important**: Set "Root Directory" to `frontend`

3. **Configure Build Settings**
   - Framework Preset: "Create React App" (auto-detected)
   - Build Command: `npm run build` (auto-set)
   - Output Directory: `build` (auto-set)

4. **Add Environment Variable**
   - Go to "Environment Variables"
   - Add:
     - **Name**: `REACT_APP_API_URL`
     - **Value**: `https://your-backend-url.railway.app/api` (use your actual backend URL)
   - Save

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app is live! 🚀

## After Deployment

1. **Test your backend**:
   ```
   https://your-backend.railway.app/api/health
   ```
   Should return: `{"status":"ok"}`

2. **Test your frontend**:
   - Visit your Vercel URL
   - Try uploading a file
   - Check browser console for any errors

## Troubleshooting

### CORS Errors
- Make sure your backend CORS includes your Vercel URL
- Check backend logs in Railway/Render dashboard

### Connection Errors
- Verify `REACT_APP_API_URL` in Vercel environment variables
- Ensure backend is running (check Railway/Render dashboard)
- Test backend health endpoint directly

### Build Failures
- Check Vercel build logs
- Ensure root directory is set to `frontend`
- Verify all dependencies are in `package.json`

## Cost

- **Vercel**: Free tier (perfect for frontend)
- **Railway**: Free tier (500 hours/month), then $5/month
- **Render**: Free tier (spins down after inactivity)

## Quick Checklist

- [ ] Backend deployed to Railway/Render
- [ ] Backend URL copied
- [ ] CORS updated in backend to include Vercel URL
- [ ] Frontend deployed to Vercel
- [ ] Environment variable `REACT_APP_API_URL` set in Vercel
- [ ] Both services tested and working

## Need Help?

- Check `DEPLOYMENT.md` for detailed instructions
- Railway docs: https://docs.railway.app
- Vercel docs: https://vercel.com/docs
- Render docs: https://render.com/docs

