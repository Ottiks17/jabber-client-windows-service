@echo off
chcp 65001 > nul
echo Создание ярлыка на рабочий стол...

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $sc = $ws.CreateShortcut('%userprofile%\Desktop\Jabber Robot.lnk'); $sc.TargetPath = 'python.exe'; $sc.Arguments = 'main.py'; $sc.WorkingDirectory = '%cd%'; $sc.IconLocation = 'python.exe,0'; $sc.Save()"

if errorlevel 1 (
    echo ❌ Не удалось создать ярлык
) else (
    echo ✅ Ярлык создан на рабочем столе
)

pause