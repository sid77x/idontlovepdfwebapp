@echo off
echo Installing PDF Microservices Dependencies...
echo ===============================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your PATH
    pause
    exit /b 1
)

echo Python found. Installing dependencies...

REM Install requirements
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ================================
echo Dependencies installed successfully!
echo.
echo To start the microservices, run:
echo   python start_services.py
echo.
echo Or run individual services:
echo   cd services
echo   python merge_service.py
echo.
echo API Documentation will be available at:
echo   http://localhost:8000/docs  (Orchestrator)
echo   http://localhost:8001/docs  (Merge Service)
echo   http://localhost:8002/docs  (Rotate Service)
echo   http://localhost:8003/docs  (Split Service)
echo ================================
pause