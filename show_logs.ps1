# Устанавливаем кодировку UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > 

Write-Host "=== Логи службы ===" -ForegroundColor Green

# Показываем логи службы
Write-Host "
Сервисные логи:" -ForegroundColor Yellow
if (Test-Path "logs\service.log") {
    Get-Content "logs\service.log" -Encoding UTF8 -Tail 20
} else {
    Write-Host "Файл service.log не найден" -ForegroundColor Red
}

# Показываем логи сообщений
Write-Host "
Сообщения:" -ForegroundColor Yellow
if (Test-Path "logs\messages.log") {
    Get-Content "logs\messages.log" -Encoding UTF8 -Tail 5
} else {
    Write-Host "Файл messages.log не найден" -ForegroundColor Red
}

Read-Host "
Нажмите Enter для выхода"
