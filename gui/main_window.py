import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import yaml
import threading
import requests
import os
import sys
import getpass
from datetime import datetime
from api.core import MessagingCore
from sources.oracle_source import OracleSource
from sources.rest_source import RestSource
from sender.real_xmpp_sender import RealXmppSender
from api.logger import FileLogger
import pystray
from PIL import Image, ImageDraw
import winsound
import subprocess
import json
import pandas as pd
from datetime import datetime, timedelta


class RoundedButton(tk.Canvas):
    """Кастомная кнопка с закругленными углами"""
    def __init__(self, parent, text, command, bg_color, hover_color, fg_color="white", width=120, height=32):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=parent['bg'])
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.text = text
        self.width = width
        self.height = height
        self.current_color = bg_color
        self.enabled = True

        self.bind('<Button-1>', self.on_click)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)

        self.draw_button()

    def draw_button(self):
        self.delete("all")
        radius = 16
        self.create_rounded_rect(0, 0, self.width, self.height, radius, fill=self.current_color, outline="")
        self.create_text(self.width // 2, self.height // 2, text=self.text, fill=self.fg_color,
                         font=('Segoe UI', 10, 'bold'))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [x1 + radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_click(self, event):
        if self.enabled:
            self.command()

    def on_enter(self, event):
        if self.enabled:
            self.current_color = self.hover_color
            self.draw_button()

    def on_leave(self, event):
        if self.enabled:
            self.current_color = self.bg_color
            self.draw_button()

    def config(self, **kwargs):
        if 'state' in kwargs:
            if kwargs['state'] == 'disabled':
                self.enabled = False
                self.current_color = '#CCCCCC'
                self.draw_button()
            else:
                self.enabled = True
                self.current_color = self.bg_color
                self.draw_button()


class RoundedEntry(tk.Frame):
    """Поле ввода с закругленными углами"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=parent['bg'], highlightthickness=0, bd=0)
        self.entry = tk.Entry(self, **kwargs)
        self.entry.pack(fill='both', expand=True, padx=2, pady=2)
        self.update_bg(parent['bg'])

    def update_bg(self, bg_color):
        self.configure(bg=bg_color)
        self.entry.configure(bg=bg_color)

    def get(self):
        return self.entry.get()

    def insert(self, index, text):
        self.entry.insert(index, text)

    def delete(self, first, last=None):
        self.entry.delete(first, last)

    def config(self, **kwargs):
        self.entry.config(**kwargs)


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
        
        self.create_window()
        self.animation_progress = 0
        self.animate()
        
    def create_window(self):
        """Создание элементов окна загрузки"""
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Анимированный робот
        self.robot_label = tk.Label(main_frame, text="🤖", font=('Segoe UI', 80),
                                    bg=self.bg_color, fg=self.accent_color)
        self.robot_label.pack(pady=20)
        
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
                                        length=300)
        self.progress.pack(pady=20)
        self.progress.start(10)
        
        # Статус
        self.status_label = tk.Label(main_frame, text="Инициализация...", 
                                     font=('Segoe UI', 10),
                                     bg=self.bg_color, fg='#E0E0E0')
        self.status_label.pack(pady=5)
        
        # Стиль для прогресс-бара
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
            size = 80 + int(5 * (self.animation_progress % 10 - 5))
            self.robot_label.config(font=('Segoe UI', size))
            self.root.after(50, self.animate)
    
    def close(self):
        """Закрыть окно загрузки"""
        self.progress.stop()
        self.root.destroy()


class RecoveryManager:
    """Управление автоматическим восстановлением после сбоя"""
    
    def __init__(self, recovery_file="logs/recovery.json"):
        self.recovery_file = recovery_file
        self.ensure_logs_dir()
    
    def ensure_logs_dir(self):
        """Создание папки для логов"""
        os.makedirs(os.path.dirname(self.recovery_file), exist_ok=True)
    
    def save_state(self, core_state):
        """Сохранение состояния"""
        state = {
            'timestamp': datetime.now().isoformat(),
            'version': '3.0',
            'is_running': core_state.get('is_running', False),
            'sources_enabled': core_state.get('sources_enabled', {}),
            'last_message_id': core_state.get('last_message_id', None),
            'last_check': datetime.now().isoformat()
        }
        
        try:
            with open(self.recovery_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения состояния: {e}")
            return False
    
    def restore_state(self):
        """Восстановление состояния после сбоя"""
        try:
            if os.path.exists(self.recovery_file):
                with open(self.recovery_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Проверяем актуальность состояния (не старше 1 часа)
                last_check = datetime.fromisoformat(state['last_check'])
                if (datetime.now() - last_check).seconds < 3600:
                    return state
        except Exception as e:
            print(f"Ошибка восстановления состояния: {e}")
        
        return None
    
    def clear_state(self):
        """Очистка сохраненного состояния"""
        try:
            if os.path.exists(self.recovery_file):
                os.remove(self.recovery_file)
        except:
            pass
    
    def get_recovery_info(self):
        """Получить информацию о последнем восстановлении"""
        state = self.restore_state()
        if state:
            return {
                'has_recovery': True,
                'timestamp': state['timestamp'],
                'was_running': state['is_running']
            }
        return {'has_recovery': False}


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jabber Robot")
        self.root.geometry("1280x800")
        self.root.protocol('WM_DELETE_WINDOW', self.hide_window)
        
        # Устанавливаем иконку
        self.setup_icon()
        
        # Загружаем сохраненную тему
        self.is_dark = self.load_theme()
        self.auto_start = self.load_auto_start_setting()
        
        # Устанавливаем цветовую схему
        self.set_theme(self.is_dark)
        
        self.core = None
        self.config = self.load_config()
        self.menu_window = None
        self.tray_icon = None
        self.recovery = RecoveryManager()
        
        self.setup_ui()
        self.setup_scroll_binding()
        
        # Настраиваем автозагрузку
        self.setup_auto_start()
        
        # Создаем иконку в трее
        self.setup_tray_icon()
        
        # Восстанавливаем состояние после сбоя
        self.auto_recovery()
        
        # Запускаем сервис автоматически, если был запущен
        self.auto_start_service()

    def setup_icon(self):
        """Установка иконки приложения"""
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                pass

    def save_state_for_recovery(self):
        """Сохранить состояние для восстановления"""
        state = {
            'is_running': self.core is not None and self.core.is_running,
            'sources_enabled': {
                'oracle': self.oracle_enabled.get(),
                'rest': self.rest_enabled.get()
            },
            'last_message_id': getattr(self, 'last_message_id', None)
        }
        self.recovery.save_state(state)

    def auto_recovery(self):
        """Автоматическое восстановление после запуска"""
        recovery_info = self.recovery.get_recovery_info()
        
        if recovery_info['has_recovery'] and recovery_info['was_running']:
            result = messagebox.askyesno(
                "Восстановление",
                "Обнаружены несохраненные данные от предыдущего сеанса.\n"
                "Восстановить состояние?"
            )
            
            if result:
                state = self.recovery.restore_state()
                if state:
                    # Восстанавливаем состояние
                    if 'sources_enabled' in state:
                        self.oracle_enabled.set(state['sources_enabled'].get('oracle', True))
                        self.rest_enabled.set(state['sources_enabled'].get('rest', True))
                    
                    # Автоматически запускаем сервис
                    self.start_service()
            
            # Очищаем состояние после восстановления
            self.recovery.clear_state()

    def create_tray_image(self):
        """Создать иконку для системного трея"""
        size = 64
        image = Image.new('RGB', (size, size), self.colors['accent'] if not self.is_dark else '#6C5CE7')
        draw = ImageDraw.Draw(image)
        
        # Рисуем букву J
        draw.text((size//2-10, size//2-10), "JR", fill='white', font=None)
        
        return image

    def setup_tray_icon(self):
        """Настройка иконки в системном трее"""
        try:
            menu = pystray.Menu(
                pystray.MenuItem("📨 Показать окно", self.show_window),
                pystray.MenuItem("▶ Запустить сервис", self.start_service_from_tray),
                pystray.MenuItem("⏹ Остановить сервис", self.stop_service_from_tray),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("❓ Помощь", self.show_help),
                pystray.MenuItem("🚪 Выход", self.exit_app)
            )
            
            self.tray_icon = pystray.Icon("jabber_robot", self.create_tray_image(), "Jabber Robot", menu)
            
            # Запускаем в отдельном потоке
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Ошибка создания иконки в трее: {e}")

    def show_help(self):
        """Показать справку"""
        help_text = """
        🤖 Jabber Robot - Помощь
        
        Горячие клавиши:
        Ctrl+Enter    - Отправить сообщение
        Ctrl+Shift+S  - Показать окно
        Ctrl+Shift+H  - Скрыть окно
        Ctrl+Shift+Q  - Выход
        Ctrl+R        - Обновить логи
        Ctrl+S        - Сохранить настройки
        
        Функции:
        • Автоматическая отправка сообщений из Oracle/REST
        • Windows Service для фоновой работы
        • Системный трей (сворачивается при закрытии)
        • Автовосстановление после сбоя
        • Светлая/темная тема
        • Автозагрузка с Windows
        """
        messagebox.showinfo("Помощь", help_text)

    def show_window(self):
        """Показать главное окно"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide_window(self):
        """Скрыть окно (свернуть в трей)"""
        self.root.withdraw()
        self.show_notification("Приложение свернуто в системный трей", "info")

    def exit_app(self):
        """Полный выход из приложения"""
        # Сохраняем состояние перед выходом
        if self.core and self.core.is_running:
            self.save_state_for_recovery()
        
        if self.core:
            self.core.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.quit()
        self.root.destroy()
        sys.exit(0)

    def start_service_from_tray(self):
        """Запуск сервиса из трея"""
        self.root.after(0, self.start_service)

    def stop_service_from_tray(self):
        """Остановка сервиса из трея"""
        self.root.after(0, self.stop_service)

    def load_auto_start_setting(self):
        """Загрузить настройку автозагрузки"""
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('auto_start', {}).get('enabled', False)
        except:
            return False

    def save_auto_start_setting(self):
        """Сохранить настройку автозагрузки"""
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        except:
            config = {}
        
        if 'auto_start' not in config:
            config['auto_start'] = {}
        config['auto_start']['enabled'] = self.auto_start
        
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)

    def setup_auto_start(self):
        """Настройка автозагрузки"""
        startup_path = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup',
            'JabberRobot.lnk'
        )
        
        if self.auto_start:
            try:
                python_path = sys.executable
                script_path = os.path.abspath(__file__)
                
                # Создаем VBS скрипт для скрытого запуска
                vbs_path = os.path.join(os.path.dirname(script_path), 'start_hidden.vbs')
                with open(vbs_path, 'w', encoding='utf-8') as f:
                    f.write(f'''CreateObject("WScript.Shell").Run "{python_path} {script_path}", 0, False''')
                
                # Создаем ярлык
                from win32com.client import Dispatch
                
                shell = Dispatch('WScript.Shell')
                shortcut = shell.CreateShortCut(startup_path)
                shortcut.Targetpath = vbs_path
                shortcut.WorkingDirectory = os.path.dirname(script_path)
                shortcut.Save()
                
                print("✅ Добавлено в автозагрузку")
            except Exception as e:
                print(f"Ошибка добавления в автозагрузку: {e}")
        else:
            try:
                if os.path.exists(startup_path):
                    os.remove(startup_path)
                print("✅ Удалено из автозагрузки")
            except Exception as e:
                print(f"Ошибка удаления из автозагрузки: {e}")

    def auto_start_service(self):
        """Автоматический запуск сервиса при старте"""
        try:
            if self.auto_start:
                self.start_service()
        except Exception as e:
            print(f"Ошибка автозапуска сервиса: {e}")

    def toggle_auto_start(self):
        """Переключить автозагрузку"""
        self.auto_start = not self.auto_start
        self.save_auto_start_setting()
        self.setup_auto_start()
        
        status = "включена" if self.auto_start else "выключена"
        self.show_notification(f"Автозагрузка {status}", "success")
        
        if self.menu_window and self.menu_window.winfo_exists():
            self.update_menu_text()

    def update_menu_text(self):
        """Обновить текст в меню"""
        if self.menu_window:
            self.menu_window.destroy()
            self.menu_window = None
            self.show_menu()

    def load_theme(self):
        """Загрузить сохраненную тему из конфига"""
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('theme', {}).get('dark', False)
        except:
            return False

    def save_theme(self):
        """Сохранить тему в конфиг"""
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
        except:
            config = {}
        
        if 'theme' not in config:
            config['theme'] = {}
        config['theme']['dark'] = self.is_dark
        
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)

    def set_theme(self, is_dark):
        """Установить цветовую схему"""
        if is_dark:
            self.colors = {
                'bg': '#1A1A2E',
                'sidebar': '#16213E',
                'card': '#0F3460',
                'message_bubble': '#1A2A4A',
                'accent': '#6C5CE7',
                'accent_hover': '#5F4FD6',
                'success': '#00B894',
                'success_hover': '#00A085',
                'danger': '#FF7675',
                'danger_hover': '#FF6B6B',
                'text': '#EEEEEE',
                'text_secondary': '#AAAAAA',
                'text_light': '#888888',
                'border': '#2D2D3A',
                'hover': '#2A2A3A',
                'input_bg': '#1E2A3A',
                'online': '#00B894',
                'offline': '#6C6C7A'
            }
        else:
            self.colors = {
                'bg': '#F5F7FA',
                'sidebar': '#FFFFFF',
                'card': '#FFFFFF',
                'message_bubble': '#E8F0FE',
                'accent': '#6C5CE7',
                'accent_hover': '#5F4FD6',
                'success': '#00B894',
                'success_hover': '#00A085',
                'danger': '#FF7675',
                'danger_hover': '#FF6B6B',
                'text': '#2D3436',
                'text_secondary': '#636E72',
                'text_light': '#B2BEC3',
                'border': '#DFE6E9',
                'hover': '#F8F9FA',
                'input_bg': '#F8F9FA',
                'online': '#00B894',
                'offline': '#B2BEC3'
            }

    def toggle_theme(self):

        self.is_dark = not self.is_dark
        self.set_theme(self.is_dark)
        self.save_theme()
    
        # Сохраняем текущую страницу
        current_page = None
        for name, page in self.pages.items():
            if page.winfo_ismapped():
               current_page = name
               break
    
        # Обновляем фон
        self.root.configure(bg=self.colors['bg'])
    
        # Сохраняем значения полей
        saved_values = {}
        if hasattr(self, 'xmpp_server'):
             saved_values['xmpp_server'] = self.xmpp_server.get()
        if hasattr(self, 'xmpp_username'):
            saved_values['xmpp_username'] = self.xmpp_username.get()
        if hasattr(self, 'xmpp_password'):
            saved_values['xmpp_password'] = self.xmpp_password.get()
        if hasattr(self, 'rest_url'):
            saved_values['rest_url'] = self.rest_url.get()
        if hasattr(self, 'rest_key'):
            saved_values['rest_key'] = self.rest_key.get()
        if hasattr(self, 'oracle_enabled'):
            saved_values['oracle_enabled'] = self.oracle_enabled.get()
        if hasattr(self, 'rest_enabled'):
            saved_values['rest_enabled'] = self.rest_enabled.get()
    
        # Удаляем все виджеты
        for widget in self.root.winfo_children():
            widget.destroy()
    
        # Пересоздаем интерфейс
        self.setup_ui()
    
        # Восстанавливаем значения полей
        if hasattr(self, 'xmpp_server') and 'xmpp_server' in saved_values:
            self.xmpp_server.delete(0, tk.END)
            self.xmpp_server.insert(0, saved_values['xmpp_server'])
        if hasattr(self, 'xmpp_username') and 'xmpp_username' in saved_values:
            self.xmpp_username.delete(0, tk.END)
            self.xmpp_username.insert(0, saved_values['xmpp_username'])
        if hasattr(self, 'xmpp_password') and 'xmpp_password' in saved_values:
            self.xmpp_password.delete(0, tk.END)
            self.xmpp_password.insert(0, saved_values['xmpp_password'])
        if hasattr(self, 'rest_url') and 'rest_url' in saved_values:
            self.rest_url.delete(0, tk.END)
            self.rest_url.insert(0, saved_values['rest_url'])
        if hasattr(self, 'rest_key') and 'rest_key' in saved_values:
            self.rest_key.delete(0, tk.END)
            self.rest_key.insert(0, saved_values['rest_key'])
        if hasattr(self, 'oracle_enabled') and 'oracle_enabled' in saved_values:
            self.oracle_enabled.set(saved_values['oracle_enabled'])
        if hasattr(self, 'rest_enabled') and 'rest_enabled' in saved_values:
            self.rest_enabled.set(saved_values['rest_enabled'])
    
        # Восстанавливаем страницу
        if current_page and current_page in self.pages:
            self.switch_page(current_page)
    
        # Пересоздаем привязку скролла
        self.setup_scroll_binding()
    
        # Обновляем иконку в трее
        if self.tray_icon:
            self.tray_icon.icon = self.create_tray_image()
    
        self.show_notification(f"Тема: {'🌙 Темная' if self.is_dark else '☀️ Светлая'}", "success")

    def setup_scroll_binding(self):
        """Настройка скролла колесиком мыши"""
        def on_mousewheel(event):
            widget = self.root.winfo_containing(event.x_root, event.y_root)
            while widget and widget != self.root:
                if isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
                    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    return
                elif isinstance(widget, tk.Canvas):
                    widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    return
                widget = widget.master
        self.root.bind_all('<MouseWheel>', on_mousewheel)

    def load_config(self):
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config is None:
                    config = {}
                config.setdefault('xmpp', {})
                config.setdefault('oracle', {})
                config.setdefault('rest', {})
                config['xmpp'].setdefault('server', 'localhost')
                config['xmpp'].setdefault('username', '')
                config['xmpp'].setdefault('password', '')
                config['oracle'].setdefault('enabled', True)
                config['rest'].setdefault('enabled', True)
                config['rest'].setdefault('api_url', 'http://localhost:5000')
                config['rest'].setdefault('api_key', '')
                return config
        except FileNotFoundError:
            return {
                'xmpp': {'server': 'localhost', 'username': '', 'password': ''},
                'oracle': {'enabled': True},
                'rest': {'enabled': True, 'api_url': 'http://localhost:5000', 'api_key': ''}
            }

    def save_config(self):
        config = {
            'xmpp': {
                'server': self.xmpp_server.get(),
                'username': self.xmpp_username.get(),
                'password': self.xmpp_password.get()
            },
            'oracle': {'enabled': self.oracle_enabled.get()},
            'rest': {
                'enabled': self.rest_enabled.get(),
                'api_url': self.rest_url.get(),
                'api_key': self.rest_key.get()
            }
        }
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
        self.show_notification("Настройки сохранены", "success")
        self.save_state_for_recovery()

    def show_notification(self, message, type="info"):
        """Показать всплывающее уведомление"""
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        bg_color = self.colors['success'] if type == "success" else self.colors['accent']
        notif.configure(bg=bg_color)
        x = self.root.winfo_x() + self.root.winfo_width() - 320
        y = self.root.winfo_y() + self.root.winfo_height() - 80
        notif.geometry(f"300x45+{x}+{y}")
        tk.Label(notif, text=message, bg=bg_color, fg='white',
                 font=('Segoe UI', 11), padx=15, pady=12).pack()
        notif.after(2000, notif.destroy)
        
        try:
            winsound.PlaySound("SystemAsterisk", winsound.SND_ASYNC)
        except:
            pass

    def toggle_menu(self):
        if self.menu_window and self.menu_window.winfo_exists():
            self.menu_window.destroy()
            self.menu_window = None
        else:
            self.show_menu()

    def show_menu(self):
        x = self.root.winfo_x() + 65
        y = self.root.winfo_y() + 55

        self.menu_window = tk.Toplevel(self.root)
        self.menu_window.overrideredirect(True)
        self.menu_window.configure(bg=self.colors['sidebar'], bd=1, relief='flat')
        self.menu_window.geometry(f"220x360+{x}+{y}")

        # Аватар
        avatar_frame = tk.Frame(self.menu_window, bg=self.colors['sidebar'], height=80)
        avatar_frame.pack(fill='x', padx=15, pady=(15, 10))

        avatar = tk.Canvas(avatar_frame, width=48, height=48,
                           bg='#E8F0FE', highlightthickness=0)
        avatar.pack(side='left')
        avatar.create_oval(4, 4, 44, 44, fill=self.colors['accent'], outline='')
        avatar.create_text(24, 24, text="JR", fill='white', font=('Segoe UI', 14, 'bold'))

        user_info = tk.Frame(avatar_frame, bg=self.colors['sidebar'])
        user_info.pack(side='left', padx=(12, 0))

        tk.Label(user_info, text="Jabber Robot",
                 font=('Segoe UI', 14, 'bold'),
                 bg=self.colors['sidebar'], fg=self.colors['text']).pack(anchor='w')

        self.menu_status = tk.Label(user_info, text="Готов к работе",
                                    font=('Segoe UI', 10),
                                    bg=self.colors['sidebar'], fg=self.colors['text_light'])
        self.menu_status.pack(anchor='w')

        separator = tk.Frame(self.menu_window, height=1, bg=self.colors['border'])
        separator.pack(fill='x', padx=15, pady=10)

        # Пункты меню
        menu_items = [
            ("⚙️ Настройки", "settings"),
            ("✉️ Отправить", "send"),
            ("📋 Логи", "logs"),
        ]

        for text, page in menu_items:
            btn = tk.Button(self.menu_window, text=text,
                            font=('Segoe UI', 12),
                            bg=self.colors['sidebar'], fg=self.colors['text'],
                            anchor='w', padx=15, pady=10,
                            bd=0, relief='flat',
                            cursor='hand2',
                            activebackground=self.colors['hover'])
            btn.pack(fill='x', padx=15, pady=2)
            btn.configure(command=lambda p=page: self.switch_page(p))

        separator2 = tk.Frame(self.menu_window, height=1, bg=self.colors['border'])
        separator2.pack(fill='x', padx=15, pady=10)

        # Кнопка переключения темы
        theme_text = "🌙 Темная тема" if not self.is_dark else "☀️ Светлая тема"
        theme_btn = tk.Button(self.menu_window, text=theme_text,
                              font=('Segoe UI', 12),
                              bg=self.colors['sidebar'], fg=self.colors['text'],
                              anchor='w', padx=15, pady=10,
                              bd=0, relief='flat',
                              cursor='hand2',
                              activebackground=self.colors['hover'],
                              command=self.toggle_theme)
        theme_btn.pack(fill='x', padx=15, pady=2)

        # Кнопка автозагрузки
        auto_text = "✅ Автозагрузка" if self.auto_start else "⬜ Автозагрузка"
        auto_btn = tk.Button(self.menu_window, text=auto_text,
                             font=('Segoe UI', 12),
                             bg=self.colors['sidebar'], fg=self.colors['text'],
                             anchor='w', padx=15, pady=10,
                             bd=0, relief='flat',
                             cursor='hand2',
                             activebackground=self.colors['hover'],
                             command=self.toggle_auto_start)
        auto_btn.pack(fill='x', padx=15, pady=2)

        # Версия внизу
        version_frame = tk.Frame(self.menu_window, bg=self.colors['sidebar'])
        version_frame.pack(side='bottom', fill='x', pady=15)
        tk.Label(version_frame, text="Версия 3.0 · 2026",
                 bg=self.colors['sidebar'], fg=self.colors['text_light'],
                 font=('Segoe UI', 10)).pack()

        def close_menu(event):
            if event.widget != self.menu_window and event.widget != self.menu_btn:
                self.menu_window.destroy()
                self.menu_window = None
                self.root.unbind('<Button-1>')

        self.root.bind('<Button-1>', close_menu)

    def switch_page(self, page_name):
        for name, page in self.pages.items():
            page.pack_forget()
        self.pages[page_name].pack(fill='both', expand=True)
        if self.menu_window:
            self.menu_window.destroy()
            self.menu_window = None

    def setup_ui(self):
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True)

        # Верхняя панель
        top_bar = tk.Frame(main_container, bg=self.colors['bg'], height=70)
        top_bar.pack(fill='x')
        top_bar.pack_propagate(False)

        # Кнопка меню
        self.menu_btn = tk.Button(top_bar, text="☰", font=('Segoe UI', 22),
                                  bg=self.colors['bg'], fg=self.colors['text'],
                                  bd=0, cursor='hand2', relief='flat',
                                  activebackground=self.colors['hover'])
        self.menu_btn.pack(side='left', padx=(25, 0), pady=15)
        self.menu_btn.configure(command=self.toggle_menu)

        # Заголовок
        tk.Label(top_bar, text="Jabber Robot",
                 font=('Segoe UI', 22, 'bold'),
                 bg=self.colors['bg'], fg=self.colors['text']).pack(side='left', padx=(15, 0))

        # Кнопка переключения темы
        theme_icon = "🌙" if not self.is_dark else "☀️"
        theme_btn = tk.Button(top_bar, text=theme_icon, font=('Segoe UI', 16),
                              bg=self.colors['bg'], fg=self.colors['text'],
                              bd=0, cursor='hand2', relief='flat',
                              activebackground=self.colors['hover'],
                              command=self.toggle_theme)
        theme_btn.pack(side='right', padx=(0, 10), pady=15)

        # Статус и кнопки справа
        right_frame = tk.Frame(top_bar, bg=self.colors['bg'])
        right_frame.pack(side='right', padx=25, pady=12)

        self.status_dot = tk.Canvas(right_frame, width=8, height=8,
                                    bg=self.colors['bg'], highlightthickness=0)
        self.status_dot.pack(side='left')
        self.status_circle = self.status_dot.create_oval(2, 2, 6, 6, fill=self.colors['offline'])

        self.status_text = tk.Label(right_frame, text="Сервис остановлен",
                                    bg=self.colors['bg'], fg=self.colors['text_secondary'],
                                    font=('Segoe UI', 11))
        self.status_text.pack(side='left', padx=(8, 15))

        self.start_btn = RoundedButton(right_frame, "Запустить", self.start_service,
                                       self.colors['success'], self.colors['success_hover'],
                                       width=100, height=32)
        self.start_btn.pack(side='left', padx=5)

        self.stop_btn = RoundedButton(right_frame, "Остановить", self.stop_service,
                                      self.colors['danger'], self.colors['danger_hover'],
                                      width=100, height=32)
        self.stop_btn.pack(side='left', padx=5)
        self.stop_btn.config(state='disabled')

        # Основная область
        self.content_area = tk.Frame(main_container, bg=self.colors['bg'])
        self.content_area.pack(fill='both', expand=True, padx=30, pady=20)

        # Страницы
        self.pages = {}

        settings_page = tk.Frame(self.content_area, bg=self.colors['bg'])
        self.pages['settings'] = settings_page
        self.setup_settings_page(settings_page)

        send_page = tk.Frame(self.content_area, bg=self.colors['bg'])
        self.pages['send'] = send_page
        self.setup_send_page(send_page)

        logs_page = tk.Frame(self.content_area, bg=self.colors['bg'])
        self.pages['logs'] = logs_page
        self.setup_logs_page(logs_page)

        self.pages['settings'].pack(fill='both', expand=True)

    def setup_settings_page(self, parent):
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # XMPP карточка
        xmpp_card = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='flat')
        xmpp_card.pack(fill='x', pady=10)

        header_frame = tk.Frame(xmpp_card, bg=self.colors['card'])
        header_frame.pack(fill='x', padx=25, pady=(25, 15))

        tk.Label(header_frame, text="XMPP Сервер",
                 font=('Segoe UI', 18, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text']).pack(side='left')

        fields_frame = tk.Frame(xmpp_card, bg=self.colors['card'])
        fields_frame.pack(fill='x', padx=25, pady=(0, 25))

        # Скругленные поля
        tk.Label(fields_frame, text="Сервер", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w')
        self.xmpp_server = RoundedEntry(fields_frame)
        self.xmpp_server.entry.config(font=('Segoe UI', 11), bg=self.colors['input_bg'], relief='flat', bd=0)
        self.xmpp_server.update_bg(self.colors['input_bg'])
        self.xmpp_server.pack(fill='x', pady=(5, 15))
        self.xmpp_server.insert(0, self.config['xmpp'].get('server', 'localhost'))

        tk.Label(fields_frame, text="JID (логин)", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w')
        self.xmpp_username = RoundedEntry(fields_frame)
        self.xmpp_username.entry.config(font=('Segoe UI', 11), bg=self.colors['input_bg'], relief='flat', bd=0)
        self.xmpp_username.update_bg(self.colors['input_bg'])
        self.xmpp_username.pack(fill='x', pady=(5, 15))
        self.xmpp_username.insert(0, self.config['xmpp'].get('username', ''))

        tk.Label(fields_frame, text="Пароль", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w')
        self.xmpp_password = RoundedEntry(fields_frame)
        self.xmpp_password.entry.config(font=('Segoe UI', 11), bg=self.colors['input_bg'], relief='flat', bd=0, show="•")
        self.xmpp_password.update_bg(self.colors['input_bg'])
        self.xmpp_password.pack(fill='x', pady=(5, 0))
        self.xmpp_password.insert(0, self.config['xmpp'].get('password', ''))

        # Источники карточка
        sources_card = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='flat')
        sources_card.pack(fill='x', pady=10)

        sources_header = tk.Frame(sources_card, bg=self.colors['card'])
        sources_header.pack(fill='x', padx=25, pady=(25, 15))

        tk.Label(sources_header, text="Источники сообщений",
                 font=('Segoe UI', 18, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text']).pack(side='left')

        sources_inner = tk.Frame(sources_card, bg=self.colors['card'])
        sources_inner.pack(fill='x', padx=25, pady=(0, 20))

        self.oracle_enabled = tk.BooleanVar(value=self.config['oracle'].get('enabled', True))
        oracle_cb = tk.Checkbutton(sources_inner, text="Oracle Database",
                                   variable=self.oracle_enabled,
                                   bg=self.colors['card'], fg=self.colors['text'],
                                   selectcolor=self.colors['card'],
                                   font=('Segoe UI', 12))
        oracle_cb.pack(anchor='w', pady=8)

        self.rest_enabled = tk.BooleanVar(value=self.config['rest'].get('enabled', True))
        rest_cb = tk.Checkbutton(sources_inner, text="REST API",
                                 variable=self.rest_enabled,
                                 bg=self.colors['card'], fg=self.colors['text'],
                                 selectcolor=self.colors['card'],
                                 font=('Segoe UI', 12))
        rest_cb.pack(anchor='w', pady=8)

        # REST поля
        rest_frame = tk.Frame(sources_inner, bg=self.colors['card'])
        rest_frame.pack(fill='x', pady=(15, 0))

        tk.Label(rest_frame, text="REST API URL", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w')
        self.rest_url = RoundedEntry(rest_frame)
        self.rest_url.entry.config(font=('Segoe UI', 11), bg=self.colors['input_bg'], relief='flat', bd=0)
        self.rest_url.update_bg(self.colors['input_bg'])
        self.rest_url.pack(fill='x', pady=(5, 10))
        self.rest_url.insert(0, self.config['rest'].get('api_url', 'http://localhost:5000'))

        tk.Label(rest_frame, text="API Key", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w')
        self.rest_key = RoundedEntry(rest_frame)
        self.rest_key.entry.config(font=('Segoe UI', 11), bg=self.colors['input_bg'], relief='flat', bd=0)
        self.rest_key.update_bg(self.colors['input_bg'])
        self.rest_key.pack(fill='x', pady=(5, 0))
        self.rest_key.insert(0, self.config['rest'].get('api_key', ''))

        # Кнопка сохранения
        save_btn = RoundedButton(sources_card, "Сохранить настройки", self.save_config,
                                 self.colors['accent'], self.colors['accent_hover'],
                                 width=150, height=36)
        save_btn.pack(pady=(20, 30))

    def setup_send_page(self, parent):
        canvas = tk.Canvas(parent, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(scrollable_frame, text="Новое сообщение",
                 font=('Segoe UI', 24, 'bold'),
                 bg=self.colors['bg'], fg=self.colors['text']).pack(anchor='w', pady=(0, 20))

        send_card = tk.Frame(scrollable_frame, bg=self.colors['card'], relief='flat')
        send_card.pack(fill='both', expand=True)

        fields_frame = tk.Frame(send_card, bg=self.colors['card'])
        fields_frame.pack(fill='x', padx=25, pady=(25, 15))

        tk.Label(fields_frame, text="Кому", font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w')
        self.send_recipient = RoundedEntry(fields_frame)
        self.send_recipient.entry.config(font=('Segoe UI', 12), bg=self.colors['input_bg'], relief='flat', bd=0)
        self.send_recipient.update_bg(self.colors['input_bg'])
        self.send_recipient.pack(fill='x', pady=(5, 15))
        self.send_recipient.insert(0, "user@jabber.local")

        tk.Label(fields_frame, text="Тема", font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w')
        self.send_subject = RoundedEntry(fields_frame)
        self.send_subject.entry.config(font=('Segoe UI', 12), bg=self.colors['input_bg'], relief='flat', bd=0)
        self.send_subject.update_bg(self.colors['input_bg'])
        self.send_subject.pack(fill='x', pady=(5, 15))

        tk.Label(fields_frame, text="Сообщение", font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w')

        self.send_text = tk.Text(fields_frame, height=8, font=('Segoe UI', 12),
                                 bg=self.colors['message_bubble'], fg=self.colors['text'],
                                 insertbackground=self.colors['accent'],
                                 relief='flat', borderwidth=0, padx=15, pady=15)
        self.send_text.pack(fill='x', pady=(5, 5))

        self.char_counter = tk.Label(fields_frame, text="0 / 256 символов",
                                     bg=self.colors['card'], fg=self.colors['text_light'],
                                     font=('Segoe UI', 10))
        self.char_counter.pack(anchor='e', pady=(5, 10))
        self.send_text.bind('<KeyRelease>', self.update_char_counter)

        self.send_btn = RoundedButton(fields_frame, "Отправить сообщение", self.send_message_from_gui,
                                      self.colors['accent'], self.colors['accent_hover'],
                                      width=160, height=38)
        self.send_btn.pack(pady=10)

        self.send_status = tk.Label(fields_frame, text="", bg=self.colors['card'],
                                    fg=self.colors['accent'], font=('Segoe UI', 11))
        self.send_status.pack(pady=5)

        # Быстрые ответы
        quick_frame = tk.Frame(send_card, bg=self.colors['card'])
        quick_frame.pack(fill='x', padx=25, pady=(0, 25))

        tk.Label(quick_frame, text="Быстрые ответы",
                 font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['card'], fg=self.colors['text_secondary']).pack(anchor='w', pady=(0, 10))

        quick_buttons = tk.Frame(quick_frame, bg=self.colors['card'])
        quick_buttons.pack(fill='x')

        templates = [("👋 Привет", "Привет! Как дела?"), ("📅 Встреча", "Напоминаю о встрече в 15:00"),
                     ("📊 Отчет", "Отчет готов"), ("✅ Готово", "Задача выполнена")]

        for i, (name, text) in enumerate(templates):
            btn = tk.Button(quick_buttons, text=name, command=lambda t=text: self.insert_template(t),
                            bg=self.colors['bg'], fg=self.colors['accent'], font=('Segoe UI', 10),
                            padx=15, pady=5, bd=1, relief='flat', cursor='hand2')
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky='ew')
        quick_buttons.columnconfigure(0, weight=1)
        quick_buttons.columnconfigure(1, weight=1)

    def setup_logs_page(self, parent):
        """Страница логов с поиском и экспортом"""
        # Заголовок
        tk.Label(parent, text="История сообщений",
                 font=('Segoe UI', 24, 'bold'),
                 bg=self.colors['bg'], fg=self.colors['text']).pack(anchor='w', pady=(0, 15))

        # Панель инструментов
        toolbar = tk.Frame(parent, bg=self.colors['bg'])
        toolbar.pack(fill='x', pady=(0, 10))

        # Кнопка обновления
        refresh_btn = RoundedButton(toolbar, "🔄 Обновить", self.refresh_logs,
                                    self.colors['accent'], self.colors['accent_hover'],
                                    width=100, height=32)
        refresh_btn.pack(side='left', padx=5)

        # Кнопка экспорта в Excel
        export_btn = RoundedButton(toolbar, "📊 Экспорт в Excel", self.export_logs_to_excel,
                                   self.colors['success'], self.colors['success_hover'],
                                   width=140, height=32)
        export_btn.pack(side='left', padx=5)

        # Панель поиска
        self.setup_log_search(parent)

        # Текстовое поле для логов
        logs_frame = tk.Frame(parent, bg=self.colors['card'], relief='flat')
        logs_frame.pack(fill='both', expand=True)

        self.log_text = tk.Text(logs_frame, wrap=tk.WORD, font=('Consolas', 11),
                                bg=self.colors['card'], fg=self.colors['text'],
                                insertbackground=self.colors['accent'],
                                relief='flat', borderwidth=0, padx=20, pady=20)
        self.log_text.pack(fill='both', expand=True, side='left')

        # Скроллбар
        scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def setup_log_search(self, parent):
        """Добавить поле поиска в логах"""
        search_frame = tk.Frame(parent, bg=self.colors['bg'])
        search_frame.pack(fill='x', padx=15, pady=(10, 5))

        # Иконка поиска
        search_icon = tk.Label(search_frame, text="🔍",
                               bg=self.colors['bg'], fg=self.colors['text_secondary'],
                               font=('Segoe UI', 12))
        search_icon.pack(side='left')

        # Поле ввода поиска
        self.search_entry = tk.Entry(search_frame, font=('Segoe UI', 11),
                                     bg=self.colors['input_bg'], fg=self.colors['text'],
                                     relief='flat', bd=1)
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        self.search_entry.bind('<KeyRelease>', self.search_logs)

        # Кнопка очистки
        clear_btn = tk.Button(search_frame, text="✖",
                              font=('Segoe UI', 10),
                              bg=self.colors['bg'], fg=self.colors['text_secondary'],
                              bd=0, cursor='hand2',
                              command=self.clear_search)
        clear_btn.pack(side='left', padx=(5, 0))

        # Метка с количеством найденных
        self.search_count_label = tk.Label(search_frame, text="",
                                           bg=self.colors['bg'], fg=self.colors['accent'],
                                           font=('Segoe UI', 10))
        self.search_count_label.pack(side='left', padx=(10, 0))

    def search_logs(self, event=None):
        """Поиск по логам"""
        if not hasattr(self, 'search_entry'):
            return

        query = self.search_entry.get().strip().lower()

        if not hasattr(self, 'logger'):
            return

        if not query:
            self.refresh_logs()
            if hasattr(self, 'search_count_label'):
                self.search_count_label.config(text="")
            return

        logs = self.logger.get_logs()
        found_count = 0
        self.log_text.delete(1.0, tk.END)

        for log in reversed(logs[-500:]):
            text_match = query in log.text.lower()
            sender_match = query in log.sender.lower()
            recipient_match = query in log.recipient.lower()
            type_match = query in log.message_type.lower()

            if text_match or sender_match or recipient_match or type_match:
                found_count += 1
                status = "✓" if log.sent_time else "⏳"
                time_str = log.created_at.strftime('%H:%M:%S') if log.created_at else '--:--:--'

                display_text = f"[{time_str}] {status} {log.message_type}: {log.sender} → {log.recipient}\n"
                display_text += f"   📝 {log.text}\n\n"

                self.log_text.insert(tk.END, display_text)

        if hasattr(self, 'search_count_label'):
            self.search_count_label.config(text=f"Найдено: {found_count}")

    def clear_search(self):
        """Очистить поиск"""
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, tk.END)
        self.refresh_logs()
        if hasattr(self, 'search_count_label'):
            self.search_count_label.config(text="")

    def export_logs_to_excel(self):
        """Экспорт логов в Excel файл"""
        if not hasattr(self, 'logger'):
            self.show_notification("Нет данных для экспорта", "warning")
            return

        logs = self.logger.get_logs()

        if not logs:
            self.show_notification("Нет сообщений для экспорта", "warning")
            return

        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"jabber_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )

        if not filename:
            return

        try:
            data = []
            for log in logs:
                data.append({
                    'ID': log.id,
                    'Тип': log.message_type,
                    'Отправитель': log.sender,
                    'Получатель': log.recipient,
                    'Сообщение': log.text,
                    'Создано': log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else '',
                    'Отправлено': log.sent_time.strftime('%Y-%m-%d %H:%M:%S') if log.sent_time else '',
                    'Доставлено': log.delivered_time.strftime('%Y-%m-%d %H:%M:%S') if log.delivered_time else '',
                    'Прочитано': log.read_time.strftime('%Y-%m-%d %H:%M:%S') if log.read_time else ''
                })

            df = pd.DataFrame(data)

            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Логи', index=False)

                worksheet = writer.sheets['Логи']

                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width

                from openpyxl.styles import Font
                for cell in worksheet[1]:
                    cell.font = Font(bold=True)

            self.show_notification(f"Экспортировано в {filename}", "success")

        except Exception as e:
            self.show_notification(f"Ошибка экспорта: {e}", "warning")

    def update_char_counter(self, event=None):
        text = self.send_text.get("1.0", tk.END).strip()
        count = len(text)
        self.char_counter.config(text=f"{count} / 256 символов")
        if count > 256:
            self.char_counter.config(fg='red')
        else:
            self.char_counter.config(fg=self.colors['text_light'])

    def insert_template(self, text):
        self.send_text.delete("1.0", tk.END)
        self.send_text.insert("1.0", text)
        self.update_char_counter()

    def send_message_from_gui(self):
        recipient = self.send_recipient.get().strip()
        subject = self.send_subject.get().strip()
        text = self.send_text.get("1.0", tk.END).strip()

        if not recipient or not text:
            self.show_notification("Заполните получателя и сообщение", "warning")
            return

        if len(text) > 256:
            self.show_notification("Сообщение превышает 256 символов", "warning")
            return

        full_text = f"[{subject}]\n{text}" if subject else text

        self.send_btn.config(state='disabled')
        self.send_status.config(text="Отправка...")

        def send():
            try:
                response = requests.post('http://localhost:5000/api/send',
                                         json={'recipient': recipient, 'message': full_text, 'sender': 'gui_user'},
                                         timeout=10)
                if response.status_code == 200:
                    self.root.after(0, self.on_send_success)
                else:
                    self.root.after(0, lambda: self.on_send_error(response.json().get('error', 'Unknown error')))
            except requests.exceptions.ConnectionError:
                self.root.after(0, lambda: self.on_send_error("API сервер не запущен"))
            except Exception as e:
                self.root.after(0, lambda: self.on_send_error(str(e)))

        threading.Thread(target=send, daemon=True).start()

    def on_send_success(self):
        self.send_btn.config(state='normal')
        self.send_status.config(text="✓ Сообщение отправлено!")
        self.send_text.delete("1.0", tk.END)
        self.send_subject.delete(0, tk.END)
        self.update_char_counter()
        self.show_notification("Сообщение отправлено", "success")
        self.root.after(3000, lambda: self.send_status.config(text=""))

    def on_send_error(self, error):
        self.send_btn.config(state='normal')
        self.send_status.config(text=f"✗ {error}")
        self.show_notification(error, "warning")
        self.root.after(5000, lambda: self.send_status.config(text=""))

    def refresh_logs(self):
        if hasattr(self, 'logger'):
            self.log_text.delete(1.0, tk.END)
            for log in reversed(self.logger.get_logs()[-50:]):
                status = "✓" if log.sent_time else "⏳"
                time_str = log.created_at.strftime('%H:%M') if log.created_at else '--:--'
                self.log_text.insert(tk.END,
                                     f"[{time_str}] {status} {log.message_type}: {log.sender} → {log.recipient}\n   {log.text[:100]}\n\n")

    def start_service(self):
        try:
            sources = []
            if self.oracle_enabled.get():
                sources.append(OracleSource())
            if self.rest_enabled.get():
                sources.append(RestSource(api_url=self.rest_url.get(), api_key=self.rest_key.get()))
            sender = RealXmppSender(server=self.xmpp_server.get(), username=self.xmpp_username.get(),
                                password=self.xmpp_password.get())
            self.logger = FileLogger()
            self.core = MessagingCore(sources, sender, self.logger)
            self.core_thread = threading.Thread(target=self.core.start)
            self.core_thread.daemon = True
            self.core_thread.start()

            self.status_text.config(text="Сервис запущен")
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_dot.itemconfig(self.status_circle, fill=self.colors['online'])
            if self.menu_window and self.menu_window.winfo_exists():
                self.menu_status.config(text="Работает", fg=self.colors['online'])
            self.show_notification("Сервис запущен", "success")
            self.save_state_for_recovery()
        except Exception as e:
            self.show_notification(f"Ошибка: {e}", "warning")

    def stop_service(self):
        if self.core:
            self.core.stop()
            self.core = None
        self.status_text.config(text="Сервис остановлен")
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_dot.itemconfig(self.status_circle, fill=self.colors['offline'])
        if self.menu_window and self.menu_window.winfo_exists():
            self.menu_status.config(text="Остановлен", fg=self.colors['offline'])
        self.show_notification("Сервис остановлен", "success")
        self.save_state_for_recovery()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Показываем splash screen
    splash = SplashScreen()
    splash.update_status("Загрузка модулей...")
    import time
    time.sleep(0.5)
    
    splash.update_status("Проверка конфигурации...")
    time.sleep(0.5)
    
    splash.update_status("Загрузка интерфейса...")
    
    # Создаем главное окно
    app = MainWindow()
    
    splash.update_status("Готово!")
    time.sleep(0.3)
    splash.close()
    
    app.run()