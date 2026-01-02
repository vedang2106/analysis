# Fixing 404 Error on Vercel

## Problem
Getting 404 error when accessing the deployed Vercel app.

## Solution Steps

### 1. Check Vercel Project Settings

Go to your Vercel project dashboard:
1. Open your project: `analysis-lime`
2. Go to **Settings** → **General**
3. Check **Root Directory**: Should be `./` (project root)
4. Check **Build & Development Settings**:
   - **Framework Preset**: Should be "Other" or "Create React App" (NOT Flask)
   - **Build Command**: Can be empty (vercel.json handles it) OR set to: `cd frontend && npm run build`
   - **Output Directory**: Can be empty OR set to: `frontend/build`
   - **Install Command**: Can be empty OR set to: `cd frontend && npm install`

### 2. Verify Build Logs

1. Go to **Deployments** tab
2. Click on the latest deployment
3. Check **Build Logs**:
   - ✅ Should see: "Running npm run vercel-build"
   - ✅ Should see: "Compiled successfully"
   - ✅ Should see: "The build folder is ready to be deployed"
   - ❌ If you see errors, fix them first

### 3. Check Function Logs

1. Go to **Deployments** → Latest deployment
2. Click **Functions** tab
3. Check if `api/index.py` is listed
4. If there are errors, check the logs

### 4. Common Issues and Fixes

#### Issue 1: Build Output Not Found
**Symptom**: 404 on all routes

**Fix**:
- Ensure `frontend/package.json` has `vercel-build` script
- Check that build completes successfully
- Verify `frontend/build` directory is created

#### Issue 2: Routes Not Matching
**Symptom**: 404 on specific routes

**Fix**:
- Verify `vercel.json` routes are correct
- Check that routes are in the right order (most specific first)

#### Issue 3: API Routes Not Working
**Symptom**: Frontend loads but API calls fail

**Fix**:
- Check that `api/index.py` exists
- Verify `requirements.txt` includes `mangum`
- Check function logs for errors

### 5. Redeploy After Fixes

After making changes:
1. Commit changes to GitHub
2. Push to main branch
3. Vercel will auto-deploy
4. OR manually trigger redeploy in Vercel dashboard

### 6. Test the Fix

1. Visit: `https://analysis-lime.vercel.app`
2. Should see the React app
3. Try uploading a file
4. Check browser console for errors

## Quick Checklist

- [ ] `vercel.json` is in root directory
- [ ] `api/index.py` exists
- [ ] `frontend/package.json` has `vercel-build` script
- [ ] `requirements.txt` includes `mangum`
- [ ] Build logs show successful compilation
- [ ] Root Directory is set to `./`
- [ ] Framework Preset is NOT "Flask"

## If Still Not Working

1. **Check Vercel Build Logs**:
   - Look for any error messages
   - Verify build completes successfully

2. **Check Browser Console**:
   - Open DevTools (F12)
   - Look for JavaScript errors
   - Check Network tab for failed requests

3. **Test API Directly**:
   - Visit: `https://analysis-lime.vercel.app/api/health`
   - Should return: `{"status":"ok"}`

4. **Verify File Structure**:
   - Ensure all files are committed to GitHub
   - Check that `vercel.json` is in the root
   - Verify `api/index.py` exists

5. **Try Manual Redeploy**:
   - Go to Vercel dashboard
   - Click "Redeploy" on latest deployment
   - Or create a new deployment

## Alternative: Use Vercel CLI

If dashboard isn't working, try CLI:

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

This will give you more detailed error messages.

