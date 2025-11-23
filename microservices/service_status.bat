@echo off
REM Check status of all PDF microservices
cd /d "%~dp0"

python stop_services.py status

pause
