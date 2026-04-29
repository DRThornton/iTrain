@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher 'py' was not found.
    echo Install Python and make sure the Python launcher is available, then try again.
    pause
    exit /b 1
)

py -m streamlit run app/main.py
if errorlevel 1 (
    echo.
    echo iTrain did not start successfully.
    echo Make sure dependencies are installed with:
    echo     py -m pip install -r requirements.txt
    pause
    exit /b 1
)

endlocal
