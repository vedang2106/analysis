# Fix: Railway Can't Find api.py

## Error
```
python: can't open file '/app/api.py': [Errno 2] No such file or directory
```

## Solution: Fix Railway Root Directory

### Step 1: Check Railway Root Directory

1. **In Railway Dashboard**:
   - Go to your "resplendent-acceptance" service
   - Click **"Settings"** tab
   - Scroll down to **"Root Directory"** or **"Source"** section
   - Check what's set there

2. **It Should Be**:
   - **Empty** (default) OR
   - **`.`** (current directory) OR
   - **`/`** (root)
   
   **NOT** `frontend/` or any subdirectory!

### Step 2: Set Root Directory (If Wrong)

1. In **"Settings"** tab
2. Find **"Root Directory"** field
3. **Clear it** (leave empty) OR set to `.`
4. Click **"Save"**
5. Railway will redeploy

### Step 3: Verify Start Command

1. In **"Settings"** tab
2. Check **"Start Command"** field
3. Should be one of:
   ```
   python api.py
   ```
   OR
   ```
   gunicorn -w 4 -b 0.0.0.0:$PORT api:app
   ```
4. Make sure it's **NOT** `python /app/api.py` or any path with `/app/`

### Step 4: Redeploy

1. Go to **"Deployments"** tab
2. Click **"..."** on latest deployment
3. Click **"Redeploy"**
4. OR make a small commit and push to trigger auto-deploy

### Step 5: Check Build Logs

1. Go to **"Build Logs"** tab
2. Check if files are being copied correctly
3. Should see `api.py` in the build output

## Alternative: Use Procfile

Railway should automatically detect your `Procfile`. If it exists, Railway will use:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT api:app
```

Make sure your `Procfile` is in the **root directory** (same level as `api.py`).

## Quick Checklist

- [ ] Root Directory is **empty** or `.` (NOT `frontend/`)
- [ ] Start Command is `python api.py` or `gunicorn -w 4 -b 0.0.0.0:$PORT api:app`
- [ ] `api.py` is in the root directory of your repo
- [ ] `Procfile` is in the root directory (if using)
- [ ] Redeployed after changes

## After Fixing

1. Wait for deployment to complete
2. Check **"Deploy Logs"** - should see Flask/gunicorn starting
3. Test: `https://resplendent-acceptance-production.up.railway.app/api/health`
4. Should return: `{"status":"ok"}`

