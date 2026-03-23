import time
import threading
from typing import List
from .interfaces import IMessageSource, IMessageSender, ILogger
from .models import Message

class MessagingCore:
    def __init__(self, sources: List[IMessageSource], sender: IMessageSender, logger: ILogger):
        self.sources = sources
        self.sender = sender
        self.logger = logger
        self.is_running = False
        self.thread = None
        self.poll_interval = 5
        
    def start(self):
        if self.is_running:
            print("Core уже запущен")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._processing_loop)
        self.thread.daemon = True
        self.thread.start()
        print("✅ Core запущен")
        
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=10)
        print("🛑 Core остановлен")
        
    def _processing_loop(self):
        try:
            self.sender.connect()
            for source in self.sources:
                source.connect()
        except Exception as e:
            self.logger.log_error("Core", f"Ошибка подключения: {e}")
            return
            
        while self.is_running:
            try:
                for source in self.sources:
                    new_messages = source.fetch_new_messages()
                    
                    for msg in new_messages:
                        print(f"📨 Получено новое сообщение: {msg.id}")
                        self.logger.log_message_received(msg)
                        receipt = self.sender.send_message(msg)
                        self.logger.log_message_sent(receipt, msg)
                        
                        if not receipt.error:
                            source.mark_as_processed(msg.id)
                            print(f"✅ Сообщение {msg.id} отправлено {msg.recipient}")
                        else:
                            print(f"❌ Ошибка отправки {msg.id}: {receipt.error}")
                            
            except Exception as e:
                self.logger.log_error("Core", str(e))
                print(f"⚠️ Ошибка в цикле обработки: {e}")
                
            time.sleep(self.poll_interval)
