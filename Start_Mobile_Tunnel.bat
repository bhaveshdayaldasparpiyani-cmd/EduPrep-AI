@echo off
cd /d %~dp0
echo ===================================================
echo   Starting EduPrep AI Live Mobile Tunnel...
echo ===================================================
echo Tunnel is connecting to Cloudflare...
echo.
%~dp0cloudflared.exe tunnel --url http://localhost:8501 --protocol http2
pause
