# Step-by-Step Vercel Deployment Guide

## Prerequisites
- ✅ GitHub repository: `vedang2106/analysis`
- ✅ Vercel account (sign up at vercel.com if needed)

## Step 1: Import Project on Vercel

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/new
   - Or click "Add New Project" in your dashboard

2. **Import from GitHub**
   - Click "Import" next to your repository `vedang2106/analysis`
   - Or search for your repository and select it

## Step 2: Configure Project Settings

### Basic Configuration:
- **Vercel Team**: Select your team (e.g., "vedang's projects")
- **Project Name**: `analysis` (or your preferred name)
- **Framework Preset**: ⚠️ **IMPORTANT**: Change from "Flask" to **"Other"** or **"Create React App"**
  - Our project uses a custom setup with both React frontend and Python backend
  - The `vercel.json` file will handle the configuration

### Root Directory:
- **Root Directory**: Keep as `./` (project root)
  - This is correct because `vercel.json` is in the root

## Step 3: Build and Output Settings

Click "> Build and Output Settings" to expand:

### For Frontend Build:
- **Build Command**: `cd frontend && npm install && npm run build`
- **Output Directory**: `frontend/build`
- **Install Command**: `cd frontend && npm install`

**OR** (if using the vercel.json approach):
- Leave these empty - `vercel.json` will handle it automatically

### Recommended Settings:
Since we have `vercel.json` configured, you can:
- **Leave Build Settings empty** - Vercel will use `vercel.json`
- OR manually set:
  - Build Command: `cd frontend && npm run vercel-build`
  - Output Directory: `frontend/build`

## Step 4: Environment Variables

Click "> Environment Variables" to expand and add:

### Required Environment Variables:

1. **API_KEY** (if you're using one)
   - Name: `API_KEY`
   - Value: Your actual API key
   - Environment: Production, Preview, Development (select all)

2. **ALLOWED_ORIGINS** (Optional)
   - Name: `ALLOWED_ORIGINS`
   - Value: Your Vercel domain (will be set automatically after first deploy)
   - Environment: Production, Preview, Development

3. **FLASK_ENV** (Optional)
   - Name: `FLASK_ENV`
   - Value: `production`
   - Environment: Production, Preview

### How to Add:
1. Click "Add" or "+" button
2. Enter variable name
3. Enter variable value
4. Select environments (Production, Preview, Development)
5. Click "Save"

## Step 5: Deploy

1. **Review Settings**
   - Double-check Framework Preset is "Other" or "Create React App"
   - Verify Root Directory is `./`
   - Confirm environment variables are added

2. **Click "Deploy"**
   - Vercel will start building your project
   - This may take 2-5 minutes

## Step 6: Monitor Build Process

Watch the build logs for:
- ✅ Frontend build completing successfully
- ✅ Python dependencies installing
- ✅ Serverless function (`api/index.py`) being set up
- ❌ Any errors (will be highlighted in red)

## Step 7: After Deployment

### First Deployment:
1. Vercel will provide a URL like: `https://analysis-xxx.vercel.app`
2. **Test the deployment**:
   - Visit the URL
   - Try uploading a file
   - Check browser console for errors

### Update Environment Variables:
After first deploy, update `ALLOWED_ORIGINS`:
1. Go to Project Settings → Environment Variables
2. Edit `ALLOWED_ORIGINS`
3. Add your Vercel domain: `https://your-project.vercel.app`
4. Redeploy

## Step 8: Custom Domain (Optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## Troubleshooting

### Build Fails:
- Check build logs in Vercel dashboard
- Verify `vercel.json` is in root directory
- Ensure `api/index.py` exists
- Check that `requirements.txt` includes `mangum`

### API Routes Not Working:
- Verify `api/index.py` exists and exports `handler`
- Check Vercel function logs
- Ensure Python dependencies are in `requirements.txt`

### CORS Errors:
- Update `ALLOWED_ORIGINS` with your Vercel domain
- Redeploy after updating environment variables

### Frontend Not Loading:
- Check that `frontend/build` directory exists after build
- Verify `vercel.json` routes are correct
- Check browser console for errors

## Quick Checklist

Before deploying, ensure:
- [ ] `vercel.json` exists in root directory
- [ ] `api/index.py` exists and is correct
- [ ] `frontend/package.json` has `vercel-build` script
- [ ] `requirements.txt` includes `mangum`
- [ ] Environment variables are set (if needed)
- [ ] Framework Preset is "Other" or "Create React App" (not Flask)

## Important Notes

⚠️ **Framework Preset**: 
- Don't use "Flask" preset
- Use "Other" or "Create React App"
- Our `vercel.json` handles the custom setup

⚠️ **Root Directory**:
- Must be `./` (project root)
- `vercel.json` is in the root

⚠️ **Build Settings**:
- Can be left empty if using `vercel.json`
- OR manually configure as shown above

## Support

If you encounter issues:
1. Check Vercel build logs
2. Review `VERCEL_SETUP.md` for detailed information
3. Check Vercel function logs for API errors
4. Verify all files are committed to GitHub

