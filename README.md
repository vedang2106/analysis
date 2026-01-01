# Data Analyst Automation Tool

A modern data analysis application with a React.js frontend and Python Flask backend. Accepts CSV/Excel/JSON files, auto-profiles, cleans, runs EDA, generates insights, and exports Excel/CSV/PDF deliverables.

## Architecture

- **Frontend**: React.js (lightweight, fast, modern UI)
- **Backend**: Python Flask API (RESTful endpoints)
- **Data Processing**: All existing backend logic preserved in `src/` modules

## Quickstart

### Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Windows PowerShell (or your terminal)

### Step 1: Setup Backend (Python)

```powershell
# Navigate to project directory
cd "C:\Users\ASUS\Desktop\analysis"

# Create virtual environment (if not exists)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Setup Frontend (React)

```powershell
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install
```

### Step 3: Run the Application

**Terminal 1 - Start Backend API:**
```powershell
cd "C:\Users\ASUS\Desktop\analysis"
.\.venv\Scripts\Activate.ps1
python api.py
```

The backend will run on `http://localhost:5000`

**Terminal 2 - Start React Frontend:**
```powershell
cd "C:\Users\ASUS\Desktop\analysis\frontend"
npm start
```

The frontend will run on `http://localhost:3000` and automatically open in your browser.

## Project Structure

```
analysis/
├── api.py                 # Flask backend API
├── app.py                 # Original Streamlit app (kept for reference)
├── requirements.txt       # Python dependencies
├── src/                   # Backend modules (unchanged)
│   ├── loaders.py
│   ├── profiling.py
│   ├── cleaning.py
│   ├── eda.py
│   ├── insights.py
│   ├── exports.py
│   └── nlqa.py
└── frontend/              # React.js frontend
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── App.js
        ├── index.js
        ├── index.css
        └── components/
            ├── FileUpload.js
            ├── DataOverview.js
            ├── DataCleaning.js
            ├── EDA.js
            ├── ChatWithData.js
            ├── Insights.js
            └── Exports.js
```

## API Endpoints

All endpoints are prefixed with `/api`:

- `POST /api/upload` - Upload dataset file
- `GET /api/overview` - Get data overview
- `POST /api/clean` - Clean the dataset
- `POST /api/eda` - Generate EDA charts
- `POST /api/qa` - Answer natural language questions
- `GET /api/insights` - Generate insights
- `GET /api/export/excel` - Export Excel report
- `GET /api/export/powerbi` - Export Power BI bundle
- `GET /api/export/pdf` - Export PDF report

## Features

- ✅ **Lightweight React UI** - Fast, responsive, no crashes
- ✅ **File detection and loading** (CSV, Excel, JSON)
- ✅ **Data understanding**: shape, dtypes, missingness, summary stats
- ✅ **Automated cleaning**: imputations, deduplication, type inference
- ✅ **EDA**: distributions, boxplots, correlation heatmap, time trends
- ✅ **Insights**: outliers, top correlations, narrative summary
- ✅ **Natural Language Q&A**: Ask questions about your data
- ✅ **Exports**: Excel (cleaned + summary), Power BI CSV, PDF report

## Development

### Backend Development

The Flask API (`api.py`) exposes all existing backend functions from `src/` modules. No changes were made to the backend logic - only wrapped in REST API endpoints.

### Frontend Development

The React frontend (`frontend/`) replicates all Streamlit UI functionality with modern React components. Uses:
- React Hooks for state management
- Axios for API calls
- React Dropzone for file uploads
- CSS Grid/Flexbox for responsive layout

## Environment Variables

Create a `.env` file in the `frontend/` directory (optional):

```
REACT_APP_API_URL=http://localhost:5000/api
```

## Notes

- For very large files, initial load may take longer.
- Excel export uses `xlsxwriter`; PDF export uses `reportlab`.
- Charts are converted to base64 images for frontend display.
- Session management handled via headers (`X-Session-ID`).

## Troubleshooting

**Backend won't start:**
- Ensure virtual environment is activated
- Check if port 5000 is available
- Verify all dependencies are installed: `pip install -r requirements.txt`

**Frontend won't start:**
- Ensure Node.js is installed: `node --version`
- Install dependencies: `cd frontend && npm install`
- Check if port 3000 is available

**CORS errors:**
- Ensure Flask-CORS is installed: `pip install flask-cors`
- Check that backend is running on port 5000

**File upload fails:**
- Check file size (limit: 200MB)
- Verify file format (CSV, XLSX, XLS, JSON)
- Check browser console for errors

## Migration from Streamlit

The original Streamlit app (`app.py`) is preserved and can still be run:

```powershell
streamlit run app.py
```

However, the new React + Flask architecture is recommended for better performance and stability.
