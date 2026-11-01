@echo off
title CampusAI - Phone Reconnect Helper
cls
echo ========================================================
echo   CampusAI - Connect Phone & Reverse Port 8000
echo ========================================================
echo.

set ADB="%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"

if not exist %ADB% (
    echo [!] adb.exe not found in %LOCALAPPDATA%\Android\Sdk\platform-tools\
    echo     Please verify Android SDK is installed.
    pause
    exit /b 1
)

echo [*] Checking connected devices...
%ADB% devices
echo.

echo [*] Setting up reverse port tunnel (phone:8000 -^> PC:8000)...
%ADB% reverse tcp:8000 tcp:8000

if %ERRORLEVEL% EQU 0 (
    echo [+] SUCCESS: Device can now access CampusAI backend at http://127.0.0.1:8000!
) else (
    echo [!] WARNING: Could not set adb reverse.
    echo     1. Make sure USB Debugging is ON in Developer Options on your phone.
    echo     2. Unlock phone and tap 'Allow USB Debugging' if prompted.
    echo     3. Unplug and replug the cable, then re-run this script.
)

echo.
echo [*] Checking if Python Backend Server is running on port 8000...
netstat -ano | findstr :8000 | findstr LISTENING >nul
if %ERRORLEVEL% EQU 0 (
    echo [+] SUCCESS: Python server is running and LISTENING on port 8000!
) else (
    echo [!] NOTICE: Python backend is NOT currently running on port 8000!
    echo     Please double-click START_CAMPUS_AI.bat or run:
    echo     uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
)

echo.
echo ========================================================
echo Done! In your CampusAI phone app login screen, ensure:
echo Server URL is: http://127.0.0.1:8000/
echo ========================================================
pause
