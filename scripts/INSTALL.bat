@echo off
chcp 65001 > nul
title Jabber Robot - Установка
color 0A

echo ========================================
echo    🤖 JABBER ROBOT - УСТАНОВКА
echo ========================================
echo.

echo [1/6] Проверка Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo.
    echo Скачайте Python с https://www.python.org/downloads/
    echo При установке ОБЯЗАТЕЛЬНО отметьте "Add Python to PATH"
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% найден

echo.
echo [2/6] Проверка pip...
python -m pip --version > nul 2>&1
if errorlevel 1 (
    echo ❌ pip не найден, устанавливаю...
    python -m ensurepip
)
echo ✅ pip готов

echo.
echo [3/6] Установка зависимостей...
echo Это может занять несколько минут...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q -i https://pypi.tuna.tsinghua.edu.cn/simple/
echo ✅ Зависимости установлены

echo.
echo [4/6] Создание папок...
if not exist logs mkdir logs
if not exist templates mkdir templates 2>nul
echo ✅ Папки созданы

echo.
echo [5/6] Настройка конфигурации...
if not exist config.yaml (
    copy config.yaml.example config.yaml 2>nul
    if exist config.yaml.example (
        echo ✅ Создан config.yaml (отредактируйте его позже)
    ) else (
        echo ⚠️ config.yaml.example не найден, создаю шаблон...
        (
            echo xmpp:
            echo   server: "jabber.ru"
            echo   username: "your_login@jabber.ru"
            echo   password: "your_password"
            echo.
            echo oracle:
            echo   enabled: true
            echo.
            echo rest:
            echo   enabled: true
            echo   api_url: "http://localhost:5000"
            echo   api_key: "test-key-123"
        ) > config.yaml
        echo ✅ Создан config.yaml
    )
) else (
    echo ✅ config.yaml уже существует
)

echo.
echo [6/6] Создание ярлыка на рабочем столе...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%userprofile%\Desktop\Jabber Robot.lnk'); $sc.TargetPath = 'python.exe'; $sc.Arguments = 'main.py'; $sc.WorkingDirectory = '%cd%'; $sc.IconLocation = 'python.exe'; $sc.Save()" 2>nul
echo ✅ Ярлык создан

echo.
echo ========================================
echo    ✅ УСТАНОВКА ЗАВЕРШЕНА!
echo ========================================
echo.
echo 📝 Что дальше?
echo    1. Отредактируйте config.yaml (укажите ваш XMPP логин и пароль)
echo    2. Запустите программу: python main.py
echo    3. Или дважды кликните на ярлык на рабочем столе
echo.
echo 🚀 Быстрый запуск:
echo    python main.py
echo.
pause