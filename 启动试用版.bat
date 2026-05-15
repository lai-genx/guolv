@echo off
cd /d "%~dp0"

echo ========================================
echo Trial Report Demo
echo ========================================
echo.
echo Working directory: %cd%
echo URL: http://127.0.0.1:8502
echo.

python --version >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo [1/3] Checking Streamlit...
python -m streamlit --version >nul 2>nul
if errorlevel 1 (
    echo Streamlit was not found. Installing required packages...
    python -m pip install streamlit pandas plotly
    if errorlevel 1 (
        echo [ERROR] Failed to install Streamlit dependencies.
        pause
        exit /b 1
    )
)

echo [2/3] Opening browser after service starts...
start "" cmd /c "timeout /t 8 /nobreak >nul && start http://127.0.0.1:8502"

echo [3/3] Starting trial report service...
echo.
echo Keep this window open. Closing it will stop the web page.
echo If the browser does not open automatically, visit:
echo http://127.0.0.1:8502
echo.

python -m streamlit run trial_demo_app.py --server.port 8502 --server.address 127.0.0.1 --server.headless true

echo.
echo Service stopped. If this was unexpected, check the error messages above.
pause
