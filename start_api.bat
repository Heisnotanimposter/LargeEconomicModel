@echo off
REM Economic Data API Startup Script for Windows

echo ==========================================
echo   Economic Data API Startup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo Python is installed

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
if not exist "venv\.installed" (
    echo Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r api_requirements.txt
    echo. > venv\.installed
    echo Dependencies installed
) else (
    echo Dependencies already installed
)

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy .env.example .env
        echo Created .env file. Please edit it with your API keys.
    ) else (
        echo Error: .env.example not found. Please create a .env file.
    )
)

echo.
echo ==========================================
echo   Starting API Server
echo ==========================================
echo   API will be available at:
echo   - Main: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
echo ==========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the API server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

