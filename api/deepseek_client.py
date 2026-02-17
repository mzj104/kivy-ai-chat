# api/deepseek_client.py
import requests
from .base import AIClientAdapter
from typing import Iterator
import json

class DeepSeekClient(AIClientAdapter):
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(api_key, model)
        self.base_url = "https://api.deepseek.com/v1"

    def send_message(self, messages: list, stream: bool = True) -> Iterator[str]:
        formatted = [{"role": m.role, "content": m.content} for m in messages]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": formatted,
            "stream": stream
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            json_str = line[6:]
                            if json_str == '[DONE]':
                                break
                            try:
                                chunk = json.loads(json_str)
                                if 'choices' in chunk and chunk['choices']:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
            else:
                # Non-streaming: return full response
                result = response.json()
                if 'choices' in result and result['choices']:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    yield content
        except requests.RequestException as e:
            yield f"Error: {str(e)}"

    def validate_api_key(self) -> bool:
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
