@echo off
title Lesson Plan AI Generator - Web Interface

echo ====================================
echo Lesson Plan AI Generator - Web Interface
echo ====================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found, please install Python 3.8 or higher
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Show Python version
echo Python version:
python --version
echo.

:: Start Web application
echo Starting Web interface...
echo Please ensure Ollama service is running (http://localhost:11434)
echo.

python start_web.py

:: If exit with error, pause to view error message
if %errorlevel% neq 0 (
    echo.
    echo Program exited with error code: %errorlevel%
    pause
)