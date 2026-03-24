import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import yaml
import threading
import requests
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
        self.root.geometry("900x700")
        
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
        
        # Вкладка отправки (НОВАЯ!)
        send_frame = ttk.Frame(notebook)
        notebook.add(send_frame, text="Отправить")
        self.setup_send_tab(send_frame)
        
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
        
    def setup_send_tab(self, parent):
        """Вкладка для отправки сообщений"""
        
        # Основной фрейм с прокруткой
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Заголовок
        title_label = ttk.Label(scrollable_frame, text="📤 Отправить сообщение", 
                                font=('Arial', 14, 'bold'))
        title_label.pack(pady=(20, 10))
        
        # Поле "Кому"
        recipient_frame = ttk.Frame(scrollable_frame)
        recipient_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(recipient_frame, text="Кому (JID):", width=15, font=('Arial', 10, 'bold')).pack(side='left')
        self.send_recipient = ttk.Entry(recipient_frame, width=50, font=('Arial', 10))
        self.send_recipient.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Пример
        example_frame = ttk.Frame(scrollable_frame)
        example_frame.pack(fill='x', padx=20, pady=(0, 5))
        ttk.Label(example_frame, text="Пример: user@jabber.local", foreground='gray').pack(side='right')
        
        # Поле "Тема" (опционально)
        subject_frame = ttk.Frame(scrollable_frame)
        subject_frame.pack(fill='x', padx=20, pady=5)
        
        ttk.Label(subject_frame, text="Тема:", width=15, font=('Arial', 10, 'bold')).pack(side='left')
        self.send_subject = ttk.Entry(subject_frame, width=50, font=('Arial', 10))
        self.send_subject.pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # Поле "Сообщение"
        message_frame = ttk.LabelFrame(scrollable_frame, text="Сообщение", padding=10)
        message_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.send_text = tk.Text(message_frame, height=8, width=60, 
                                  wrap=tk.WORD, font=('Arial', 10))
        self.send_text.pack(fill='both', expand=True)
        
        # Счетчик символов
        char_frame = ttk.Frame(message_frame)
        char_frame.pack(fill='x', pady=(5, 0))
        
        self.char_counter = ttk.Label(char_frame, text="0 / 256 символов", 
                                       foreground='gray')
        self.char_counter.pack(side='right')
        
        # Привязываем событие для подсчета символов
        self.send_text.bind('<KeyRelease>', self.update_char_counter)
        
        # Кнопка отправки
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=15)
        
        self.send_button = ttk.Button(button_frame, text="📨 Отправить сообщение", 
                                       command=self.send_message_from_gui,
                                       width=30)
        self.send_button.pack()
        
        # Статус отправки
        self.send_status = ttk.Label(scrollable_frame, text="", foreground='green', font=('Arial', 10))
        self.send_status.pack(pady=5)
        
        # Раздел с быстрыми шаблонами
        templates_frame = ttk.LabelFrame(scrollable_frame, text="Быстрые шаблоны", padding="10")
        templates_frame.pack(fill='x', padx=20, pady=10)
        
        templates = [
            ("Привет! Как дела?", "Привет! Как дела?"),
            ("Совещание в 15:00", "Напоминаю, что совещание сегодня в 15:00"),
            ("Отчет готов", "Отчет по проекту готов. Можете посмотреть в папке."),
            ("Тестовое сообщение", "Это тестовое сообщение из Jabber клиента")
        ]
        
        for i, (name, text) in enumerate(templates):
            btn = ttk.Button(templates_frame, text=name, 
                             command=lambda t=text: self.insert_template(t))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
        
        templates_frame.columnconfigure(0, weight=1)
        templates_frame.columnconfigure(1, weight=1)
        
        # Информация
        info_frame = ttk.LabelFrame(scrollable_frame, text="Информация", padding="10")
        info_frame.pack(fill='x', padx=20, pady=10)
        
        info_text = "💡 Совет: Сообщение будет отправлено через XMPP получателю.\n" \
                    "   Убедитесь, что API сервер запущен (python api_server.py).\n" \
                    "   Максимальная длина сообщения: 256 символов."
        
        info_label = ttk.Label(info_frame, text=info_text, foreground='gray', justify='left')
        info_label.pack()
        
    def update_char_counter(self, event=None):
        """Обновление счетчика символов"""
        text = self.send_text.get("1.0", tk.END).strip()
        count = len(text)
        self.char_counter.config(text=f"{count} / 256 символов")
        
        if count > 256:
            self.char_counter.config(foreground='red')
        else:
            self.char_counter.config(foreground='gray')

    def insert_template(self, text):
        """Вставить шаблон в поле сообщения"""
        self.send_text.delete("1.0", tk.END)
        self.send_text.insert("1.0", text)
        self.update_char_counter()

    def send_message_from_gui(self):
        """Отправить сообщение из GUI через API"""
        recipient = self.send_recipient.get().strip()
        subject = self.send_subject.get().strip()
        text = self.send_text.get("1.0", tk.END).strip()
        
        # Проверка получателя
        if not recipient:
            messagebox.showwarning("Ошибка", "Введите получателя (JID)")
            return
        
        # Проверка сообщения
        if not text:
            messagebox.showwarning("Ошибка", "Введите текст сообщения")
            return
        
        # Проверка длины
        if len(text) > 256:
            messagebox.showwarning("Ошибка", f"Сообщение превышает 256 символов (сейчас {len(text)})")
            return
        
        # Добавляем тему если есть
        if subject:
            full_text = f"[{subject}]\n{text}"
        else:
            full_text = text
        
        # Отключаем кнопку на время отправки
        self.send_button.config(state='disabled', text="⏳ Отправка...")
        self.send_status.config(text="Отправка...", foreground='orange')
        
        try:
            def send():
                try:
                    response = requests.post(
                        'http://localhost:5000/api/send',
                        json={
                            'recipient': recipient,
                            'message': full_text,
                            'sender': 'gui_user'
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        self.root.after(0, lambda: self.on_send_success(result))
                    else:
                        error = response.json().get('error', 'Unknown error')
                        self.root.after(0, lambda: self.on_send_error(error))
                        
                except requests.exceptions.ConnectionError:
                    self.root.after(0, lambda: self.on_send_error("API сервер не запущен! Запустите: python api_server.py"))
                except requests.exceptions.Timeout:
                    self.root.after(0, lambda: self.on_send_error("Превышено время ожидания ответа от сервера"))
                except Exception as e:
                    self.root.after(0, lambda: self.on_send_error(str(e)))
            
            # Запускаем в отдельном потоке
            thread = threading.Thread(target=send)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.on_send_error(str(e))

    def on_send_success(self, result):
        """Обработка успешной отправки"""
        self.send_button.config(state='normal', text="📨 Отправить сообщение")
        self.send_status.config(
            text=f"✅ Сообщение отправлено! ID: {result.get('message_id', 'unknown')[:8]}...",
            foreground='green'
        )
        
        # Очищаем поле сообщения и тему
        self.send_text.delete("1.0", tk.END)
        self.send_subject.delete(0, tk.END)
        self.update_char_counter()
        
        # Очищаем статус через 5 секунд
        self.root.after(5000, lambda: self.send_status.config(text=""))

    def on_send_error(self, error):
        """Обработка ошибки отправки"""
        self.send_button.config(state='normal', text="📨 Отправить сообщение")
        self.send_status.config(
            text=f"❌ Ошибка: {error}",
            foreground='red'
        )
        
        # Очищаем статус через 5 секунд
        self.root.after(5000, lambda: self.send_status.config(text=""))
        
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