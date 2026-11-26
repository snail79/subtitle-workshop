@echo off
title Subtitle Workshop TTS Server
cd /d "%~dp0"
rem Use WorkBuddy bundled Python (has edge_tts installed)
set "PY=C:\Users\cyx\.workbuddy\binaries\python\versions\3.13.12\python.exe"
if exist "%PY%" (
  "%PY%" tts_server.py
) else (
  py tts_server.py 2>nul || python tts_server.py
)
echo.
echo Server stopped. Press any key to close.
pause >nul
