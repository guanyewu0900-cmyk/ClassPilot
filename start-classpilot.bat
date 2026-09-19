@echo off
setlocal
cd /d "%~dp0"

where node >nul 2>nul
if errorlevel 1 (
  echo Node.js 18 or later is required.
  echo Download it from https://nodejs.org/
  pause
  exit /b 1
)

if not exist ".env" (
  copy /Y ".env.example" ".env" >nul
  echo Created .env from .env.example.
  echo Add provider API keys to .env to enable AI responses.
)

start "ClassPilot Server" /D "%~dp0" cmd /k node server.js
timeout /t 2 >nul
start "" "http://localhost:5173/"

echo ClassPilot is starting at http://localhost:5173/
exit /b 0
