# Quick Start Guide

## Running the Application

### Method 1: Using Scripts (Easiest)

**Terminal 1 - Backend:**
```powershell
cd "C:\Users\ASUS\Desktop\analysis"
.\start_backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
cd "C:\Users\ASUS\Desktop\analysis"
.\start_frontend.ps1
```

### Method 2: Manual Commands

**Terminal 1 - Backend:**
```powershell
cd "C:\Users\ASUS\Desktop\analysis"
.\.venv\Scripts\Activate.ps1
python api.py
```

**Terminal 2 - Frontend:**
```powershell
cd "C:\Users\ASUS\Desktop\analysis\frontend"
npm start
```

## First Time Setup (If Not Done Already)

### Backend Setup:
```powershell
cd "C:\Users\ASUS\Desktop\analysis"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Setup:
```powershell
cd "C:\Users\ASUS\Desktop\analysis\frontend"
npm install
```

## Access the Application

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **API Health Check:** http://localhost:5000/api/health

## Troubleshooting

**If you get PowerShell execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**If backend won't start:**
- Make sure virtual environment is activated (you should see `(.venv)` in prompt)
- Check if port 5000 is available
- Verify Flask is installed: `pip list | findstr flask`

**If frontend won't start:**
- Make sure Node.js is installed: `node --version`
- Install dependencies: `cd frontend && npm install`
- Check if port 3000 is available

**If file upload fails:**
- Check browser console (F12) for errors
- Check Flask terminal for error messages
- Verify file format (CSV, XLSX, XLS, JSON)
- Check file size (limit: 200MB)

