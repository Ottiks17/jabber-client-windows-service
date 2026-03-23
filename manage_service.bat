@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ===== Jabber XMPP Client Service Manager =====
echo.

if "%1"=="" (
    echo Использование:
    echo   %0 install   - Установить службу
    echo   %0 start     - Запустить службу
    echo   %0 stop      - Остановить службу
    echo   %0 restart   - Перезапустить службу
    echo   %0 remove    - Удалить службу
    echo   %0 status    - Проверить статус
    goto :eof
)

if "%1"=="install" (
    echo Установка службы...
    python jabber_service.py install
    echo.
    echo Для автоматического запуска при старте системы выполните:
    echo sc config JabberXMPPClient start= auto
    goto :eof
)

if "%1"=="start" (
    echo Запуск службы...
    net start JabberXMPPClient
    goto :eof
)

if "%1"=="stop" (
    echo Остановка службы...
    net stop JabberXMPPClient
    goto :eof
)

if "%1"=="restart" (
    echo Перезапуск службы...
    net stop JabberXMPPClient
    timeout /t 3 /nobreak > nul
    net start JabberXMPPClient
    goto :eof
)

if "%1"=="remove" (
    echo Удаление службы...
    net stop JabberXMPPClient 2>nul
    timeout /t 3 /nobreak > nul
    python jabber_service.py remove
    goto :eof
)

if "%1"=="status" (
    sc query JabberXMPPClient
    goto :eof
)

echo Неизвестная команда: %1
