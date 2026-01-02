# Fix Railway DNS Error (DNS_PROBE_FINISHED_NXDOMAIN)

## Problem
The Railway domain `analysis-production-2767.up.railway.app` is not resolving (DNS error).

## Solution Steps

### Step 1: Check Railway Deployment Status

1. **Go to Railway Dashboard**:
   - Open your "analysis" service
   - Check the **"Deployments"** tab
   - Look for the latest deployment status

2. **Check if Deployment is Successful**:
   - Should show "COMPLETED" (green)
   - If it shows "FAILED" or "BUILDING", wait for it to complete
   - If failed, check the logs

### Step 2: Check Railway Logs

1. **Go to "Logs" tab** in Railway:
   - Look for any errors
   - Check if the Flask app started successfully
   - Look for: "Starting Flask Backend API Server..."
   - Check what port it's listening on

2. **Common Issues in Logs**:
   - Import errors (missing dependencies)
   - Port binding errors
   - Application crashes

### Step 3: Verify Service is Running

1. **Check Service Status**:
   - In Railway dashboard, look for service status indicator
   - Should show "Running" or "Active"
   - If it shows "Stopped" or "Crashed", there's an issue

2. **Check Start Command**:
   - Go to **"Settings"** tab
   - Check **"Start Command"**
   - Should be: `python api.py` or `gunicorn -w 4 -b 0.0.0.0:$PORT api:app`
   - If empty or wrong, set it correctly

### Step 4: Verify Port Configuration

1. **Check Environment Variables**:
   - Go to **"Variables"** tab
   - Look for `PORT` variable
   - Railway sets this automatically (usually a random port like 8080, 5000, etc.)

2. **Check Public Networking**:
   - Go to **"Settings"** → **"Public Networking"**
   - Make sure a domain is generated
   - The port should match what your app is listening on
   - If using `python api.py`, it uses `$PORT` from environment
   - If using gunicorn, it also uses `$PORT`

3. **Port Mismatch Fix**:
   - In "Public Networking", the port field should match Railway's `PORT` variable
   - OR use the port your app is actually listening on (check logs)

### Step 5: Restart/Redeploy Service

1. **Manual Redeploy**:
   - Go to **"Deployments"** tab
   - Click **"..."** (three dots) on latest deployment
   - Click **"Redeploy"**

2. **Or Trigger New Deployment**:
   - Make a small change to your code (add a comment)
   - Push to GitHub
   - Railway will auto-deploy

### Step 6: Use Gunicorn (Recommended for Production)

Your `Procfile` uses gunicorn, but Railway might be using `python api.py`. 

**Update Railway Start Command**:
1. Go to **"Settings"** tab
2. Find **"Start Command"** field
3. Set it to:
   ```
   gunicorn -w 4 -b 0.0.0.0:$PORT api:app
   ```
4. Save and redeploy

**OR** ensure gunicorn is installed:
- Check `requirements.txt` has `gunicorn>=21.2.0`
- Railway should install it automatically

## Quick Checklist

- [ ] Deployment status is "COMPLETED" (not failed)
- [ ] Service status is "Running"
- [ ] Logs show Flask/gunicorn started successfully
- [ ] Start command is set correctly
- [ ] Port in "Public Networking" matches Railway's PORT variable
- [ ] Domain is generated in "Public Networking"
- [ ] No errors in logs

## Most Common Issues

### Issue 1: Service Not Running
**Fix**: Check logs, fix errors, redeploy

### Issue 2: Wrong Port
**Fix**: 
- Check Railway's `PORT` variable
- Use that port in "Public Networking"
- Or use gunicorn which automatically uses `$PORT`

### Issue 3: Start Command Missing/Wrong
**Fix**: Set start command to `gunicorn -w 4 -b 0.0.0.0:$PORT api:app`

### Issue 4: Domain Not Generated
**Fix**: 
- Go to "Settings" → "Public Networking"
- Enter the port (check Variables tab for PORT value)
- Click "Generate Domain"

## After Fixing

1. **Wait 1-2 minutes** for DNS to propagate
2. **Test the URL**: `https://analysis-production-2767.up.railway.app/api/health`
3. Should return: `{"status":"ok"}`
4. If still not working, check Railway logs for errors



