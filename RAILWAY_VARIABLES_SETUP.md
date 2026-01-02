# Railway Variables Setup Guide

## Important: Frontend vs Backend Variables

### ❌ Don't Set This in Railway:
- `REACT_APP_API_URL` - This is a **frontend** variable for Vercel, not Railway backend!

### ✅ Set These in Railway (Backend):

#### 1. ALLOWED_ORIGINS (Required for CORS)
- **Name**: `ALLOWED_ORIGINS`
- **Value**: `https://graphgrover.vercel.app`
  - Replace with your actual Vercel frontend URL
  - If you have multiple origins, separate with commas: `https://graphgrover.vercel.app,https://your-other-domain.com`

#### 2. PORT (Usually Auto-Set)
- Railway automatically sets `PORT` - you don't need to add it manually
- Check the "7 variables added by Railway" section to see it

#### 3. FLASK_ENV (Optional)
- **Name**: `FLASK_ENV`
- **Value**: `production`
- This disables debug mode for production

## How to Add Variables in Railway

1. **Click "+ New Variable"** button (top right)
2. **Enter**:
   - **Name**: `ALLOWED_ORIGINS`
   - **Value**: `https://graphgrover.vercel.app` (your Vercel URL)
3. **Click "Add"**
4. Railway will automatically redeploy

## Where to Set REACT_APP_API_URL

**Set `REACT_APP_API_URL` in Vercel, NOT Railway!**

1. Go to [vercel.com](https://vercel.com)
2. Open your frontend project
3. Go to **Settings** → **Environment Variables**
4. Add:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://your-railway-backend-url.up.railway.app/api`
   - Use your Railway backend URL (not localhost!)

## Quick Checklist

### Railway (Backend) Variables:
- [ ] `ALLOWED_ORIGINS` = `https://graphgrover.vercel.app`
- [ ] `PORT` = (auto-set by Railway, don't add manually)
- [ ] `FLASK_ENV` = `production` (optional)

### Vercel (Frontend) Variables:
- [ ] `REACT_APP_API_URL` = `https://your-railway-backend-url.up.railway.app/api`

## Current Setup

You're looking at the **backend service** on Railway. You should:
1. **Ignore** the `REACT_APP_API_URL` suggestion (that's for frontend)
2. **Add** `ALLOWED_ORIGINS` with your Vercel URL
3. **Set** `REACT_APP_API_URL` in Vercel instead



