# Quick Fix for Vercel 404 Error

## ⚠️ CRITICAL: Change Root Directory

On the Vercel import page, you need to change:

### Current (WRONG):
- **Root Directory**: `frontend` ❌

### Should Be (CORRECT):
- **Root Directory**: `./` (project root) ✅

## Steps to Fix:

1. **On the Vercel Import Page:**
   - Find "Root Directory" field
   - Click "Edit" button next to it
   - Change from `frontend` to `./` (or leave empty for project root)
   - Click "Save" or "Done"

2. **Keep These Settings (They're Correct):**
   - ✅ Framework Preset: "Create React App"
   - ✅ Build Command: `cd frontend && npm run build`
   - ✅ Output Directory: `frontend/build`
   - ✅ Install Command: `cd frontend && npm install`

3. **Click "Deploy"**

## Why This Matters:

- `vercel.json` is in the project root (not in frontend/)
- `api/index.py` is in the project root (not in frontend/)
- Vercel needs to see the entire project structure
- Setting root to `frontend` makes Vercel only see the frontend folder

## After Deployment:

1. Wait for build to complete (2-5 minutes)
2. Visit your deployment URL
3. Should see your React app (not 404)

