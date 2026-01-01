# Fix: Railway Service Not Running (DNS Error)

## Problem
Your Railway URL shows DNS error because the service isn't actually running. Logs show containers starting/stopping and Streamlit warnings.

## Solution: Set Correct Start Command

### Step 1: Check Current Start Command

1. **In Railway Dashboard**:
   - Go to your "resplendent-acceptance" service
   - Click **"Settings"** tab
   - Scroll down to find **"Start Command"** field
   - Check what's currently set (or if it's empty)

### Step 2: Set Correct Start Command

**Option A: Use Gunicorn (Recommended for Production)**

1. In **"Settings"** → **"Start Command"** field
2. Enter:
   ```
   gunicorn -w 4 -b 0.0.0.0:$PORT api:app
   ```
3. Click **"Save"**
4. Railway will automatically redeploy

**Option B: Use Python Directly**

1. In **"Settings"** → **"Start Command"** field
2. Enter:
   ```
   python api.py
   ```
3. Click **"Save"**
4. Railway will automatically redeploy

### Step 3: Check Deployment Status

1. Go to **"Deployments"** tab
2. Wait for the latest deployment to complete
3. Should show **"COMPLETED"** (green)
4. If it shows **"FAILED"**, check the logs

### Step 4: Check Logs for Errors

1. Go to **"Logs"** tab
2. Look for:
   - ✅ **Success**: "Starting Flask Backend API Server..." or "Booting worker"
   - ❌ **Errors**: Import errors, port binding errors, crashes
3. If you see errors, share them to fix

### Step 5: Verify Service is Running

1. After deployment completes, check **"Logs"** tab
2. You should see:
   - Flask/gunicorn starting messages
   - No Streamlit warnings
   - Server listening on a port
3. If still not working, check for error messages

## Why Streamlit Warnings?

The Streamlit warnings suggest Railway might be trying to run `app.py` (your old Streamlit app) instead of `api.py` (your Flask API).

**Fix**: Make sure the start command points to `api.py`, not `app.py`

## Quick Checklist

- [ ] Start Command is set: `gunicorn -w 4 -b 0.0.0.0:$PORT api:app` OR `python api.py`
- [ ] Deployment shows "COMPLETED" (not failed)
- [ ] Logs show Flask/gunicorn starting (not Streamlit)
- [ ] No errors in logs
- [ ] Service status is "Running"

## After Fixing

1. **Wait 1-2 minutes** for deployment to complete
2. **Test the URL**: `https://resplendent-acceptance-production.up.railway.app/api/health`
3. Should return: `{"status":"ok"}`
4. If still DNS error, wait a bit longer for DNS propagation

