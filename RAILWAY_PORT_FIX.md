# Fix Railway Port Configuration

## Current Issue
Railway shows port **8080** in the settings, but your Flask app might be using a different port.

## Quick Fix

### Option 1: Use Railway's PORT Variable (Recommended)

1. **In Railway Dashboard** (where you are now):
   - The port field shows "8080"
   - **Change it to**: `5000` (or leave as 8080 if Railway set it)
   - Actually, **better approach**: Check what PORT Railway is using

2. **Check Railway Environment Variables**:
   - Go to **"Variables"** tab in Railway
   - Look for `PORT` variable
   - Note the value (Railway sets this automatically)

3. **Use That Port**:
   - Go back to **"Settings"** → **"Public Networking"**
   - Enter the port number from the `PORT` variable
   - OR use `5000` (Flask default)

4. **Click "Generate Domain"**
   - This will create your public URL
   - Copy the URL (e.g., `https://analysis-production-xxxx.up.railway.app`)

### Option 2: Set Port Explicitly

1. **In Railway "Variables" tab**:
   - Add/check: `PORT=5000`
   - This ensures your app listens on port 5000

2. **In "Settings" → "Public Networking"**:
   - Enter port: `5000`
   - Click **"Generate Domain"**

## Most Likely Solution

Since Railway automatically sets the `PORT` environment variable, and your Flask app uses `os.environ.get('PORT', 5000)`, you should:

1. **Check Railway Variables tab** for the `PORT` value
2. **Use that same port** in the "Public Networking" port field
3. **Click "Generate Domain"**

If you're not sure, try **5000** first (Flask default), then click "Generate Domain".

## After Generating Domain

1. **Test the URL**: `https://your-railway-url.up.railway.app/api/health`
2. **Update Vercel**: Add environment variable `REACT_APP_API_URL=https://your-railway-url.up.railway.app/api`
3. **Update Railway CORS**: Add variable `ALLOWED_ORIGINS=https://graphgrover.vercel.app`



