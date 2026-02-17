# api/__init__.py
from .base import AIClientAdapter
from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient
from .config import get_client, CLIENTS
