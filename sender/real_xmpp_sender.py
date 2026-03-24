import threading
import time
from datetime import datetime
from typing import Optional
import xmpp

from api.interfaces import IMessageSender
from api.models import Message, DeliveryReceipt


class RealXmppSender(IMessageSender):
    """Реальный XMPP отправитель с использованием xmpppy"""
    
    def __init__(self, server: str = "localhost", username: str = "", password: str = ""):
        self.server = server
        self.username = username
        self.password = password
        self.connected = False
        self.client = None
        self.thread = None
        self.last_error = None
        
    def connect(self) -> bool:
        """Подключение к реальному XMPP серверу"""
        print(f"🔌 Подключение к XMPP серверу {self.server}...")
        
        try:
            # Парсим JID
            jid = xmpp.JID(self.username)
            
            # Создаем клиента
            self.client = xmpp.Client(jid.getDomain(), debug=[])
            
            # Подключаемся к серверу
            if not self.client.connect(server=(self.server, 5222)):
                self.last_error = "Ошибка подключения к серверу"
                print(f"❌ {self.last_error}")
                return False
            
            # Авторизуемся
            if not self.client.auth(jid.getNode(), self.password):
                self.last_error = "Ошибка авторизации (неверный логин или пароль)"
                print(f"❌ {self.last_error}")
                return False
            
            # Отправляем присутствие (становимся онлайн)
            self.client.sendInitPresence()
            
            self.connected = True
            print(f"✅ Подключено как {self.username}")
            
            # Запускаем поток для обработки входящих сообщений
            self.thread = threading.Thread(target=self._process_messages, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            self.last_error = str(e)
            print(f"❌ Ошибка подключения: {e}")
            return False
    
    def _process_messages(self):
        """Обработка входящих сообщений в фоне"""
        while self.connected:
            try:
                self.client.Process(1)  # Обрабатываем 1 секунду
            except Exception as e:
                print(f"⚠️ Ошибка обработки сообщений: {e}")
                break
    
    def disconnect(self) -> None:
        """Отключение от XMPP сервера"""
        self.connected = False
        if self.client:
            try:
                self.client.disconnect()
            except:
                pass
        print("🔌 Отключено от XMPP сервера")
    
    def send_message(self, message: Message) -> DeliveryReceipt:
        """Отправка реального сообщения через XMPP"""
        if not self.connected:
            return DeliveryReceipt(
                message_id=message.id,
                error=self.last_error or "Нет подключения к XMPP серверу"
            )
        
        try:
            # Проверяем получателя
            if not message.recipient or '@' not in message.recipient:
                return DeliveryReceipt(
                    message_id=message.id,
                    error="Неверный формат получателя (должно быть user@domain)"
                )
            
            # Проверяем длину сообщения
            if len(message.text) > 256:
                print(f"⚠️ Сообщение обрезано до 256 символов")
                message.text = message.text[:256]
            
            # Создаем XMPP сообщение
            msg = xmpp.Message(message.recipient, message.text)
            msg.setType('chat')
            
            # Отправляем
            self.client.send(msg)
            
            print(f"📤 Сообщение отправлено {message.recipient}: {message.text[:50]}...")
            
            # Возвращаем квитанцию
            return DeliveryReceipt(
                message_id=message.id,
                delivered_at=datetime.now()
            )
            
        except xmpp.ProtocolError as e:
            error_msg = f"XMPP протокол ошибка: {e}"
            print(f"❌ {error_msg}")
            return DeliveryReceipt(
                message_id=message.id,
                error=error_msg
            )
        except Exception as e:
            error_msg = f"Ошибка отправки: {str(e)}"
            print(f"❌ {error_msg}")
            return DeliveryReceipt(
                message_id=message.id,
                error=error_msg
            )
    
    def get_status(self) -> dict:
        """Получить статус подключения"""
        return {
            'connected': self.connected,
            'server': self.server,
            'username': self.username,
            'last_error': self.last_error
        }