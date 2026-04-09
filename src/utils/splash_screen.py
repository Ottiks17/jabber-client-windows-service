import tkinter as tk
from tkinter import ttk
import time

class SplashScreen:
    """Анимация загрузки при старте приложения"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        
        self.bg_color = "#6C5CE7"
        self.accent_color = "#FFFFFF"
        
        self.width = 500
        self.height = 350
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        self.root.configure(bg=self.bg_color)
        self.root.attributes('-topmost', True)
        
        self.create_window()
        self.animation_progress = 0
        self.animate()
        
    def create_window(self):
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        self.robot_label = tk.Label(main_frame, text="🤖", font=('Segoe UI', 80),
                                    bg=self.bg_color, fg=self.accent_color)
        self.robot_label.pack(pady=20)
        
        title = tk.Label(main_frame, text="Jabber Robot", 
                        font=('Segoe UI', 28, 'bold'),
                        bg=self.bg_color, fg=self.accent_color)
        title.pack(pady=10)
        
        version = tk.Label(main_frame, text="Версия 3.0", 
                          font=('Segoe UI', 10),
                          bg=self.bg_color, fg='#E0E0E0')
        version.pack()
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=20)
        self.progress.start(10)
        
        self.status_label = tk.Label(main_frame, text="Инициализация...", 
                                     font=('Segoe UI', 10),
                                     bg=self.bg_color, fg='#E0E0E0')
        self.status_label.pack(pady=5)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=10, background=self.accent_color)
    
    def update_status(self, text):
        self.status_label.config(text=text)
        self.root.update()
    
    def animate(self):
        self.animation_progress += 1
        if self.animation_progress < 30:
            size = 80 + int(5 * (self.animation_progress % 10 - 5))
            self.robot_label.config(font=('Segoe UI', size))
            self.root.after(50, self.animate)
    
    def close(self):
        self.progress.stop()
        self.root.destroy()