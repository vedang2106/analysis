# Troubleshoot 404 Error - Step by Step

## You're Still Getting 404? Let's Fix It!

### Step 1: Verify Vercel Project Settings

Go to Vercel Dashboard → Your Project → Settings → General:

**Check These Settings:**

1. **Root Directory**: Must be `./` (empty or project root)
   - ❌ NOT `frontend`
   - ✅ Should be `./` or empty

2. **Framework Preset**: Should be "Create React App"

3. **Build & Development Settings**:
   - If you have overrides enabled, check:
     - Build Command: `cd frontend && npm run build`
     - Output Directory: `frontend/build`
     - Install Command: `cd frontend && npm install`

### Step 2: Check Build Logs

1. Go to **Deployments** tab
2. Click on the **latest deployment**
3. Click **Build Logs**
4. Look for:
   - ✅ "Compiled successfully"
   - ✅ "The build folder is ready to be deployed"
   - ❌ Any red error messages

**If build failed:**
- Share the error message
- Check that `frontend/package.json` has `build` script

### Step 3: Check Function Logs

1. In the deployment page, click **Functions** tab
2. Check if `api/index.py` is listed
3. If there are errors, click on it to see logs

### Step 4: Verify Files Are Committed

Make sure these files are in your GitHub repository:

- ✅ `vercel.json` (in root)
- ✅ `api/index.py` (in api/ folder)
- ✅ `frontend/package.json` (in frontend/ folder)
- ✅ `requirements.txt` (in root, includes `mangum`)

### Step 5: Test API Directly

Try visiting:
- `https://analysis-lime.vercel.app/api/health`

**Expected**: `{"status":"ok"}`

**If this works but frontend doesn't:**
- The API is working, issue is with frontend routing

**If this also gives 404:**
- The API function isn't deploying correctly

### Step 6: Clear and Redeploy

1. Go to **Settings** → **General**
2. **Clear all Build & Development Settings** (disable overrides)
3. Let `vercel.json` handle everything
4. Go to **Deployments**
5. Click **"..."** → **Redeploy**

### Step 7: Alternative - Use Vercel CLI

If dashboard isn't working, try CLI:

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy (this will show detailed errors)
vercel --prod
```

## Common Issues & Solutions

### Issue 1: Build Succeeds But 404
**Cause**: Routes not matching correctly

**Fix**: 
- Check `vercel.json` routes
- Ensure `"handle": "filesystem"` is present (or routes are in correct order)

### Issue 2: Build Fails
**Cause**: Missing dependencies or wrong Node version

**Fix**:
- Check build logs for specific error
- Ensure `frontend/package.json` has all dependencies
- Verify Node.js version (should be 18+)

### Issue 3: API Works, Frontend Doesn't
**Cause**: Static files not being served

**Fix**:
- Check Output Directory is `frontend/build`
- Verify `frontend/build/index.html` exists after build
- Check routes in `vercel.json`

### Issue 4: Both API and Frontend 404
**Cause**: Root Directory is wrong or vercel.json not found

**Fix**:
- Verify Root Directory is `./` (not `frontend`)
- Check that `vercel.json` is in root directory
- Ensure it's committed to GitHub

## Quick Diagnostic Checklist

Run through this checklist:

- [ ] Root Directory is `./` (not `frontend`)
- [ ] `vercel.json` exists in root directory
- [ ] `api/index.py` exists
- [ ] `frontend/package.json` has `build` script
- [ ] `requirements.txt` includes `mangum`
- [ ] Build logs show "Compiled successfully"
- [ ] Latest deployment is from after you made changes
- [ ] Tried visiting `/api/health` endpoint

## Still Not Working?

**Share these details:**

1. **Build Logs**: Copy the last 20-30 lines
2. **Function Logs**: Any errors from `api/index.py`
3. **Vercel Settings Screenshot**: Settings → General page
4. **What happens when you visit**:
   - `https://analysis-lime.vercel.app/`
   - `https://analysis-lime.vercel.app/api/health`

This will help identify the exact issue!

