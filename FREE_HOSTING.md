# Free Hosting Guide - Backend & Frontend

This guide covers **completely free** hosting options for both your React frontend and Flask backend.

## 🎯 Best Free Combinations

### Option 1: Vercel (Frontend) + Render (Backend) ⭐ **Most Recommended**
- **Frontend**: Vercel - Unlimited free hosting
- **Backend**: Render - Free tier (spins down after 15 min inactivity, wakes on request)
- **Total Cost**: $0/month

### Option 2: Netlify (Frontend) + Railway (Backend)
- **Frontend**: Netlify - Unlimited free hosting
- **Backend**: Railway - 500 free hours/month (enough for 24/7 if you're the only user)
- **Total Cost**: $0/month (if usage < 500 hours)

### Option 3: Vercel (Frontend) + Fly.io (Backend)
- **Frontend**: Vercel - Unlimited free hosting
- **Backend**: Fly.io - 3 shared VMs free
- **Total Cost**: $0/month

---

## 🚀 Option 1: Vercel + Render (Recommended)

### Frontend on Vercel (Free Forever)

1. **Sign up**: [vercel.com](https://vercel.com) (GitHub login)
2. **Deploy**:
   - Click "Add New Project"
   - Import your GitHub repo
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `build` (auto-detected)
3. **Environment Variable**:
   - Add: `REACT_APP_API_URL=https://your-app.onrender.com/api`
   - (You'll set this after deploying backend)
4. **Done!** Your frontend is live forever for free

### Backend on Render (Free Tier)

1. **Sign up**: [render.com](https://render.com) (GitHub login)

2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `data-analyst-backend` (or any name)
     - **Region**: Choose closest to you
     - **Branch**: `main` (or your default branch)
     - **Root Directory**: Leave empty (project root)
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn api:app`
     - **Plan**: **Free** (select this!)

3. **Environment Variables** (in Render dashboard):
   ```
   PORT=10000
   FLASK_ENV=production
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```
   (Update `ALLOWED_ORIGINS` after you get your Vercel URL)

4. **Deploy**: Click "Create Web Service"
   - First deploy takes 5-10 minutes
   - Render provides URL: `https://your-app.onrender.com`

5. **Important Notes**:
   - ⚠️ Free tier spins down after 15 minutes of inactivity
   - First request after spin-down takes ~30 seconds (cold start)
   - Subsequent requests are fast
   - Perfect for personal projects and demos

6. **Update Frontend**:
   - Go back to Vercel
   - Update `REACT_APP_API_URL` to your Render URL
   - Redeploy frontend

---

## 🚀 Option 2: Netlify + Railway

### Frontend on Netlify (Free Forever)

1. **Sign up**: [netlify.com](https://netlify.com) (GitHub login)

2. **Deploy**:
   - Click "Add new site" → "Import an existing project"
   - Connect GitHub repo
   - Settings:
     - **Base directory**: `frontend`
     - **Build command**: `npm run build`
     - **Publish directory**: `frontend/build`
   - Click "Deploy site"

3. **Environment Variable**:
   - Site settings → Environment variables
   - Add: `REACT_APP_API_URL=https://your-app.railway.app/api`

4. **Done!** Free forever

### Backend on Railway (500 Free Hours/Month)

1. **Sign up**: [railway.app](https://railway.app) (GitHub login)

2. **Deploy**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python

3. **Configure**:
   - **Start Command**: `python api.py` (or `gunicorn -w 4 -b 0.0.0.0:$PORT api:app`)
   - **Plan**: Free (Hobby plan)

4. **Environment Variables**:
   ```
   ALLOWED_ORIGINS=https://your-app.netlify.app
   ```

5. **Get URL**: Railway provides: `https://your-app.railway.app`

6. **Note**: 
   - 500 hours/month = ~20 days of 24/7 uptime
   - Perfect if you don't need 24/7 uptime
   - Or upgrade to $5/month for unlimited

---

## 🚀 Option 3: Vercel + Fly.io

### Frontend on Vercel
(Same as Option 1 above)

### Backend on Fly.io (3 Free VMs)

1. **Install Fly CLI**:
   ```powershell
   # Windows PowerShell
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Login**:
   ```powershell
   fly auth login
   ```

3. **Create App**:
   ```powershell
   cd "C:\Users\ASUS\Desktop\analysis"
   fly launch
   ```
   - Follow prompts
   - Choose region closest to you
   - Don't deploy yet (we need to configure first)

4. **Create `fly.toml`** (in project root):
   ```toml
   app = "your-app-name"
   primary_region = "iad"  # Change to your region

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

5. **Deploy**:
   ```powershell
   fly deploy
   ```

6. **Get URL**: `https://your-app-name.fly.dev`

7. **Set Environment Variables**:
   ```powershell
   fly secrets set ALLOWED_ORIGINS=https://your-app.vercel.app
   ```

---

## 📊 Free Tier Comparison

| Platform | Free Tier | Limitations | Best For |
|----------|-----------|-------------|----------|
| **Vercel** | Unlimited | 100GB bandwidth/month | Frontend hosting |
| **Netlify** | Unlimited | 100GB bandwidth/month | Frontend hosting |
| **Render** | Always free | Spins down after 15min | Backend (personal projects) |
| **Railway** | 500 hrs/month | ~20 days 24/7 | Backend (moderate use) |
| **Fly.io** | 3 shared VMs | 160GB outbound/month | Backend (always-on) |

---

## 🎯 Recommended Setup for Maximum Free Usage

### Best Combo: **Vercel + Render**

**Why?**
- ✅ Both completely free forever
- ✅ No time limits
- ✅ Easy setup
- ✅ Good performance
- ⚠️ Only downside: Render spins down (30s cold start)

**Setup Time**: ~15 minutes

---

## 🔧 Quick Setup Checklist

### Backend (Render)
- [ ] Sign up at render.com
- [ ] Create Web Service
- [ ] Set build: `pip install -r requirements.txt`
- [ ] Set start: `gunicorn api:app`
- [ ] Add environment variables
- [ ] Deploy and copy URL

### Frontend (Vercel)
- [ ] Sign up at vercel.com
- [ ] Import GitHub repo
- [ ] Set root directory: `frontend`
- [ ] Add env var: `REACT_APP_API_URL`
- [ ] Deploy

### Final Steps
- [ ] Update backend CORS with frontend URL
- [ ] Test both services
- [ ] Share your live app! 🎉

---

## 💡 Pro Tips

1. **Keep Render Alive** (Optional):
   - Use a free cron service like [cron-job.org](https://cron-job.org)
   - Ping your Render URL every 10 minutes
   - Keeps it from spinning down

2. **Monitor Usage**:
   - Railway: Check dashboard for hours used
   - Render: Check logs for activity
   - Fly.io: Check usage in dashboard

3. **Custom Domains** (Optional):
   - Vercel: Free custom domain support
   - Render: Free custom domain on paid plan only
   - Use subdomains for free (e.g., `api.yourdomain.com`)

---

## 🆘 Troubleshooting

### Render Spins Down Too Often
- Use cron-job.org to ping every 10 minutes
- Or upgrade to paid ($7/month) for always-on

### Railway Runs Out of Hours
- Monitor usage in dashboard
- Upgrade to $5/month for unlimited
- Or switch to Render (always free)

### Cold Start Too Slow (Render)
- First request takes 30s
- Subsequent requests are fast
- Consider Railway or Fly.io for faster cold starts

---

## 📝 Summary

**Easiest & Most Free**: Vercel + Render
- Frontend: Vercel (unlimited free)
- Backend: Render (always free, spins down)
- **Total: $0/month forever**

**Best Performance**: Vercel + Railway
- Frontend: Vercel (unlimited free)
- Backend: Railway (500 free hours/month)
- **Total: $0/month** (if < 500 hours)

**Always-On Backend**: Vercel + Fly.io
- Frontend: Vercel (unlimited free)
- Backend: Fly.io (3 free VMs)
- **Total: $0/month**

All options are completely free for personal projects and demos! 🎉

