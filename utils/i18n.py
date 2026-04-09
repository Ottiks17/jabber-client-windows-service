import json
import os

class LanguageManager:
    """Управление языками интерфейса"""
    
    LANGUAGES = {
        'ru': {
            # Общие
            'app_title': 'Jabber Robot',
            'service_started': 'Сервис запущен',
            'service_stopped': 'Сервис остановлен',
            'start': 'Запустить',
            'stop': 'Остановить',
            'save': 'Сохранить',
            'send': 'Отправить',
            'cancel': 'Отмена',
            'settings': 'Настройки',
            'logs': 'Логи',
            'send_message': 'Отправить сообщение',
            
            # Статистика
            'total_messages': 'Всего сообщений',
            'sent': 'Отправлено',
            'delivered': 'Доставлено',
            'read': 'Прочитано',
            'success_rate': 'Успех',
            
            # Настройки
            'xmpp_server': 'XMPP Сервер',
            'jid': 'JID (логин)',
            'password': 'Пароль',
            'oracle_source': 'Oracle БД',
            'rest_source': 'REST API',
            'rest_url': 'REST API URL',
            'api_key': 'API Key',
            
            # Сообщения
            'new_message': 'Новое сообщение',
            'recipient': 'Кому',
            'subject': 'Тема',
            'message': 'Сообщение',
            'char_counter': 'символов',
            'quick_replies': 'Быстрые ответы',
            
            # Уведомления
            'config_saved': 'Настройки сохранены',
            'message_sent': 'Сообщение отправлено',
            'error_recipient': 'Заполните получателя',
            'error_message': 'Введите текст сообщения',
            'error_length': 'Сообщение превышает 256 символов',
            'api_not_running': 'API сервер не запущен',
            
            # Тема
            'light_theme': 'Светлая тема',
            'dark_theme': 'Темная тема',
            'theme': 'Тема',
            'custom_color': 'Выбрать цвет',
            
            # Меню
            'show_window': 'Показать окно',
            'hide_window': 'Скрыть окно',
            'exit': 'Выход',
            'help': 'Помощь',
            'about': 'О программе',
        },
        
        'en': {
            # General
            'app_title': 'Jabber Robot',
            'service_started': 'Service started',
            'service_stopped': 'Service stopped',
            'start': 'Start',
            'stop': 'Stop',
            'save': 'Save',
            'send': 'Send',
            'cancel': 'Cancel',
            'settings': 'Settings',
            'logs': 'Logs',
            'send_message': 'Send message',
            
            # Statistics
            'total_messages': 'Total messages',
            'sent': 'Sent',
            'delivered': 'Delivered',
            'read': 'Read',
            'success_rate': 'Success rate',
            
            # Settings
            'xmpp_server': 'XMPP Server',
            'jid': 'JID (login)',
            'password': 'Password',
            'oracle_source': 'Oracle Database',
            'rest_source': 'REST API',
            'rest_url': 'REST API URL',
            'api_key': 'API Key',
            
            # Messages
            'new_message': 'New message',
            'recipient': 'Recipient',
            'subject': 'Subject',
            'message': 'Message',
            'char_counter': 'characters',
            'quick_replies': 'Quick replies',
            
            # Notifications
            'config_saved': 'Settings saved',
            'message_sent': 'Message sent',
            'error_recipient': 'Enter recipient',
            'error_message': 'Enter message text',
            'error_length': 'Message exceeds 256 characters',
            'api_not_running': 'API server not running',
            
            # Theme
            'light_theme': 'Light theme',
            'dark_theme': 'Dark theme',
            'theme': 'Theme',
            'custom_color': 'Choose color',
            
            # Menu
            'show_window': 'Show window',
            'hide_window': 'Hide window',
            'exit': 'Exit',
            'help': 'Help',
            'about': 'About',
        }
    }
    
    def __init__(self, lang='ru'):
        self.lang = lang
        self.strings = self.LANGUAGES.get(lang, self.LANGUAGES['ru'])
        self.lang_file = 'lang.json'
        self.load_language()
    
    def load_language(self):
        """Загрузить сохраненный язык"""
        try:
            with open(self.lang_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('lang') in self.LANGUAGES:
                    self.lang = data['lang']
                    self.strings = self.LANGUAGES[self.lang]
        except:
            pass
    
    def save_language(self):
        """Сохранить выбранный язык"""
        with open(self.lang_file, 'w', encoding='utf-8') as f:
            json.dump({'lang': self.lang}, f)
    
    def get(self, key):
        """Получить строку по ключу"""
        return self.strings.get(key, key)
    
    def set_language(self, lang):
        """Сменить язык"""
        if lang in self.LANGUAGES:
            self.lang = lang
            self.strings = self.LANGUAGES[lang]
            self.save_language()
            return True
        return False
    
    def get_languages(self):
        """Получить список доступных языков"""
        return list(self.LANGUAGES.keys())