# Deployment Guide

This guide explains how to deploy the Data Analyst Automation Tool to production.

## 🆓 Free Hosting Options

**Looking for 100% free hosting?** See:
- **[QUICK_FREE_DEPLOY.md](QUICK_FREE_DEPLOY.md)** - Fastest free setup (15 min)
- **[FREE_HOSTING.md](FREE_HOSTING.md)** - Complete free hosting guide

**Recommended Free Combo**: Vercel (Frontend) + Render (Backend) = $0/month forever

## Architecture Overview

- **Frontend**: React.js app → Deploy to **Vercel** (recommended) or Netlify
- **Backend**: Flask API → Deploy to **Railway**, **Render**, or **Fly.io**

## Option 1: Vercel (Frontend) + Railway (Backend) - Recommended

### Step 1: Deploy Backend to Railway

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure Backend**
   - Railway will auto-detect Python
   - Set the root directory to the project root (not `frontend/`)
   - Add environment variables if needed

4. **Set Start Command**
   - In Railway settings, set the start command:
     ```
     python api.py
     ```
   - Or use gunicorn for production:
     ```
     pip install gunicorn && gunicorn -w 4 -b 0.0.0.0:$PORT api:app
     ```

5. **Get Backend URL**
   - Railway will provide a URL like: `https://your-app.railway.app`
   - Copy this URL (you'll need it for the frontend)

### Step 2: Deploy Frontend to Vercel

1. **Create Vercel Account**
   - Go to [vercel.com](https://vercel.com)
   - Sign up with GitHub

2. **Import Project**
   - Click "Add New Project"
   - Import your GitHub repository
   - Set the root directory to `frontend/`

3. **Configure Environment Variables**
   - In Vercel project settings, go to "Environment Variables"
   - Add:
     ```
     REACT_APP_API_URL=https://your-app.railway.app/api
     ```
   - Replace `your-app.railway.app` with your actual Railway backend URL

4. **Deploy**
   - Vercel will automatically build and deploy
   - Your app will be live at `https://your-app.vercel.app`

## Option 2: Vercel (Frontend) + Render (Backend)

### Deploy Backend to Render

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `data-analyst-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn api:app`
     - **Plan**: Free tier available

3. **Get Backend URL**
   - Render provides: `https://your-app.onrender.com`
   - Update frontend environment variable with this URL

### Deploy Frontend to Vercel
   - Follow the same steps as Option 1, Step 2
   - Use the Render backend URL in environment variables

## Option 3: Vercel (Frontend) + Fly.io (Backend)

### Deploy Backend to Fly.io

1. **Install Fly CLI**
   ```powershell
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login and Create App**
   ```powershell
   fly auth login
   fly launch
   ```

3. **Create `fly.toml`** (in project root):
   ```toml
   app = "your-app-name"
   primary_region = "iad"

   [build]

   [http_service]
     internal_port = 5000
     force_https = true
     auto_stop_machines = true
     auto_start_machines = true
     min_machines_running = 0
     processes = ["app"]

   [[services]]
     protocol = "tcp"
     internal_port = 5000
   ```

4. **Deploy**
   ```powershell
   fly deploy
   ```

## Important Notes

### Backend Configuration Changes Needed

1. **Update CORS in `api.py`**:
   ```python
   CORS(app, resources={
       r"/api/*": {
           "origins": [
               "http://localhost:3000",
               "https://your-frontend.vercel.app"  # Add your Vercel URL
           ],
           "methods": ["GET", "POST", "OPTIONS"],
           "allow_headers": ["Content-Type", "X-Session-ID"]
       }
   })
   ```

2. **Update Port Binding**:
   ```python
   # In api.py, change the last line:
   port = int(os.environ.get('PORT', 5000))
   app.run(debug=False, port=port, host='0.0.0.0')
   ```

3. **Use Production Server** (recommended):
   - Install gunicorn: `pip install gunicorn`
   - Use: `gunicorn -w 4 -b 0.0.0.0:$PORT api:app`

### Session Management

- Current implementation uses in-memory sessions
- For production, consider using:
  - Redis (for session storage)
  - Database-backed sessions
  - JWT tokens

### File Size Limits

- Vercel: 4.5MB limit for serverless functions (not applicable for static frontend)
- Railway: No hard limit, but consider 200MB max
- Render: 100MB request body limit
- Consider using cloud storage (S3, Cloudinary) for large files

## Environment Variables Summary

### Frontend (Vercel)
```
REACT_APP_API_URL=https://your-backend-url.com/api
```

### Backend (Railway/Render/Fly.io)
```
PORT=5000  # Usually auto-set by platform
FLASK_ENV=production
```

## Testing Deployment

1. **Test Backend Health**:
   ```
   curl https://your-backend-url.com/api/health
   ```

2. **Test Frontend**:
   - Visit your Vercel URL
   - Check browser console for errors
   - Try uploading a small test file

## Troubleshooting

### CORS Errors
- Ensure backend CORS includes your Vercel frontend URL
- Check that `Access-Control-Allow-Origin` header is present

### Connection Errors
- Verify backend URL in frontend environment variables
- Check backend is running and accessible
- Test backend health endpoint directly

### Build Failures
- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`
- Verify Node.js version compatibility

## Cost Estimates

- **Vercel (Frontend)**: Free tier available (generous limits)
- **Railway**: Free tier (500 hours/month), then $5/month
- **Render**: Free tier available (spins down after inactivity)
- **Fly.io**: Free tier available (3 shared VMs)

## Recommended Setup

For production, I recommend:
- **Frontend**: Vercel (free, fast, easy)
- **Backend**: Railway (reliable, good free tier, easy setup)

This combination provides the best balance of ease, cost, and performance.

