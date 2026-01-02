# PowerShell script to start the Flask backend
Write-Host "Starting Flask Backend API..." -ForegroundColor Green
cd "C:\Users\ASUS\Desktop\analysis"
.\.venv\Scripts\Activate.ps1
python api.py

