# PowerShell script to start the React frontend
Write-Host "Starting React Frontend..." -ForegroundColor Green
$frontendPath = Join-Path $PSScriptRoot "frontend"
if (-not (Test-Path "$frontendPath\package.json")) {
    Write-Host "Error: package.json not found in frontend directory!" -ForegroundColor Red
    Write-Host "Expected path: $frontendPath" -ForegroundColor Yellow
    exit 1
}
Set-Location $frontendPath
Write-Host "Changed to directory: $(Get-Location)" -ForegroundColor Cyan
npm start

