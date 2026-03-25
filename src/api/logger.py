import json
from datetime import datetime
from typing import List, Optional
from .interfaces import ILogger
from .models import Message, DeliveryReceipt, LogEntry

class FileLogger(ILogger):
    def __init__(self, log_file: str = "messages.log"):
        self.log_file = log_file
        self.logs: List[LogEntry] = []
        self._load_logs()
        
    def _load_logs(self):
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    self.logs.append(LogEntry(**item))
        except (FileNotFoundError, json.JSONDecodeError):
            self.logs = []
            
    def _save_logs(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump([vars(log) for log in self.logs], f, ensure_ascii=False, indent=2, default=str)
            
    def log_message_received(self, message: Message) -> None:
        entry = LogEntry(
            id=message.id,
            message_type=message.source_type,
            sender=message.sender,
            recipient=message.recipient,
            text=message.text,
            sent_time=None,
            delivered_time=None,
            read_time=None
        )
        self.logs.append(entry)
        self._save_logs()
        print(f"📝 Лог: сообщение получено от {message.sender}")
        
    def log_message_sent(self, receipt: DeliveryReceipt, message: Message) -> None:
        for log in self.logs:
            if log.id == receipt.message_id:
                log.sent_time = datetime.now()
                log.delivered_time = receipt.delivered_at
                log.read_time = receipt.read_at
                break
        self._save_logs()
        print(f"📝 Лог: сообщение отправлено {message.recipient}")
        
    def log_error(self, source: str, error: str, message_id: Optional[str] = None) -> None:
        print(f"⚠️ Ошибка [{source}]: {error} (msg: {message_id})")
        
    def get_logs(self) -> List[LogEntry]:
        return self.logs
