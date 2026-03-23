import time
from typing import List
from api.interfaces import IMessageSource
from api.models import Message

class RestSource(IMessageSource):
    def __init__(self, api_url: str = "http://localhost:5000", api_key: str = ""):
        self.api_url = api_url
        self.api_key = api_key
        self.connected = False
        self.processed = set()
        
    def connect(self) -> bool:
        print(f"🔌 Подключение к REST API {self.api_url}...")
        time.sleep(1)
        self.connected = True
        print("✅ Подключено к REST API (эмуляция)")
        return True
        
    def disconnect(self) -> None:
        self.connected = False
        print("🔌 Отключено от REST API")
        
    def fetch_new_messages(self) -> List[Message]:
        if not self.connected:
            return []
        
        # Для демо создаем тестовое сообщение
        if len(self.processed) == 0:
            return [
                Message.create(
                    source_type="rest",
                    sender="rest_api",
                    recipient="user3@jabber.local",
                    text="Тестовое сообщение из REST API"
                )
            ]
        return []
        
    def mark_as_processed(self, message_id: str) -> None:
        self.processed.add(message_id)
        print(f"✅ Сообщение {message_id} отмечено как обработанное в REST")
