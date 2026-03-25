@echo off
chcp 65001 > nul
title Jabber Robot - Web Dashboard
color 0D

echo ========================================
echo    ?? JABBER ROBOT - WEB DASHBOARD
echo ========================================
echo.

echo ?????? Web Dashboard (???? 8080)...
start http://localhost:8080
python src\web_dashboard.py

pause
