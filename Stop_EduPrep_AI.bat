@echo off
echo ==============================================
echo   Stopping EduPrep AI Background Server...
echo ==============================================
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
taskkill /F /IM cloudflared.exe >nul 2>&1
echo.
echo [OK] Server has been completely stopped.
timeout /t 3
