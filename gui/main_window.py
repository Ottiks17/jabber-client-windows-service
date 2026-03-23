import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import yaml
import threading
from datetime import datetime
from api.core import MessagingCore
from sources.oracle_source import OracleSource
from sources.rest_source import RestSource
from sender.xmpp_sender import XmppSender
from api.logger import FileLogger

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jabber Client")
        self.root.geometry("800x600")
        
        self.core = None
        self.config = self.load_config()
        
        self.setup_ui()
        
    def load_config(self):
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                # Проверяем и заполняем отсутствующие значения
                if config is None:
                    config = {}
                if 'xmpp' not in config or config['xmpp'] is None:
                    config['xmpp'] = {}
                if 'server' not in config['xmpp']:
                    config['xmpp']['server'] = 'localhost'
                if 'username' not in config['xmpp']:
                    config['xmpp']['username'] = ''
                if 'password' not in config['xmpp']:
                    config['xmpp']['password'] = ''
                    
                if 'oracle' not in config or config['oracle'] is None:
                    config['oracle'] = {}
                if 'enabled' not in config['oracle']:
                    config['oracle']['enabled'] = True
                    
                if 'rest' not in config or config['rest'] is None:
                    config['rest'] = {}
                if 'enabled' not in config['rest']:
                    config['rest']['enabled'] = True
                if 'api_url' not in config['rest']:
                    config['rest']['api_url'] = 'http://localhost:5000'
                if 'api_key' not in config['rest']:
                    config['rest']['api_key'] = ''
                    
                return config
        except FileNotFoundError:
            # Возвращаем конфиг по умолчанию
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
            'oracle': {
                'enabled': self.oracle_enabled.get()
            },
            'rest': {
                'enabled': self.rest_enabled.get(),
                'api_url': self.rest_url.get(),
                'api_key': self.rest_key.get()
            }
        }
        
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
            
        messagebox.showinfo("Успех", "Конфигурация сохранена")
        
    def setup_ui(self):
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Вкладка настроек
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Настройки")
        self.setup_settings_tab(settings_frame)
        
        # Вкладка логов
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Логи")
        self.setup_logs_tab(logs_frame)
        
        # Панель управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="Запустить сервис", command=self.start_service)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Остановить сервис", command=self.stop_service, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Статус: Остановлен")
        self.status_label.pack(side='right', padx=5)
        
    def setup_settings_tab(self, parent):
        # XMPP настройки
        xmpp_frame = ttk.LabelFrame(parent, text="XMPP настройки", padding=10)
        xmpp_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(xmpp_frame, text="Сервер:").grid(row=0, column=0, sticky='w')
        self.xmpp_server = ttk.Entry(xmpp_frame, width=30)
        self.xmpp_server.insert(0, self.config['xmpp'].get('server', 'localhost'))
        self.xmpp_server.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(xmpp_frame, text="Имя пользователя:").grid(row=1, column=0, sticky='w')
        self.xmpp_username = ttk.Entry(xmpp_frame, width=30)
        self.xmpp_username.insert(0, self.config['xmpp'].get('username', ''))
        self.xmpp_username.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(xmpp_frame, text="Пароль:").grid(row=2, column=0, sticky='w')
        self.xmpp_password = ttk.Entry(xmpp_frame, width=30, show="*")
        self.xmpp_password.insert(0, self.config['xmpp'].get('password', ''))
        self.xmpp_password.grid(row=2, column=1, padx=5, pady=2)
        
        # Источники сообщений
        sources_frame = ttk.LabelFrame(parent, text="Источники сообщений", padding=10)
        sources_frame.pack(fill='x', padx=5, pady=5)
        
        self.oracle_enabled = tk.BooleanVar(value=self.config['oracle'].get('enabled', True))
        ttk.Checkbutton(sources_frame, text="Oracle БД", variable=self.oracle_enabled).pack(anchor='w')
        
        self.rest_enabled = tk.BooleanVar(value=self.config['rest'].get('enabled', True))
        ttk.Checkbutton(sources_frame, text="REST API", variable=self.rest_enabled).pack(anchor='w')
        
        ttk.Label(sources_frame, text="REST URL:").pack(anchor='w')
        self.rest_url = ttk.Entry(sources_frame, width=50)
        self.rest_url.insert(0, self.config['rest'].get('api_url', 'http://localhost:5000'))
        self.rest_url.pack(fill='x', padx=20, pady=2)
        
        ttk.Label(sources_frame, text="REST API Key:").pack(anchor='w')
        self.rest_key = ttk.Entry(sources_frame, width=50)
        self.rest_key.insert(0, self.config['rest'].get('api_key', ''))
        self.rest_key.pack(fill='x', padx=20, pady=2)
        
        # Кнопка сохранения
        ttk.Button(parent, text="Сохранить настройки", command=self.save_config).pack(pady=10)
        
    def setup_logs_tab(self, parent):
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, height=20)
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        ttk.Button(parent, text="Обновить логи", command=self.refresh_logs).pack(pady=5)
        
    def refresh_logs(self):
        if hasattr(self, 'logger'):
            self.log_text.delete(1.0, tk.END)
            for log in self.logger.get_logs():
                self.log_text.insert(tk.END, 
                    f"[{log.created_at}] {log.message_type}: {log.sender} -> {log.recipient}\n"
                    f"    Текст: {log.text}\n"
                    f"    Отправлено: {log.sent_time}\n"
                    f"    Доставлено: {log.delivered_time}\n"
                    f"    Прочитано: {log.read_time}\n"
                    f"{'-'*50}\n"
                )
                
    def start_service(self):
        try:
            sources = []
            
            if self.oracle_enabled.get():
                sources.append(OracleSource())
                
            if self.rest_enabled.get():
                sources.append(RestSource(
                    api_url=self.rest_url.get(),
                    api_key=self.rest_key.get()
                ))
                
            sender = XmppSender(
                server=self.xmpp_server.get(),
                username=self.xmpp_username.get(),
                password=self.xmpp_password.get()
            )
            
            self.logger = FileLogger()
            
            self.core = MessagingCore(sources, sender, self.logger)
            
            self.core_thread = threading.Thread(target=self.core.start)
            self.core_thread.daemon = True
            self.core_thread.start()
            
            self.status_label.config(text="Статус: Запущен")
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            
            messagebox.showinfo("Успех", "Сервис запущен")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить сервис: {e}")
            
    def stop_service(self):
        if self.core:
            self.core.stop()
            self.core = None
            
        self.status_label.config(text="Статус: Остановлен")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        messagebox.showinfo("Успех", "Сервис остановлен")
        
    def run(self):
        self.root.mainloop()
