import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import threading
import time
import logging
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем наши модули
from api.core import MessagingCore
from api.logger import FileLogger
from sources.oracle_source import OracleSource
from sources.rest_source import RestSource
from sender.real_xmpp_sender import RealXmppSender  # ← ИСПРАВЛЕНО: используем RealXmppSender

# Настройка логирования для службы
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'service.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class JabberXMPPService(win32serviceutil.ServiceFramework):
    """Windows Service для Jabber клиента"""
    
    # Обязательные атрибуты службы
    _svc_name_ = "JabberXMPPClient"
    _svc_display_name_ = "Jabber XMPP Client Service"
    _svc_description_ = "Сервис для получения сообщений из Oracle и REST API и отправки их через XMPP"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        
        # Событие для остановки службы
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        
        # Флаг работы службы
        self.is_running = True
        self.core = None
        self.core_thread = None
        
        logging.info("Служба инициализирована")
        
    def SvcStop(self):
        """Вызывается при остановке службы"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        logging.info("Получен сигнал остановки службы")
        
        # Останавливаем ядро
        if self.core:
            self.core.stop()
            
    def SvcDoRun(self):
        """Вызывается при запуске службы"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        logging.info("Служба запущена")
        
        try:
            self.main()
        except Exception as e:
            logging.error(f"Критическая ошибка в службе: {e}", exc_info=True)
            
    def main(self):
        """Основная логика службы"""
        logging.info("Запуск основной логики службы")
        
        try:
            # Создаем компоненты
            sources = []
            
            # Загружаем конфигурацию
            import yaml
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            else:
                logging.warning("config.yaml не найден, используются настройки по умолчанию")
                config = {}
            
            # Настройка источников
            oracle_config = config.get('oracle', {})
            if oracle_config.get('enabled', True):
                sources.append(OracleSource())
                logging.info("Oracle источник добавлен")
                
            rest_config = config.get('rest', {})
            if rest_config.get('enabled', True):
                sources.append(RestSource(
                    api_url=rest_config.get('api_url', 'http://localhost:5000'),
                    api_key=rest_config.get('api_key', '')
                ))
                logging.info("REST API источник добавлен")
            
            # XMPP отправитель - ИСПРАВЛЕНО: используем RealXmppSender
            xmpp_config = config.get('xmpp', {})
            sender = RealXmppSender(  # ← ИЗМЕНЕНО: XmpppySender → RealXmppSender
                server=xmpp_config.get('server', 'localhost'),
                username=xmpp_config.get('username', ''),
                password=xmpp_config.get('password', '')
            )
            logging.info(f"XMPP отправитель настроен на сервер {xmpp_config.get('server', 'localhost')}")
            
            # Логгер
            logger = FileLogger(log_file=os.path.join(log_dir, 'messages.log'))
            
            # Создаем ядро
            self.core = MessagingCore(sources, sender, logger)
            
            # Запускаем ядро в отдельном потоке
            self.core_thread = threading.Thread(target=self.core.start)
            self.core_thread.daemon = True
            self.core_thread.start()
            
            logging.info("Ядро запущено, ожидание команд...")
            
            # Ожидаем сигнала остановки
            while self.is_running:
                # Проверяем событие остановки
                rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)  # 5 секунд таймаут
                if rc == win32event.WAIT_OBJECT_0:
                    logging.info("Получен сигнал остановки")
                    break
                    
        except Exception as e:
            logging.error(f"Ошибка в main: {e}", exc_info=True)
            
        logging.info("Служба завершает работу")

def main():
    """Точка входа для управления службой"""
    if len(sys.argv) == 1:
        # Запуск как службы
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(JabberXMPPService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Обработка команд (install/start/stop/remove)
        win32serviceutil.HandleCommandLine(JabberXMPPService)

if __name__ == '__main__':
    main()