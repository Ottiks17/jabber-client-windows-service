import time
from typing import List
from api.interfaces import IMessageSource
from api.models import Message

class OracleSource(IMessageSource):
    def __init__(self):
        self.connected = False
        self.messages = []
        self.processed = set()
        self._create_test_messages()
        
    def _create_test_messages(self):
        test_messages = [
            ("system", "vabber@jabber.fr", "Привет! Это тестовое сообщение из Oracle"),
            ("admin", "vabber@jabber.fr", "Hello! Test message from Oracle"),
            ("bot", "vabber@jabber.fr", "Сообщение с цифрами 123 и знаками !@#"),
        ]
        
        for sender, recipient, text in test_messages:
            self.messages.append(
                Message.create(
                    source_type="oracle",
                    sender=sender,
                    recipient=recipient,
                    text=text
                )
            )
            
    def connect(self) -> bool:
        print("🔌 Подключение к Oracle...")
        time.sleep(1)
        self.connected = True
        print("✅ Подключено к Oracle")
        return True
        
    def disconnect(self) -> None:
        self.connected = False
        print("🔌 Отключено от Oracle")
        
    def fetch_new_messages(self) -> List[Message]:
        if not self.connected:
            return []
            
        new_messages = []
        for msg in self.messages:
            if msg.id not in self.processed:
                new_messages.append(msg)
                break
                
        return new_messages
        
    def mark_as_processed(self, message_id: str) -> None:
        self.processed.add(message_id)
        print(f"✅ Сообщение {message_id} отмечено как обработанное в Oracle")
