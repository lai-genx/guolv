@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo CT Intel Agent is starting...
echo Project directory: %cd%
echo ========================================
echo.

set "APP_URL=http://localhost:8501"
set "PYTHON_EXE="

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=%cd%\.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if not errorlevel 1 (
        python -c "import sys; sys.exit(0 if sys.version_info[:2] in ((3,10),(3,11),(3,12)) else 1)" >nul 2>nul && set "PYTHON_EXE=python"
    )
)

if "%PYTHON_EXE%"=="" (
    for %%P in (
        "%USERPROFILE%\AppData\Local\Programs\Python\Python311\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python310\python.exe"
        "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe"
    ) do (
        if exist "%%~P" (
            "%%~P" -c "import sys; sys.exit(0 if sys.version_info[:2] in ((3,10),(3,11),(3,12)) else 1)" >nul 2>nul && set "PYTHON_EXE=%%~P"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo ERROR: Compatible Python was not found.
    echo Please run setup.bat first, or install Python 3.10/3.11/3.12.
    pause
    exit /b 1
)

if not exist ".env" (
    echo .env was not found. Creating it from .env.example...
    copy ".env.example" ".env" >nul
    echo Please edit .env and fill at least one LLM API key.
    echo Then run this startup file again.
    pause
    exit /b 1
)

echo Using Python:
%PYTHON_EXE% --version
echo.

%PYTHON_EXE% -c "import streamlit" >nul 2>nul
if errorlevel 1 (
    echo ERROR: Streamlit is not installed in this Python environment.
    echo Please double-click setup.bat first, then run this startup file again.
    pause
    exit /b 1
)

start "" "%APP_URL%"
%PYTHON_EXE% -m streamlit run web_app.py --server.port 8501 --server.address localhost

echo.
echo The app has stopped. Press any key to close this window.
pause >nul
