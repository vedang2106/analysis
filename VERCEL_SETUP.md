# Vercel Deployment Guide

This guide explains how to deploy the Data Analyst Automation Tool to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed (optional, for local testing): `npm i -g vercel`

## Deployment Steps

### 1. Environment Variables Setup

Before deploying, you need to set up environment variables in Vercel:

1. Go to your Vercel project settings
2. Navigate to "Environment Variables"
3. Add the following variables:
   - `API_KEY`: Your API key (if needed)
   - `ALLOWED_ORIGINS`: Comma-separated list of allowed origins (optional, defaults to localhost)
   - `FLASK_ENV`: Set to `production` for production deployments

### 2. Deploy via Vercel Dashboard

1. Push your code to GitHub/GitLab/Bitbucket
2. Go to https://vercel.com/new
3. Import your repository
4. Vercel will automatically detect the configuration from `vercel.json`
5. Click "Deploy"

### 3. Deploy via CLI

```bash
# Install Vercel CLI (if not already installed)
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# For production deployment
vercel --prod
```

## Project Structure

```
.
├── api/
│   └── index.py          # Vercel serverless function handler
├── frontend/             # React frontend
│   ├── src/
│   ├── package.json
│   └── build/            # Generated after build
├── src/                  # Backend source code
├── api.py                # Flask application
├── vercel.json           # Vercel configuration
└── requirements.txt      # Python dependencies
```

## How It Works

1. **Frontend**: React app is built and served as static files
2. **Backend**: Flask app is wrapped with Mangum to work as a Vercel serverless function
3. **Routing**: All `/api/*` requests are routed to the Python serverless function
4. **Environment Variables**: Loaded from Vercel's environment variables (not .env file in production)

## Important Notes

⚠️ **Serverless Function Limitations**:
- Vercel serverless functions have execution time limits (10s for Hobby, 60s for Pro)
- Large file uploads might timeout
- Heavy computations (pandas, matplotlib) might be slow
- Consider upgrading to Vercel Pro for better performance

⚠️ **Dependencies**:
- Large Python packages (pandas, matplotlib, etc.) might increase cold start time
- Total package size should be under 50MB for optimal performance

## Troubleshooting

### API Routes Not Working

1. Check that `api/index.py` exists and exports `handler`
2. Verify `vercel.json` routes are correct
3. Check Vercel function logs in the dashboard

### Environment Variables Not Loading

1. Ensure variables are set in Vercel dashboard
2. Redeploy after adding new environment variables
3. Check variable names match what's in the code

### Build Failures

1. Check that all dependencies are in `requirements.txt`
2. Verify Python version compatibility
3. Check Vercel build logs for specific errors

## Local Development

For local development, you can still use the original setup:

```bash
# Start backend
cd frontend
npm run start:backend

# Start frontend (in another terminal)
cd frontend
npm run start:frontend

# Or start both together
cd frontend
npm start
```

## API Endpoints

All API endpoints are available at `/api/*`:
- `/api/health` - Health check
- `/api/upload` - Upload dataset
- `/api/overview` - Get data overview
- `/api/clean` - Clean data
- `/api/eda` - Generate EDA charts
- `/api/qa` - Natural language Q&A
- `/api/insights` - Generate insights
- `/api/export/excel` - Export Excel
- `/api/export/powerbi` - Export Power BI bundle
- `/api/export/pdf` - Export PDF

