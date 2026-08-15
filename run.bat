@echo off
setlocal
title avii's YT Grabber
echo ========================================
echo    Starting avii's YT Grabber...
echo ========================================

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not found on your system!
        echo Please install Python from https://www.python.org and check "Add Python to PATH".
        pause
        exit /b 1
    ) else (
        set PY_CMD=py
    )
) else (
    set PY_CMD=python
)

:: Install / verify dependencies quietly
echo Checking dependencies...
%PY_CMD% -m pip install -r requirements.txt --quiet --no-warn-script-location

:: Run the app
echo Launching...
%PY_CMD% main.py

if %errorlevel% neq 0 (
    echo.
    echo [Notice] App finished with an exit code.
    pause
)
