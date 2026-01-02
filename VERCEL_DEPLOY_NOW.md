# Deploy Now - Final Settings

## ⚠️ IMPORTANT: Update Build Settings

Your current settings need to be changed because your React app is in the `frontend/` folder, not the root.

### Step 1: Update Build Command

1. Click the **edit icon** (pencil) next to "Build Command"
2. **Change from**: `npm run build` or `react-scripts build`
3. **Change to**: `cd frontend && npm run build`
4. Click "Save" or press Enter

### Step 2: Update Output Directory

1. Click the **edit icon** (pencil) next to "Output Directory"
2. **Change from**: `build`
3. **Change to**: `frontend/build`
4. Click "Save" or press Enter

### Step 3: Update Install Command (Optional but Recommended)

1. Click the **edit icon** (pencil) next to "Install Command"
2. **Change from**: `yarn install`, `pnpm install`, `npm install`, or `bun install`
3. **Change to**: `cd frontend && npm install`
4. Click "Save" or press Enter

### Step 4: Environment Variables (Optional)

You can remove the example variable `EXAMPLE_NAME` if you don't need it:
- Click the **minus icon** (-) next to it

Or add your own:
- Click **"+ Add More"**
- Add if needed:
  - Key: `API_KEY` (if you use one)
  - Value: Your actual API key
  - Or add later after deployment

### Step 5: Click "Deploy"

Once all settings are updated:
1. Click the black **"Deploy"** button
2. Wait for build to complete (2-5 minutes)
3. Watch the build progress

## Summary of Settings:

✅ **Framework Preset**: "Create React App" (correct)
✅ **Root Directory**: `./` (correct)
✅ **Build Command**: `cd frontend && npm run build` (UPDATE THIS)
✅ **Output Directory**: `frontend/build` (UPDATE THIS)
✅ **Install Command**: `cd frontend && npm install` (UPDATE THIS)

## After Deployment:

1. Vercel will show you a deployment URL
2. Visit the URL to see your app
3. Test: `your-url.vercel.app/api/health` should return `{"status":"ok"}`

