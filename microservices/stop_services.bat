@echo off
REM Stop all PDF microservices
cd /d "%~dp0"

echo Stopping PDF Microservices...
python stop_services.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo All services stopped successfully!
) else (
    echo.
    echo Some services failed to stop. Try running as administrator.
)

pause
