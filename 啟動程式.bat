@echo off
chcp 65001

echo ============================
echo        Magnifier
echo ============================

python --version >nul 2>&1
if errorlevel 1 (
    echo [Error] Python not found
    echo Please install Python 3.8 or later
    echo Download: www.python.org/downloads
    goto end
)

pip install -r requirements.txt
if errorlevel 1 (
    echo [Error] Package installation failed
    goto end
)

echo [OK] Starting...
python main.py

:end
echo ============================
pause 