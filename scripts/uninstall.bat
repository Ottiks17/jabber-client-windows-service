@echo off
chcp 65001 > nul
title Jabber Robot - Удаление
color 0C

echo ========================================
echo    🗑️ JABBER ROBOT - УДАЛЕНИЕ
echo ========================================
echo.
echo ВНИМАНИЕ! Это удалит:
echo   - Windows Service (если установлен)
echo   - Все файлы проекта
echo   - Логи и настройки
echo.

choice /C YN /M "Продолжить удаление? (Y/N)"
if errorlevel 2 goto end

echo.
echo [1/4] Остановка службы...
net stop JabberXMPPClient 2>nul
echo ✅

echo.
echo [2/4] Удаление службы...
sc delete JabberXMPPClient 2>nul
echo ✅

echo.
echo [3/4] Удаление ярлыка...
del "%userprofile%\Desktop\Jabber Robot.lnk" 2>nul
echo ✅

echo.
echo [4/4] Удаление файлов...
cd ..
rmdir /S /Q jabber-client 2>nul
echo ✅

echo.
echo ========================================
echo    ✅ ПРОЕКТ УДАЛЕН
echo ========================================

:end
pause