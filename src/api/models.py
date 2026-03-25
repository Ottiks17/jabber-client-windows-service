from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid

@dataclass
class Message:
    id: str
    source_type: str
    sender: str
    recipient: str
    text: str
    created_at: datetime
    
    @classmethod
    def create(cls, source_type: str, sender: str, recipient: str, text: str):
        return cls(
            id=str(uuid.uuid4()),
            source_type=source_type,
            sender=sender,
            recipient=recipient,
            text=text,
            created_at=datetime.now()
        )

@dataclass
class DeliveryReceipt:
    message_id: str
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    error: Optional[str] = None

@dataclass
class LogEntry:
    id: str
    message_type: str
    sender: str
    recipient: str
    text: str
    sent_time: Optional[datetime]
    delivered_time: Optional[datetime]
    read_time: Optional[datetime]
    created_at: datetime = datetime.now()
