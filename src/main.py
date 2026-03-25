import sys
import os

# Добавляем путь к папке src
src_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, src_path)

from gui.main_window import MainWindow
from utils.splash_screen import SplashScreen

def main():
    splash = SplashScreen()
    splash.update_status("Загрузка модулей...")
    import time
    time.sleep(0.5)
    
    splash.update_status("Проверка конфигурации...")
    time.sleep(0.5)
    
    splash.update_status("Загрузка интерфейса...")
    
    app = MainWindow()
    
    splash.update_status("Готово!")
    time.sleep(0.3)
    splash.close()
    
    app.run()

if __name__ == "__main__":
    main()