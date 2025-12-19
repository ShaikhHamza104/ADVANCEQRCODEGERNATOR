#!/bin/bash
# KTVS - Kelley Token Validation System Startup Script
echo "================================================"
echo " KTVS - Kelley Token Validation System"
echo " Starting Development Server"
echo "================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

echo "[1/3] Installing dependencies..."
uv sync
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[2/3] Running database migrations..."
uv run python manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to run migrations"
    exit 1
fi

echo ""
echo "[3/3] Starting development server..."
echo ""
echo "Server will be available at: http://127.0.0.1:8000"
echo "Press Ctrl+C to stop the server"
echo ""
uv run python manage.py runserver
