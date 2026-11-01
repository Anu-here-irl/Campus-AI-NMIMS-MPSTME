@echo off
title CampusAI - Complete Launcher (Server + Phone Bridge)
cls
echo ===================================================================
echo                     CAMPUS AI - SYSTEM LAUNCHER
echo ===================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

set ADB="%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
set PYTHON="%SCRIPT_DIR%.venv\Scripts\python.exe"

REM 1. Setup ADB Port Forwarding if device connected
if exist %ADB% (
    echo [*] Checking for connected Android phone via USB...
    %ADB% devices
    echo [*] Setting up port bridge: phone port 8000 -^> PC port 8000...
    %ADB% reverse tcp:8000 tcp:8000
    if %ERRORLEVEL% EQU 0 (
        echo [+] SUCCESS: Phone port 8000 bridged to PC via ADB Reverse!
    ) else (
        echo [i] Note: Phone not detected via ADB. If connecting via Wi-Fi, use your PC Wi-Fi IP.
    )
) else (
    echo [i] ADB not found at default SDK path. Continuing server launch...
)

echo.
echo ===================================================================
echo [*] Starting Campus AI FastAPI Backend Server on 0.0.0.0:8000...
echo.
echo   - Local PC access:  http://127.0.0.1:8000/
echo   - Android USB:      http://127.0.0.1:8000/
echo   - Swagger API Docs: http://127.0.0.1:8000/docs
echo.
echo   Press CTRL+C anytime in this window to stop the server.
echo ===================================================================
echo.

if exist %PYTHON% (
    %PYTHON% -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
) else (
    echo [!] Virtual environment not found at .venv\Scripts\python.exe!
    echo [*] Falling back to system uvicorn...
    uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
)

pause
