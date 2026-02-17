# api/openai_client.py
from openai import OpenAI, OpenAIError
from .base import AIClientAdapter
from typing import Iterator

class OpenAIClient(AIClientAdapter):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model)
        self.client = OpenAI(api_key=api_key)

    def send_message(self, messages: list, stream: bool = True) -> Iterator[str]:
        formatted = [{"role": m.role, "content": m.content} for m in messages]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted,
                stream=stream
            )
            if stream:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                # Non-streaming: return full response
                content = response.choices[0].message.content
                yield content
        except Exception as e:
            yield f"Error: {str(e)}"

    def validate_api_key(self) -> bool:
        try:
            self.client.models.list()
            return True
        except OpenAIError:
            return False
