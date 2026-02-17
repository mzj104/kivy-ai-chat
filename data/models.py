# data/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal
import uuid

@dataclass
class Message:
    role: Literal['user', 'assistant']
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    messages: List[Message] = field(default_factory=list)

@dataclass
class Settings:
    api_provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    current_conversation_id: str = ""
