@echo off
REM ===================================================================
REM  MPLADS Intelligence - start the whole demo, reachable on the wifi.
REM
REM  Just double-click this file, or run:  run.cmd
REM
REM  Ports live in frontend\vite.config.js (WEB_PORT / API_PORT). If you
REM  change them there, change the two numbers below to match -- the web
REM  server proxies /api to the API, so a mismatch means every page loads
REM  and every figure is missing, which is a confusing way to fail.
REM
REM  The port and health-check logic lives in scripts\ports.ps1 rather
REM  than inline here. Escaping a PowerShell one-liner inside a batch
REM  file is a trap: a caret continuation plus a quoted string with a
REM  pipe in it silently produces a command that does nothing, reports
REM  success, and leaves the port held.
REM ===================================================================

set API_PORT=8020
set WEB_PORT=4300
set PORTS=powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\ports.ps1"

cd /d "%~dp0"

echo.
echo  Clearing ports %API_PORT% and %WEB_PORT%...
%PORTS% -Action free -Ports %API_PORT%,%WEB_PORT%

%PORTS% -Action check -Ports %API_PORT%,%WEB_PORT%
if errorlevel 1 (
  echo.
  pause
  exit /b 1
)

echo.
echo  Starting the API on 0.0.0.0:%API_PORT% ...
start "MPLADS API" cmd /k ".venv\Scripts\python.exe -m uvicorn mplads.api.app:app --host 0.0.0.0 --port %API_PORT%"

echo  Waiting for the API to warm its caches...
%PORTS% -Action wait -Url "http://127.0.0.1:%API_PORT%/api/health"

echo.
echo  Starting the web app on 0.0.0.0:%WEB_PORT% ...
REM host and port both come from vite.config.js, so there is one source of truth.
start "MPLADS Web" cmd /k "cd frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo  ==========================================================
echo   On this machine :  http://localhost:%WEB_PORT%
echo.
echo   On the wifi, from a phone or another laptop, use the
echo   "Network:" address printed in the MPLADS Web window.
echo  ==========================================================
echo.
echo  Both servers run in their own windows. Close those windows to stop them.
echo.
pause
