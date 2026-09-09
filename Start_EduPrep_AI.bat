@echo off
cd /d "%~dp0"
echo Starting EduPrep AI Suite...
start "" http://localhost:8501
"%~dp0.venv\Scripts\python.exe" -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false
