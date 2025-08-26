# Data Analyst Automation Tool

A Streamlit app that accepts CSV/Excel/JSON, auto-profiles, cleans, runs EDA, generates insights, and exports Excel/CSV/PDF deliverables.

## Quickstart (Windows PowerShell)

```powershell
cd "C:\Users\ASUS\Desktop\datanalysis auto"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Features
- File detection and loading (CSV, Excel, JSON)
- Data understanding: shape, dtypes, missingness, summary stats
- Automated cleaning: imputations, deduplication, type inference
- EDA: distributions, boxplots, correlation heatmap, time trends
- Insights: outliers, top correlations, narrative summary
- Exports: Excel (cleaned + summary), Power BI CSV, PDF report

## Notes
- For very large files, initial load may take longer.
- Excel export uses `xlsxwriter`; PDF export uses `reportlab`.
