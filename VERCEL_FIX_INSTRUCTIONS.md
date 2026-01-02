# Fix 404 Error on Vercel - Step by Step

## The Problem
Getting 404 error when accessing `https://analysis-lime.vercel.app`

## Solution

### Option 1: Update Vercel Project Settings (Recommended)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com
   - Open your project: `analysis-lime`

2. **Go to Settings → General**
   - Scroll to **Build & Development Settings**

3. **Update Build Settings**:
   - **Framework Preset**: Change to **"Create React App"** (NOT Flask, NOT Other)
   - **Root Directory**: Keep as `./` (project root)
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/build`
   - **Install Command**: `cd frontend && npm install`

4. **Save Settings**

5. **Redeploy**:
   - Go to **Deployments** tab
   - Click **"..."** (three dots) on latest deployment
   - Click **"Redeploy"**
   - OR push a new commit to trigger auto-deploy

### Option 2: Use vercel.json (Current Setup)

The `vercel.json` file has been updated. After pushing to GitHub:

1. **Commit and Push**:
   ```bash
   git add vercel.json
   git commit -m "Fix Vercel routing configuration"
   git push
   ```

2. **Vercel will auto-deploy**

3. **If still 404**, go to Vercel dashboard:
   - **Settings → General**
   - **Clear Build & Development Settings** (set to empty/auto-detect)
   - Let `vercel.json` handle everything
   - Redeploy

### Option 3: Manual Build Command Override

In Vercel Dashboard → Settings → General:

1. **Override Build Command**: 
   - Check "Override"
   - Enter: `cd frontend && npm install && npm run build`

2. **Override Output Directory**:
   - Check "Override"  
   - Enter: `frontend/build`

3. **Save and Redeploy**

## Verify Build Success

After redeploying, check:

1. **Build Logs**:
   - Go to **Deployments** → Latest deployment
   - Click on the deployment
   - Check **Build Logs**:
     - ✅ Should see: "Compiled successfully"
     - ✅ Should see: "The build folder is ready to be deployed"
     - ❌ If errors, fix them first

2. **Test the URL**:
   - Visit: `https://analysis-lime.vercel.app`
   - Should see the React app (not 404)

3. **Test API**:
   - Visit: `https://analysis-lime.vercel.app/api/health`
   - Should return: `{"status":"ok"}`

## Common Issues

### Issue: Build completes but still 404
**Solution**: 
- Check that `frontend/build/index.html` exists
- Verify Output Directory is exactly `frontend/build` (not `build` or `./build`)

### Issue: Build fails
**Solution**:
- Check build logs for errors
- Ensure `frontend/package.json` has `build` script
- Verify Node.js version (should be 18+)

### Issue: API routes work but frontend doesn't
**Solution**:
- Check that routes in `vercel.json` have `"handle": "filesystem"` before catch-all
- Verify static files are being served

## Quick Fix Checklist

- [ ] Framework Preset is "Create React App" (NOT Flask)
- [ ] Build Command: `cd frontend && npm run build`
- [ ] Output Directory: `frontend/build`
- [ ] Root Directory: `./`
- [ ] `vercel.json` exists in root
- [ ] `api/index.py` exists
- [ ] Build logs show "Compiled successfully"
- [ ] Redeployed after making changes

## Still Not Working?

1. **Check Vercel Function Logs**:
   - Go to **Deployments** → Latest → **Functions** tab
   - Check for any errors

2. **Try Vercel CLI**:
   ```bash
   npm i -g vercel
   vercel login
   vercel --prod
   ```
   This will show more detailed error messages

3. **Check GitHub**:
   - Ensure all files are committed
   - Verify `vercel.json` is in the root directory
   - Check that `frontend/package.json` exists

