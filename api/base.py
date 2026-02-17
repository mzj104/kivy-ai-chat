# api/base.py
from abc import ABC, abstractmethod
from typing import Iterator, Optional

class AIClientAdapter(ABC):
    """Base class for AI service adapters"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def send_message(self, messages: list, stream: bool = True) -> Iterator[str]:
        """Send message and yield response chunks"""
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate API key is valid"""
        pass
