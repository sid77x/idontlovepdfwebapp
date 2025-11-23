@echo off
REM IdontLovePDF Docker Startup Script for Windows
REM This script helps you start the application using Docker

echo.
echo 🐳 IdontLovePDF Docker Startup
echo ================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not installed
    echo Please install Docker Desktop from https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Error: Docker Compose is not installed
        echo Please install Docker Desktop which includes Docker Compose
        exit /b 1
    )
    set COMPOSE_CMD=docker compose
) else (
    set COMPOSE_CMD=docker-compose
)

REM Parse command line arguments
set MODE=%1
if "%MODE%"=="" set MODE=production

if /i "%MODE%"=="production" goto production
if /i "%MODE%"=="prod" goto production
if /i "%MODE%"=="development" goto development
if /i "%MODE%"=="dev" goto development
if /i "%MODE%"=="build" goto build
if /i "%MODE%"=="stop" goto stop
if /i "%MODE%"=="restart" goto restart
if /i "%MODE%"=="logs" goto logs
if /i "%MODE%"=="status" goto status
if /i "%MODE%"=="clean" goto clean
if /i "%MODE%"=="help" goto help
if /i "%MODE%"=="--help" goto help
if /i "%MODE%"=="-h" goto help

echo ❌ Unknown command: %MODE%
echo Run 'docker-start.bat help' for usage information
exit /b 1

:production
echo 🚀 Starting in PRODUCTION mode...
echo.
%COMPOSE_CMD% up -d
goto show_urls

:development
echo 🔧 Starting in DEVELOPMENT mode...
echo.
%COMPOSE_CMD% -f docker-compose.dev.yml up
goto end

:build
echo 🔨 Building Docker images...
echo.
%COMPOSE_CMD% build --no-cache
goto end

:stop
echo 🛑 Stopping all services...
echo.
%COMPOSE_CMD% down
goto end

:restart
echo 🔄 Restarting all services...
echo.
%COMPOSE_CMD% restart
goto end

:logs
echo 📋 Showing logs...
echo.
%COMPOSE_CMD% logs -f
goto end

:status
echo 📊 Service status:
echo.
%COMPOSE_CMD% ps
goto end

:clean
echo 🧹 Cleaning up (removing containers, volumes, and images)...
echo.
%COMPOSE_CMD% down -v --rmi all
goto end

:help
echo Usage: docker-start.bat [command]
echo.
echo Commands:
echo   production, prod    Start in production mode (default)
echo   development, dev    Start in development mode with hot-reload
echo   build               Rebuild all Docker images
echo   stop                Stop all services
echo   restart             Restart all services
echo   logs                Show and follow logs
echo   status              Show service status
echo   clean               Remove all containers, volumes, and images
echo   help                Show this help message
echo.
goto end

:show_urls
echo.
echo ✅ Services are starting...
echo.
echo 📱 Access the application at:
echo    • Streamlit App:      http://localhost:8501
echo    • Microservices API:  http://localhost:8000
echo    • API Documentation:  http://localhost:8000/docs
echo    • React Frontend:     http://localhost:3000
echo.
echo 📊 Check service status: docker-start.bat status
echo 📋 View logs:            docker-start.bat logs
echo 🛑 Stop services:        docker-start.bat stop
echo.

:end
exit /b 0
