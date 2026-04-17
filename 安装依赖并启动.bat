@echo off
chcp 65001 >nul 2>&1
title MingLi Engine

echo ========================================
echo   MingLi Prediction Engine
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/3] Installing dependencies...
pip install -r mingli_engine/requirements.txt -q
if errorlevel 1 (
    echo WARNING: Some dependencies failed to install, trying to continue...
)

echo [3/3] Starting server...
echo.
echo ========================================
echo   Server: http://localhost:18766
echo   Press Ctrl+C to stop
echo ========================================
echo.

cd mingli_engine
python main.py
pause
