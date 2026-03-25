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
            
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
                headers['X-API-Key'] = self.api_key
            
            response = requests.get(self.api_url, headers=headers, timeout=5)
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            messages = []
            
            if isinstance(data, dict) and 'messages' in data:
                items = data['messages']
            elif isinstance(data, list):
                items = data
            else:
                return []
            
            for item in items:
                msg_id = str(item.get('id', item.get('message_id', '')))
                if not msg_id or msg_id in self.processed_ids:
                    continue
                
                message = Message.create(
                    source_type="rest",
                    sender=item.get('sender', item.get('from', 'external_api')),
                    recipient=item.get('recipient', item.get('to', '')),
                    text=item.get('text', item.get('message', item.get('content', '')))
                )
                message.id = msg_id
                messages.append(message)
            
            return messages
                
        except Exception as e:
            print(f"⚠️ Ошибка получения сообщений: {e}")
            
        return []
        
    def mark_as_processed(self, message_id: str) -> None:
        self.processed_ids.add(message_id)
        print(f"✅ Сообщение {message_id} отмечено как обработанное")