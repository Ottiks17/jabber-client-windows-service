@echo off
chcp 65001 > nul
title Jabber Robot - Запуск
color 0B

echo ========================================
echo    🤖 JABBER ROBOT - ЗАПУСК
echo ========================================
echo.
echo Выберите режим запуска:
echo.
echo   [1] 🖥️  GUI (основное приложение)
echo   [2] 🌐  Web Dashboard (мониторинг)
echo   [3] 📡  REST API сервер
echo   [4] 📊  Админ панель
echo   [5] 🚀  ВСЕ СЕРВИСЫ (GUI + API + Dashboard)
echo   [6] 🔧  Windows Service (управление)
echo.
set /p choice="Ваш выбор (1-6): "

if "%choice%"=="1" (
    echo.
    echo Запуск GUI...
    start python main.py
    goto end
)
if "%choice%"=="2" (
    echo.
    echo Запуск Web Dashboard...
    start http://localhost:8080
    start python web_dashboard.py
    goto end
)
if "%choice%"=="3" (
    echo.
    echo Запуск REST API...
    start http://localhost:5000
    start python api_server.py
    goto end
)
if "%choice%"=="4" (
    echo.
    echo Запуск Админ панели...
    start http://localhost:5001/admin
    start python admin_panel.py
    goto end
)
if "%choice%"=="5" (
    echo.
    echo Запуск всех сервисов...
    start python main.py
    timeout /t 2 /nobreak > nul
    start python api_server.py
    timeout /t 2 /nobreak > nul
    start python web_dashboard.py
    echo.
    echo ✅ Все сервисы запущены!
    echo    📱 GUI: открыто
    echo    🌐 API: http://localhost:5000
    echo    📊 Dashboard: http://localhost:8080
    goto end
)
if "%choice%"=="6" (
    echo.
    echo Управление Windows Service
    echo   [s] Запустить
    echo   [t] Остановить
    echo   [r] Перезапустить
    echo   [u] Удалить
    set /p sc_choice="Команда (s/t/r/u): "
    if "%sc_choice%"=="s" net start JabberXMPPClient
    if "%sc_choice%"=="t" net stop JabberXMPPClient
    if "%sc_choice%"=="r" (
        net stop JabberXMPPClient
        timeout /t 3 /nobreak > nul
        net start JabberXMPPClient
    )
    if "%sc_choice%"=="u" (
        net stop JabberXMPPClient 2>nul
        sc delete JabberXMPPClient
    )
    goto end
)

echo ❌ Неверный выбор!

:end
echo.
pause