"""
Jabber Robot - Главный запуск
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.splash_screen import SplashScreen
from gui.main_window import MainWindow
from recovery_manager import RecoveryManager


def main():
    """Точка входа"""
    
    # Показываем splash screen
    splash = SplashScreen()
    splash.update_status("Загрузка модулей...")
    
    # Имитация загрузки
    import time
    time.sleep(0.5)
    
    splash.update_status("Проверка конфигурации...")
    time.sleep(0.5)
    
    splash.update_status("Загрузка интерфейса...")
    
    # Проверяем наличие иконки
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    
    # Создаем главное окно
    app = MainWindow()
    
    # Устанавливаем иконку
    if os.path.exists(icon_path):
        try:
            app.root.iconbitmap(icon_path)
        except:
            pass
    
    # Проверяем возможность восстановления
    recovery = RecoveryManager()
    recovery_info = recovery.get_recovery_info()
    
    if recovery_info['has_recovery'] and recovery_info['was_running']:
        splash.update_status("Обнаружены несохраненные данные...")
        time.sleep(0.5)
        
        # Спрашиваем о восстановлении
        result = messagebox.askyesno(
            "Восстановление",
            "Обнаружены несохраненные данные от предыдущего сеанса.\n"
            "Восстановить состояние?"
        )
        
        if result:
            state = recovery.restore_state()
            if state:
                splash.update_status("Восстановление состояния...")
                time.sleep(0.5)
                # Восстанавливаем состояние
                if 'sources_enabled' in state:
                    app.oracle_enabled.set(state['sources_enabled'].get('oracle', True))
                    app.rest_enabled.set(state['sources_enabled'].get('rest', True))
    
    # Закрываем splash screen
    splash.update_status("Готово!")
    time.sleep(0.3)
    splash.close()
    
    # Запускаем приложение
    app.run()


if __name__ == "__main__":
    main()