while(True) {
    Clear-Host
    Write-Host "=== Мониторинг Jabber Service ===" -ForegroundColor Green
    Write-Host "Время: 03/20/2026 10:02:21" -ForegroundColor Yellow
    Write-Host ""
    
    # Статус службы
    try {
         = sc.exe query JabberXMPPClient | Select-String "STATE"
        if () {
            Write-Host "Статус: " -ForegroundColor Cyan
        } else {
            Write-Host "Статус: Служба не найдена" -ForegroundColor Red
        }
    } catch {
        Write-Host "Ошибка получения статуса службы" -ForegroundColor Red
    }
    
    # Процесс
    try {
         = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { .Id -eq 10632 }
        if () {
             = [math]::Round(.CPU, 2)
             = [math]::Round(.WorkingSet / 1MB, 2)
            Write-Host "Процесс: Python (PID: ) CPU: s RAM:  MB" -ForegroundColor Cyan
        } else {
            Write-Host "Процесс Python с PID 10632 не найден" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Ошибка получения информации о процессе" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Последние 5 записей service.log:" -ForegroundColor Yellow
    
    # Проверяем логи службы
    if (Test-Path "logs\service.log") {
        Get-Content logs\service.log -Tail 5 -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host  -ForegroundColor White
        }
    } else {
        Write-Host "Файл service.log не найден" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Последние 3 сообщения:" -ForegroundColor Yellow
    
    # Проверяем логи сообщений
    if (Test-Path "logs\messages.log") {
        Get-Content logs\messages.log -Tail 3 -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host  -ForegroundColor White
        }
    } else {
        Write-Host "Файл messages.log не найден" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Нажмите Ctrl+C для выхода" -ForegroundColor Green
    
    Start-Sleep -Seconds 5
}
