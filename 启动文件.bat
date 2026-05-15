@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo CT Intel Agent is starting...
echo Project directory: %cd%
echo ========================================
echo.

set "PYTHON_EXE=C:\Users\chend\AppData\Local\Programs\Python\Python311\python.exe"
set "STREAMLIT_EXE=C:\Users\chend\AppData\Local\Programs\Python\Python311\Scripts\streamlit.exe"
set "APP_URL=http://localhost:8501"

if exist "%STREAMLIT_EXE%" (
    echo Using Streamlit executable:
    echo %STREAMLIT_EXE%
    start "" "%APP_URL%"
    "%STREAMLIT_EXE%" run web_app.py --server.port 8501 --server.address localhost
    goto END
)

if exist "%PYTHON_EXE%" (
    echo Streamlit executable was not found. Trying python -m streamlit...
    start "" "%APP_URL%"
    "%PYTHON_EXE%" -m streamlit run web_app.py --server.port 8501 --server.address localhost
    goto END
)

echo ERROR: Python/Streamlit was not found.
echo Please check whether Python 3.11 and Streamlit are installed.

:END
echo.
echo The startup window is closing or the app has stopped.
echo Press any key to close this window.
pause >nul
