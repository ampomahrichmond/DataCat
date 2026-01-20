@echo off
REM Alteryx to Python Converter - Windows Startup Script

echo ========================================
echo   Alteryx to Python Converter
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip is not installed
    pause
    exit /b 1
)

echo [OK] pip is installed
echo.

REM Install/upgrade dependencies
echo Installing/upgrading dependencies...
echo.
pip install -r requirements.txt

echo.
echo ========================================
echo   Launching Application
echo ========================================
echo.
echo The app will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

REM Launch the application
streamlit run app.py

pause
