@echo off
REM KTVS - Kelley Token Validation System Startup Script
echo ================================================
echo  KTVS - Kelley Token Validation System
echo  Starting Development Server
echo ================================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
uv sync
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Running database migrations...
uv run python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)

echo.
echo [3/3] Starting development server...
echo.
echo Server will be available at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
uv run python manage.py runserver
