from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Message, DeliveryReceipt, LogEntry

class IMessageSource(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def fetch_new_messages(self) -> List[Message]:
        pass
    
    @abstractmethod
    def mark_as_processed(self, message_id: str) -> None:
        pass

class IMessageSender(ABC):
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def send_message(self, message: Message) -> DeliveryReceipt:
        pass

class ILogger(ABC):
    @abstractmethod
    def log_message_received(self, message: Message) -> None:
        pass
    
    @abstractmethod
    def log_message_sent(self, receipt: DeliveryReceipt, message: Message) -> None:
        pass
    
    @abstractmethod
    def log_error(self, source: str, error: str, message_id: Optional[str] = None) -> None:
        pass
    
    @abstractmethod
    def get_logs(self) -> List[LogEntry]:
        pass
