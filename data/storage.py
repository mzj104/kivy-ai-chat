# data/storage.py
from tinydb import TinyDB, Query
from kivy.app import App
from pathlib import Path
from typing import List, Optional
from .models import Conversation, Settings, Message

# Constant for settings document ID
SETTINGS_ID = "_settings"


class StorageManager:
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            app = App.get_running_app()
            data_dir = Path(app.user_data_dir)
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(self.data_dir / "chat_data.json")

    def save_conversation(self, conversation: Conversation) -> None:
        data = {
            'id': conversation.id,
            'title': conversation.title,
            'created_at': conversation.created_at,
            'messages': [
                {'role': m.role, 'content': m.content, 'timestamp': m.timestamp}
                for m in conversation.messages
            ]
        }
        self.db.upsert(data, Query().id == conversation.id)

    def get_conversation(self, conv_id: str) -> Conversation:
        result = self.db.get(Query().id == conv_id)
        if not result:
            return Conversation()
        return Conversation(
            id=result['id'],
            title=result['title'],
            created_at=result['created_at'],
            messages=[Message(**m) for m in result['messages']]
        )

    def get_all_conversations(self) -> List[Conversation]:
        results = self.db.all()
        return [
            Conversation(
                id=r['id'],
                title=r['title'],
                created_at=r['created_at'],
                messages=[Message(**m) for m in r['messages']]
            )
            for r in results if 'id' in r  # Only conversations, not settings
        ]

    def delete_conversation(self, conv_id: str) -> None:
        self.db.remove(Query().id == conv_id)

    def save_settings(self, settings: Settings) -> None:
        data = {
            '_id': SETTINGS_ID,
            'api_provider': settings.api_provider,
            'api_key': settings.api_key,
            'model': settings.model,
            'current_conversation_id': settings.current_conversation_id
        }
        self.db.upsert(data, Query()._id == SETTINGS_ID)

    def get_settings(self) -> Settings:
        result = self.db.get(Query()._id == SETTINGS_ID)
        if result:
            return Settings(
                api_provider=result.get('api_provider', 'openai'),
                api_key=result.get('api_key', ''),
                model=result.get('model', 'gpt-3.5-turbo'),
                current_conversation_id=result.get('current_conversation_id', '')
            )
        return Settings()
