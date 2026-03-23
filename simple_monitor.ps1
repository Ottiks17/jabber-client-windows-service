Write-Host "=== Jabber Service Monitor ===" -ForegroundColor Green
Write-Host ""

# Статус службы
 = sc.exe query JabberXMPPClient
Write-Host "Статус службы:" -ForegroundColor Cyan
 | Select-String "STATE"

Write-Host ""
Write-Host "Последние 10 строк service.log:" -ForegroundColor Cyan
if (Test-Path "logs\service.log") {
    Get-Content logs\service.log -Tail 10
} else {
    Write-Host "Файл service.log не найден" -ForegroundColor Red
}

Write-Host ""
Write-Host "Последние 5 строк messages.log:" -ForegroundColor Cyan
if (Test-Path "logs\messages.log") {
    Get-Content logs\messages.log -Tail 5
} else {
    Write-Host "Файл messages.log не найден" -ForegroundColor Red
}
