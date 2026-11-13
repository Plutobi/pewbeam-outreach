@echo off
title Pewbeam UK Church Outreach Hub
echo ====================================================
echo Starting Pewbeam UK Church Outreach Hub...
echo Open in browser: http://127.0.0.1:8080
echo ====================================================
cd /d "%~dp0"
start http://127.0.0.1:8080
python app.py
pause
