@echo off
cd /d %~dp0
echo ===================================================
echo   Starting EduPrep AI Server and Mobile Tunnel...
echo ===================================================
start EduPrep AI Server %~dp0.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false
timeout /t 3 /nobreak >nul
start EduPrep Mobile Tunnel %~dp0cloudflared.exe tunnel --url http://localhost:8501 --protocol http2
start " http://localhost:8501
