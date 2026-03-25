import tkinter as tk
from tkinter import ttk
import threading
import time

class SplashScreen:
    """Анимация загрузки при старте приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        
        # Цвета
        self.bg_color = "#6C5CE7"
        self.accent_color = "#FFFFFF"
        
        # Размеры
        self.width = 500
        self.height = 350
        
        # Центрируем окно
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        # Настройка окна
        self.root.configure(bg=self.bg_color)
        self.root.attributes('-topmost', True)
        
        # Убираем стандартную рамку, но добавляем свою
        self.create_window()
        
        # Запускаем анимацию
        self.animation_progress = 0
        self.animate()
        
    def create_window(self):
        """Создание элементов окна загрузки"""
        # Основной фрейм
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Логотип
        logo_frame = tk.Frame(main_frame, bg=self.bg_color)
        logo_frame.pack(pady=20)
        
        # Анимированный робот
        self.robot_label = tk.Label(logo_frame, text="🤖", font=('Segoe UI', 80),
                                    bg=self.bg_color, fg=self.accent_color)
        self.robot_label.pack()
        
        # Название
        title = tk.Label(main_frame, text="Jabber Robot", 
                        font=('Segoe UI', 28, 'bold'),
                        bg=self.bg_color, fg=self.accent_color)
        title.pack(pady=10)
        
        # Версия
        version = tk.Label(main_frame, text="Версия 3.0", 
                          font=('Segoe UI', 10),
                          bg=self.bg_color, fg='#E0E0E0')
        version.pack()
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', 
                                        length=300, style='TProgressbar')
        self.progress.pack(pady=20)
        self.progress.start(10)
        
        # Статус
        self.status_label = tk.Label(main_frame, text="Инициализация...", 
                                     font=('Segoe UI', 10),
                                     bg=self.bg_color, fg='#E0E0E0')
        self.status_label.pack(pady=5)
        
        # Создаем стиль для прогресс-бара
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=10, background=self.accent_color)
        
    def update_status(self, text):
        """Обновление текста статуса"""
        self.status_label.config(text=text)
        self.root.update()
    
    def animate(self):
        """Анимация робота"""
        self.animation_progress += 1
        if self.animation_progress < 30:
            # Робот двигается
            size = 80 + int(5 * (self.animation_progress % 10 - 5))
            self.robot_label.config(font=('Segoe UI', size))
            self.root.after(50, self.animate)
    
    def close(self):
        """Закрыть окно загрузки"""
        self.progress.stop()
        self.root.destroy()