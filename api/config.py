# api/config.py
from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient
from .base import AIClientAdapter

CLIENTS = {
    "openai": OpenAIClient,
    "deepseek": DeepSeekClient,
}

def get_client(provider: str, api_key: str, model: str) -> AIClientAdapter:
    client_class = CLIENTS.get(provider)
    if not client_class:
        raise ValueError(f"Unknown provider: {provider}")
    return client_class(api_key=api_key, model=model)
