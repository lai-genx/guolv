@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo CT Intel Agent - Windows Setup
echo Project directory: %cd%
echo ========================================
echo.

set "PY_CMD="

where python >nul 2>nul
if not errorlevel 1 (
    python -c "import sys; sys.exit(0 if sys.version_info[:2] in ((3,10),(3,11),(3,12)) else 1)" >nul 2>nul && set "PY_CMD=python"
)

if "%PY_CMD%"=="" (
    for %%P in (
        "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
    ) do (
        if exist "%%~P" (
            "%%~P" -c "import sys; sys.exit(0 if sys.version_info[:2] in ((3,10),(3,11),(3,12)) else 1)" >nul 2>nul && set "PY_CMD=%%~P"
        )
    )
)

if "%PY_CMD%"=="" (
    echo ERROR: Compatible Python was not found.
    echo Please install Python 3.10, 3.11, or 3.12 from https://www.python.org/downloads/
    echo During installation, check "Add python.exe to PATH".
    pause
    exit /b 1
)

echo [1/5] Python detected:
%PY_CMD% --version
if errorlevel 1 (
    echo ERROR: Python exists but cannot run.
    pause
    exit /b 1
)

echo.
echo [2/5] Creating local virtual environment...
if not exist ".venv\Scripts\python.exe" (
    %PY_CMD% -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create .venv.
        pause
        exit /b 1
    )
) else (
    echo .venv already exists.
)

set "VENV_PY=%cd%\.venv\Scripts\python.exe"

echo.
echo [3/5] Installing Python dependencies...
"%VENV_PY%" -m pip install --upgrade pip
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [4/5] Installing Playwright Chromium...
"%VENV_PY%" -m playwright install chromium
if errorlevel 1 (
    echo WARNING: Playwright Chromium install failed.
    echo Web collector may not work until you run:
    echo "%VENV_PY%" -m playwright install chromium
)

echo.
echo [5/5] Preparing local files and folders...
if not exist data mkdir data
if not exist data\reports mkdir data\reports
if not exist data\plans mkdir data\plans
if not exist knowledge_base mkdir knowledge_base

if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo Created .env from .env.example.
    echo Please edit .env and fill at least one LLM API key before collecting.
) else (
    echo .env already exists.
)

echo.
echo ========================================
echo Setup finished.
echo Next steps:
echo 1. Edit .env and fill API keys.
echo 2. Double-click startup.bat or the Chinese startup file.
echo 3. Open http://localhost:8501
echo ========================================
pause
