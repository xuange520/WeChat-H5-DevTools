@echo off
cd /d "%~dp0"
python app.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start WebView2 window. Falling back to browser preview...
    python app.py --browser
)