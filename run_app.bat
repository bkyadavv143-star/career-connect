@echo off
title CareerConnect Job Board Launcher
echo ====================================================
echo Starting CareerConnect Job Board Platform...
echo ====================================================

cd /d "%~dp0"

echo Opening default browser to http://127.0.0.1:8000 ...
start http://127.0.0.1:8000/

echo.
echo Server is running! Keep this window open while using the app.
echo Press Ctrl+C or close this window to stop the server.
echo.

python manage.py runserver
pause

