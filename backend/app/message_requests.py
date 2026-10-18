from pydantic import BaseModel
from app.models.message import MessagePriority


class MessageRequest(BaseModel):
    message_id: str
    source_id: str
    destination_id: str
    content: str
    priority: MessagePriority
