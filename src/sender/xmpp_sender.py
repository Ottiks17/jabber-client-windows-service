import time
from datetime import datetime
from api.interfaces import IMessageSender
from api.models import Message, DeliveryReceipt

class XmppSender(IMessageSender):
    def __init__(self, server='localhost', username='', password=''):
        self.server = server
        self.username = username
        self.password = password
        self.connected = False
        
    def connect(self):
        print(f"🔌 Подключение к XMPP серверу {self.server}...")
        time.sleep(1)
        self.connected = True
        print(f"✅ Подключено как {self.username} (ЭМУЛЯЦИЯ)")
        return True
        
    def disconnect(self):
        self.connected = False
        print("🔌 Отключено от XMPP сервера")
        
    def send_message(self, message):
        if not self.connected:
            return DeliveryReceipt(
                message_id=message.id,
                error="Нет подключения"
            )
        
        print(f"📤 Отправка сообщения {message.recipient}: {message.text[:50]}...")
        time.sleep(0.5)
        
        return DeliveryReceipt(
            message_id=message.id,
            delivered_at=datetime.now()
        )
