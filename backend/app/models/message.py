from dataclasses import dataclass
from enum import Enum


class MessagePriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"


@dataclass
class Message:
    message_id: str
    source_id: str
    destination_id: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL