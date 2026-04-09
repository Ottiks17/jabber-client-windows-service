import requests
import time
from typing import List
from api.interfaces import IMessageSource
from api.models import Message

class RestSource(IMessageSource):
    """Реальный источник сообщений из REST API"""
    
    def __init__(self, api_url: str = "", api_key: str = ""):
        self.api_url = api_url
        self.api_key = api_key
        self.connected = False
        self.processed_ids = set()
        
    def connect(self) -> bool:
        if not self.api_url:
            print("❌ REST API URL не указан")
            return False
            
        print(f"🔌 Подключение к REST API {self.api_url}...")
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                headers['X-API-Key'] = self.api_key
            
            response = requests.get(self.api_url, headers=headers, timeout=5)
            self.connected = response.status_code == 200
            if self.connected:
                print("✅ Подключено к REST API")
            else:
                print(f"❌ Ошибка: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            self.connected = False
        return self.connected
        
    def disconnect(self) -> None:
        self.connected = False
        print("🔌 Отключено от REST API")
        
    def fetch_new_messages(self) -> List[Message]:
        if not self.connected:
            return []
        
        # Для демо создаем тестовое сообщение
        if len(self.processed_ids) == 0:
            return [
                Message.create(
                    source_type="rest",
                    sender="rest_api",
                    recipient="vabber@jabber.fr",  # ← изменено на ваш JID
                    text="Тестовое сообщение из REST API"
                )
            ]
        return []
        
    def mark_as_processed(self, message_id: str) -> None:
        self.processed_ids.add(message_id)
        print(f"✅ Сообщение {message_id} отмечено как обработанное")