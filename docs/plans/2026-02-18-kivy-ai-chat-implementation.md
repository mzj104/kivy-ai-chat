# Kivy AI Chat Assistant Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a cross-platform AI chat Android app using Kivy/KivyMD with ChatGPT-style interface, multi-conversation support, and configurable AI providers.

**Architecture:** MVC pattern with KivyMD for UI, adapter pattern for AI services, TinyDB for local storage.

**Tech Stack:** Kivy 2.3.0, KivyMD 1.2.0, OpenAI API, TinyDB, Buildozer

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `main.py`
- Create: `.gitignore`
- Create: `buildozer.spec`

**Step 1: Create requirements.txt**

```txt
kivy==2.3.0
kivymd==1.2.0
plyer==2.1.0
openai==1.12.0
requests==2.31.0
tinydb==4.8.0
markdownify==0.11.6
```

**Step 2: Create basic main.py**

```python
from kivy.app import App
from kivy.lang import Builder
from kivymd.app import MDApp

class AIChatApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return Builder.load_string("""
MDBoxLayout:
    orientation: 'vertical'
    MDLabel:
        text: 'AI Chat Assistant'
        halign: 'center'
""")

if __name__ == '__main__':
    AIChatApp().run()
```

**Step 3: Create .gitignore**

```txt
# Kivy
.bin/
.cache/

# Buildozer
.buildozer/
*.apk
*.aab

# Python
__pycache__/
*.pyc
venv/
.venv/

# IDE
.vscode/
.idea/

# Data
*.db
*.json
!package.json
```

**Step 4: Initialize buildozer.spec**

Run: `buildozer init`

**Step 5: Test basic app runs**

Run: `python main.py`
Expected: Window opens with "AI Chat Assistant" label

**Step 6: Commit**

```bash
git add .
git commit -m "feat: initial project setup with Kivy/KivyMD"
```

---

## Task 2: Data Layer - Models and Storage

**Files:**
- Create: `data/__init__.py`
- Create: `data/models.py`
- Create: `data/storage.py`

**Step 1: Create data models**

```python
# data/models.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid

@dataclass
class Message:
    role: str  # 'user' or 'assistant'
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
    api_provider: str = "openai"  # 'openai', 'deepseek', etc.
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    current_conversation_id: str = ""
```

**Step 2: Create storage manager**

```python
# data/storage.py
from tinydb import TinyDB, Query
from kivy.app import App
from pathlib import Path
from .models import Conversation, Settings, Message
import json

class StorageManager:
    def __init__(self):
        app = App.get_running_app()
        self.data_dir = Path(app.user_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = TinyDB(self.data_dir / "chat_data.json")

    def save_conversation(self, conversation: Conversation):
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

    def get_all_conversations(self) -> list:
        return self.db.all()

    def delete_conversation(self, conv_id: str):
        self.db.remove(Query().id == conv_id)

    def save_settings(self, settings: Settings):
        data = {
            'api_provider': settings.api_provider,
            'api_key': settings.api_key,
            'model': settings.model,
            'current_conversation_id': settings.current_conversation_id
        }
        self.db.upsert(data, Query().api_provider != "")

    def get_settings(self) -> Settings:
        result = self.db.get(Query().api_provider.exists())
        if result:
            return Settings(**result)
        return Settings()
```

**Step 3: Create data __init__.py**

```python
# data/__init__.py
from .models import Message, Conversation, Settings
from .storage import StorageManager
```

**Step 4: Test storage**

Create test file: `tests/test_storage.py`

```python
import sys
sys.path.insert(0, '..')
from data.models import Message, Conversation, Settings
from data.storage import StorageManager
from kivy.app import App
from tempfile import TemporaryDirectory
import os

# Mock App for testing
class MockApp(App):
    def __init__(self, temp_dir):
        super().__init__()
        self._user_data_dir = temp_dir

    @property
    def user_data_dir(self):
        return self._user_data_dir

def test_save_and_load_conversation():
    App.set_running_app(MockApp(TemporaryDirectory().name))

    storage = StorageManager()
    conv = Conversation(title="Test Chat")
    conv.messages.append(Message(role="user", content="Hello"))

    storage.save_conversation(conv)
    loaded = storage.get_conversation(conv.id)

    assert loaded.id == conv.id
    assert loaded.title == "Test Chat"
    assert len(loaded.messages) == 1
    assert loaded.messages[0].content == "Hello"

def test_settings():
    App.set_running_app(MockApp(TemporaryDirectory().name))

    storage = StorageManager()
    settings = Settings(api_provider="deepseek", api_key="test-key")

    storage.save_settings(settings)
    loaded = storage.get_settings()

    assert loaded.api_provider == "deepseek"
    assert loaded.api_key == "test-key"
```

**Step 5: Run tests**

Run: `python -m pytest tests/test_storage.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add data/ tests/
git commit -m "feat: implement data layer with TinyDB storage"
```

---

## Task 3: API Layer - AI Service Adapters

**Files:**
- Create: `api/__init__.py`
- Create: `api/base.py`
- Create: `api/openai_client.py`
- Create: `api/deepseek_client.py`
- Create: `api/config.py`

**Step 1: Create base adapter**

```python
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
```

**Step 2: Create OpenAI client**

```python
# api/openai_client.py
from openai import OpenAI
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
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

    def validate_api_key(self) -> bool:
        try:
            self.client.models.list()
            return True
        except:
            return False
```

**Step 3: Create DeepSeek client**

```python
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
            "stream": True
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                stream=True
            )
            response.raise_for_status()

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
        except Exception as e:
            yield f"Error: {str(e)}"

    def validate_api_key(self) -> bool:
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(f"{self.base_url}/models", headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False
```

**Step 4: Create config manager**

```python
# api/config.py
from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient

CLIENTS = {
    "openai": OpenAIClient,
    "deepseek": DeepSeekClient,
}

def get_client(provider: str, api_key: str, model: str):
    client_class = CLIENTS.get(provider)
    if not client_class:
        raise ValueError(f"Unknown provider: {provider}")
    return client_class(api_key=api_key, model=model)
```

**Step 5: Create api __init__.py**

```python
# api/__init__.py
from .base import AIClientAdapter
from .openai_client import OpenAIClient
from .deepseek_client import DeepSeekClient
from .config import get_client, CLIENTS
```

**Step 6: Test API clients**

Create: `tests/test_api.py`

```python
import sys
sys.path.insert(0, '..')
from api.config import get_client
from data.models import Message

def test_get_openai_client():
    client = get_client("openai", "test-key", "gpt-3.5-turbo")
    assert client.model == "gpt-3.5-turbo"
    assert client.api_key == "test-key"

def test_get_deepseek_client():
    client = get_client("deepseek", "test-key", "deepseek-chat")
    assert client.model == "deepseek-chat"
```

**Step 7: Run tests**

Run: `python -m pytest tests/test_api.py -v`
Expected: PASS

**Step 8: Commit**

```bash
git add api/ tests/
git commit -m "feat: implement AI API adapters (OpenAI, DeepSeek)"
```

---

## Task 4: UI Components - Message Bubble

**Files:**
- Create: `ui/__init__.py`
- Create: `ui/chat_bubble.py`

**Step 1: Create chat bubble component**

```python
# ui/chat_bubble.py
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

KV_CODE = """
<ChatBubble>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: "8dp"
    spacing: "4dp"

    MDBoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: self.minimum_height

        MDIcon:
            id: icon
            icon: root.role_icon
            font_style: "Icon"
            theme_text_color: "Custom"
            text_color: root.role_color
            size_hint_x: None
            width: "24dp"

        MDLabel:
            text: root.role_text
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: root.role_color
            size_hint_x: None
            width: self.texture_size[0]
            text_size: None, None

    MDBoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: self.minimum_height

        MDLabel:
            text: root.content
            font_style: "Body1"
            markup: True
            size_hint_y: None
            height: self.texture_size[1]
            text_size: root.width - "16dp", None
"""

class ChatBubble(MDBoxLayout):
    content = StringProperty("")
    role = StringProperty("user")  # 'user' or 'assistant'

    def __init__(self, **kwargs):
        self._update_role_attrs()
        super().__init__(**kwargs)

    def on_role(self, instance, value):
        self._update_role_attrs()

    def _update_role_attrs(self):
        if self.role == "user":
            self.role_icon = "account"
            self.role_color = [0.2, 0.6, 1, 1]  # Blue
            self.role_text = "You"
        else:
            self.role_icon = "robot"
            self.role_color = [0.2, 0.8, 0.4, 1]  # Green
            self.role_text = "AI"

Builder.load_string(KV_CODE)
```

**Step 2: Update ui __init__.py**

```python
# ui/__init__.py
from .chat_bubble import ChatBubble
```

**Step 3: Test bubble component**

Create: `tests/test_bubble.py`

```python
import sys
sys.path.insert(0, '..')
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from ui.chat_bubble import ChatBubble

class BubbleTestApp(App):
    def build(self):
        root = Builder.load_string('''
Screen:
    BoxLayout:
        orientation: 'vertical'
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                id: container
        MDTextField:
            id: input
            hint_text: "Enter message"
            size_hint_y: None
            height: "50dp"
        MDRaisedButton:
            text: "Add User Bubble"
            on_release: app.add_user_bubble()
            size_hint_y: None
            height: "45dp"
        MDRaisedButton:
            text: "Add AI Bubble"
            on_release: app.add_ai_bubble()
            size_hint_y: None
            height: "45dp"
''')
        return root

    def add_user_bubble(self):
        bubble = ChatBubble(role="user", content=self.root.ids.input.text)
        self.root.ids.container.add_widget(bubble)

    def add_ai_bubble(self):
        bubble = ChatBubble(role="assistant", content=self.root.ids.input.text)
        self.root.ids.container.add_widget(bubble)

if __name__ == '__main__':
    BubbleTestApp().run()
```

**Step 4: Run bubble test**

Run: `python tests/test_bubble.py`
Expected: Window opens with buttons to add test bubbles

**Step 5: Commit**

```bash
git add ui/ tests/
git commit -m "feat: implement chat bubble component"
```

---

## Task 5: UI - Main Chat Screen

**Files:**
- Create: `ui/main_screen.py`
- Modify: `main.py`

**Step 1: Create main screen**

```python
# ui/main_screen.py
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from ui.chat_bubble import ChatBubble
from data.models import Conversation, Message
from data.storage import StorageManager
import threading

KV_CODE = """
<MainScreen>:
    orientation: 'vertical'

    # Top Bar
    MDTopAppBar:
        title: "AI Chat"
        elevation: 2
        left_action_items: [["menu", lambda x: root.toggle_drawer()]]
        right_action_items: [
            ["cog", lambda x: root.open_settings()],
            ["delete", lambda x: root.clear_chat()]
        ]

    # Message List
    RecycleView:
        id: message_list
        viewclass: 'ChatBubble'
        RecycleBoxLayout:
            default_size: None, dp(80)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'

    # Input Area
    MDBoxLayout:
        orientation: 'horizontal'
        padding: "8dp"
        spacing: "8dp"
        size_hint_y: None
        height: "65dp"

        MDTextField:
            id: message_input
            hint_text: "Type a message..."
            mode: "fill"
            multiline: False
            on_text_validate: root.send_message()

        MDFloatingActionButton:
            icon: "send"
            theme_icon_color: "Custom"
            icon_color: 1, 1, 1, 1
            md_bg_color: root.theme_cls.primary_color
            size_hint: None, None
            size: "55dp", "55dp"
            pos_hint: {"center_y": 0.5}
            on_release: root.send_message()
"""

class MainScreen(MDBoxLayout):
    current_conversation = ObjectProperty(None, allownone=True)
    storage = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = StorageManager()
        self._load_or_create_conversation()

    def _load_or_create_conversation(self):
        settings = self.storage.get_settings()
        if settings.current_conversation_id:
            self.current_conversation = self.storage.get_conversation(settings.current_conversation_id)
        else:
            self.current_conversation = Conversation()
            settings.current_conversation_id = self.current_conversation.id
            self.storage.save_settings(settings)

        self._refresh_messages()

    def _refresh_messages(self):
        self.ids.message_list.data = []
        for msg in self.current_conversation.messages:
            self._add_bubble(msg.role, msg.content)

    def _add_bubble(self, role: str, content: str):
        self.ids.message_list.data.append({
            'role': role,
            'content': content
        })

    def send_message(self):
        input_field = self.ids.message_input
        message = input_field.text.strip()

        if not message:
            return

        input_field.text = ""

        # Add user message
        user_msg = Message(role="user", content=message)
        self.current_conversation.messages.append(user_msg)
        self._add_bubble("user", message)

        # Save conversation
        self.storage.save_conversation(self.current_conversation)

        # TODO: Send to API and stream response
        # This will be implemented in Task 6

    def toggle_drawer(self):
        # TODO: Implement in Task 7
        pass

    def open_settings(self):
        # TODO: Implement in Task 7
        pass

    def clear_chat(self):
        self.current_conversation.messages = []
        self._refresh_messages()
        self.storage.save_conversation(self.current_conversation)

Builder.load_string(KV_CODE)
```

**Step 2: Update main.py**

```python
from kivy.app import App
from kivymd.app import MDApp
from ui.main_screen import MainScreen

class AIChatApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        return MainScreen()

if __name__ == '__main__':
    AIChatApp().run()
```

**Step 3: Test main screen**

Run: `python main.py`
Expected: Main chat interface opens, can type messages

**Step 4: Commit**

```bash
git add ui/main_screen.py main.py
git commit -m "feat: implement main chat screen with message input"
```

---

## Task 6: UI - Settings Screen

**Files:**
- Create: `ui/settings_screen.py`
- Modify: `ui/main_screen.py`

**Step 1: Create settings screen**

```python
# ui/settings_screen.py
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from data.storage import StorageManager
from data.models import Settings
from api.config import CLIENTS

KV_CODE = """
<SettingsScreen>:
    orientation: 'vertical'
    padding: "16dp"
    spacing: "16dp"

    MDLabel:
        text: "Settings"
        font_style: "H5"
        size_hint_y: None
        height: self.texture_size[1]

    MDBoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: "8dp"

        MDLabel:
            text: "API Provider"
            font_style: "Subtitle2"
            size_hint_y: None
            height: self.texture_size[1]

        MDDropDownItem:
            id: provider_dropdown
            text: "OpenAI"
            on_release: root.show_provider_menu()

    MDBoxLayout:
        orientation: 'vertical'
        size_hint_y: None
        height: self.minimum_height
        spacing: "8dp"

        MDLabel:
            text: "API Key"
            font_style: "Subtitle2"
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: api_key_input
            hint_text: "Enter your API key"
            password: True
            mode: "fill"

    MDBoxLayout:
        orientation: 'vertical"
        size_hint_y: None
        height: self.minimum_height
        spacing: "8dp"

        MDLabel:
            text: "Model"
            font_style: "Subtitle2"
            size_hint_y: None
            height: self.texture_size[1]

        MDTextField:
            id: model_input
            hint_text: "gpt-3.5-turbo"
            mode: "fill"

    MDWidget:
        # Spacer

    MDRaisedButton:
        text: "Save Settings"
        on_release: root.save_settings()
        size_hint_y: None
        height: "50dp"
        md_bg_color: root.theme_cls.primary_color

    MDRaisedButton:
        text: "Cancel"
        on_release: root.dismiss()
        size_hint_y: None
        height: "50dp"
        theme_text_color: "Custom"
        text_color: root.theme_cls.primary_color
        md_bg_color: 1, 1, 1, 1
"""

class SettingsScreen(MDBoxLayout):
    storage = None
    settings = None
    callback = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = StorageManager()
        self._load_settings()

    def _load_settings(self):
        self.settings = self.storage.get_settings()
        self.ids.provider_dropdown.text = self.settings.api_provider.capitalize()
        self.ids.api_key_input.text = self.settings.api_key
        self.ids.model_input.text = self.settings.model

    def show_provider_menu(self):
        menu_items = [
            {"text": "OpenAI", "viewclass": "OneLineListItem", "on_release": lambda x: self.set_provider("openai")},
            {"text": "DeepSeek", "viewclass": "OneLineListItem", "on_release": lambda x: self.set_provider("deepseek")},
        ]

        MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        ).open(self.ids.provider_dropdown)

    def set_provider(self, provider: str):
        self.ids.provider_dropdown.text = provider.capitalize()

    def save_settings(self):
        self.settings.api_provider = self.ids.provider_dropdown.text.lower()
        self.settings.api_key = self.ids.api_key_input.text
        self.settings.model = self.ids.model_input.text or "gpt-3.5-turbo"

        self.storage.save_settings(self.settings)

        if self.callback:
            self.callback(self.settings)

        self.dismiss()

    def dismiss(self):
        self.parent.parent.parent.dismiss()

Builder.load_string(KV_CODE)
```

**Step 2: Update main_screen.py to open settings**

Add to MainScreen class:

```python
def open_settings(self):
    settings_dialog = MDDialog(
        title="Settings",
        type="custom",
        content_cls=SettingsScreen(),
    )
    settings_dialog.open()
```

**Step 3: Test settings**

Run: `python main.py`
Expected: Can open settings and change configuration

**Step 4: Commit**

```bash
git add ui/settings_screen.py ui/main_screen.py
git commit -m "feat: implement settings screen with API configuration"
```

---

## Task 7: API Integration with Streaming

**Files:**
- Modify: `ui/main_screen.py`

**Step 1: Add API streaming to main screen**

Add imports at top:
```python
from api.config import get_client
from kivy.clock import Clock
```

Add method to MainScreen:

```python
def send_message(self):
    input_field = self.ids.message_input
    message = input_field.text.strip()

    if not message:
        return

    input_field.text = ""

    # Add user message
    user_msg = Message(role="user", content=message)
    self.current_conversation.messages.append(user_msg)
    self._add_bubble("user", message)

    # Save conversation
    self.storage.save_conversation(self.current_conversation)

    # Get AI response
    settings = self.storage.get_settings()
    if not settings.api_key:
        self._show_error("Please configure API key in settings")
        return

    # Start AI response in thread
    thread = threading.Thread(target=self._get_ai_response, args=(settings,))
    thread.start()

def _get_ai_response(self, settings):
    try:
        client = get_client(settings.api_provider, settings.api_key, settings.model)

        # Create AI message placeholder
        ai_msg = Message(role="assistant", content="")
        self.current_conversation.messages.append(ai_msg)

        # Stream response
        response_text = ""
        for chunk in client.send_message(self.current_conversation.messages[:-1]):
            response_text += chunk

            # Update UI on main thread
            Clock.schedule_once(lambda dt: self._update_last_bubble(response_text), 0)

        ai_msg.content = response_text
        self.storage.save_conversation(self.current_conversation)

    except Exception as e:
        Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)

def _update_last_bubble(self, content: str):
    if self.ids.message_list.data:
        last = self.ids.message_list.data[-1]
        if last['role'] == 'assistant':
            self.ids.message_list.data[-1] = {'role': 'assistant', 'content': content}
        else:
            self.ids.message_list.data.append({'role': 'assistant', 'content': content})
    else:
        self.ids.message_list.data.append({'role': 'assistant', 'content': content})

def _show_error(self, message: str):
    self.ids.message_list.data.append({
        'role': 'assistant',
        'content': f"⚠️ Error: {message}"
    })
```

**Step 2: Test API integration**

Run: `python main.py`
Expected: Can send messages and receive streaming AI responses

**Step 3: Commit**

```bash
git add ui/main_screen.py
git commit -m "feat: integrate AI API with streaming responses"
```

---

## Task 8: Conversation History (Drawer)

**Files:**
- Create: `ui/history_screen.py`
- Modify: `ui/main_screen.py`
- Modify: `main.py`

**Step 1: Create history drawer**

```python
# ui/history_screen.py
from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineListItem
from data.storage import StorageManager

KV_CODE = """
<HistoryDrawer>:
    orientation: 'vertical'

    MDBoxLayout:
        orientation: 'vertical'
        padding: "16dp"
        spacing: "8dp"

        MDLabel:
            text: "Conversations"
            font_style: "H6"
            size_hint_y: None
            height: self.texture_size[1]

        MDScrollView:
            id: scroll
            MDList:
                id: conversation_list

        MDSeparator:
            height: "1dp"

        MDRaisedButton:
            text: "New Chat"
            icon: "plus"
            on_release: root.new_conversation()
            size_hint_y: None
            height: "45dp"
"""

class HistoryDrawer(MDBoxLayout):
    storage = None
    main_screen = None

    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.storage = StorageManager()
        self._load_conversations()

    def _load_conversations(self):
        self.ids.conversation_list.clear_widgets()

        conversations = self.storage.get_all_conversations()
        for conv in conversations:
            item = OneLineListItem(
                text=conv.get('title', 'New Chat'),
                on_release=lambda x, c=conv.get('id'): self.load_conversation(c)
            )
            self.ids.conversation_list.add_widget(item)

    def load_conversation(self, conv_id: str):
        settings = self.storage.get_settings()
        settings.current_conversation_id = conv_id
        self.storage.save_settings(settings)

        if self.main_screen:
            self.main_screen._load_or_create_conversation()

        # Close drawer
        self.parent.set_state("close")

    def new_conversation(self):
        from data.models import Conversation
        new_conv = Conversation()
        self.storage.save_conversation(new_conv)

        settings = self.storage.get_settings()
        settings.current_conversation_id = new_conv.id
        self.storage.save_settings(settings)

        if self.main_screen:
            self.main_screen._load_or_create_conversation()

        self.parent.set_state("close")
        self._load_conversations()

Builder.load_string(KV_CODE)
```

**Step 2: Update main.py to include drawer**

```python
from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from ui.main_screen import MainScreen
from ui.history_screen import HistoryDrawer

class RootLayout(MDBoxLayout):
    pass

class AIChatApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        # Create root with navigation drawer
        root = Builder.load_string('''
MDNavigationLayout:
    MDNavigationDrawer:
        id: drawer
        radius: (0, 16, 16, 0)
        HistoryDrawer:
            id: history
            main_screen: app.main_screen

    MainScreen:
        id: main_screen
        drawer: drawer
''')

        self.main_screen = root.ids.main_screen
        self.main_screen.drawer = root.ids.drawer
        root.ids.history.main_screen = self.main_screen

        return root

if __name__ == '__main__':
    AIChatApp().run()
```

**Step 3: Update main_screen.py to handle drawer**

Add property:
```python
drawer = ObjectProperty(None, allownone=True)
```

Update toggle_drawer:
```python
def toggle_drawer(self):
    if self.drawer:
        self.drawer.set_state("toggle")
```

**Step 4: Test history drawer**

Run: `python main.py`
Expected: Can open drawer, see conversations, create new chat

**Step 5: Commit**

```bash
git add ui/history_screen.py ui/main_screen.py main.py
git commit -m "feat: implement conversation history drawer"
```

---

## Task 9: Markdown Rendering

**Files:**
- Create: `ui/markdown_label.py`
- Modify: `ui/chat_bubble.py`
- Modify: `requirements.txt`

**Step 1: Install markdown garden**

Add to requirements.txt:
```txt
markdown==3.5.1
```

**Step 2: Create markdown label component**

```python
# ui/markdown_label.py
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
from markdown import markdown
import re

KV_CODE = """
<MarkdownLabel>:
    markup: True
    text_size: self.width, None
    valign: 'top'
"""

class MarkdownLabel(MDLabel):
    source_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._render_markdown()

    def on_source_text(self, instance, value):
        self._render_markdown()

    def _render_markdown(self):
        if not self.source_text:
            self.text = ""
            return

        # Convert markdown to HTML
        html = markdown(self.source_text)

        # Convert HTML to Kivy markup
        kivy_markup = self._html_to_kivy_markup(html)
        self.text = kivy_markup

    def _html_to_kivy_markup(self, html: str) -> str:
        """Simple HTML to Kivy markup conversion"""
        result = html

        # Code blocks
        result = re.sub(r'<pre><code>(.*?)</code></pre>', r'[color=#2d2d2d][b]\1[/b][/color]', result, flags=re.DOTALL)

        # Inline code
        result = re.sub(r'<code>(.*?)</code>', r'[color=#2d2d2d][font=RobotoMono]\1[/font][/color]', result)

        # Bold
        result = re.sub(r'<strong>(.*?)</strong>', r'[b]\1[/b]', result)

        # Italic
        result = re.sub(r'<em>(.*?)</em>', r'[i]\1[/i]', result)

        # Links
        result = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[ref=\1][color=#2196F3][u]\2[/u][/color][/ref]', result)

        # Remove other HTML tags
        result = re.sub(r'<[^>]+>', '', result)

        # Handle newlines
        result = result.replace('\n', '\n')

        return result

Builder.load_string(KV_CODE)
```

**Step 3: Update chat bubble to use markdown**

Modify ui/chat_bubble.py:
```python
from ui.markdown_label import MarkdownLabel

# In KV_CODE, replace MDLabel with MarkdownLabel for content
```

**Step 4: Test markdown**

Run: `python main.py`
Expected: AI responses with code blocks are formatted

**Step 5: Commit**

```bash
git add ui/markdown_label.py ui/chat_bubble.py requirements.txt
git commit -m "feat: add markdown rendering support"
```

---

## Task 10: Android Packaging Configuration

**Files:**
- Modify: `buildozer.spec`

**Step 1: Configure buildozer.spec**

Edit buildozer.spec with these settings:

```spec
[app]
title = AI Chat Assistant
package.name = kvyaichat
package.domain = org.myapp
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = 0.1
requirements = python3,kivy,kivymd,openai,requests,tinydb,markdown,plyer
presplash.filename = %(source.dir)s/data/presplash.png
icon.filename = %(source.dir)s/data/icon.png

[buildozer]
log_level = 2

[app]
android.minapi = 21
android.sdk = 33
android.ndk = 25b

[android]
permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.archs = arm64-v8a,armeabi-v7a

[android.metadata]
release.type = final
```

**Step 2: Add placeholder assets**

Create: `data/icon.png` (512x512 PNG icon)
Create: `data/presplash.png` (portrait splash screen)

**Step 3: Test build**

Run: `buildozer android debug`
Expected: Compiles APK (may take 10-30 minutes)

**Step 4: Commit**

```bash
git add buildozer.spec data/
git commit -m "feat: configure Android packaging with Buildozer"
```

---

## Task 11: Final Testing and Polish

**Files:**
- Various

**Step 1: Test full flow**

1. Open app
2. Configure API in settings
3. Send message
4. Verify streaming response
5. Create new conversation
6. Switch between conversations
7. Clear chat
8. Close and reopen app - verify persistence

**Step 2: Add error handling for edge cases**

- Empty API key
- Network errors
- Invalid API key
- Rate limiting

**Step 3: Add loading indicator**

Add to main_screen.py during API call:
```python
# Show loading spinner
self.ids.send_button.disabled = True
```

**Step 4: Final commit**

```bash
git add .
git commit -m "chore: final polish and error handling"
```

**Step 5: Create release build**

Run: `buildozer android release`

---

## Completion Checklist

- [ ] Project initialized with Kivy/KivyMD
- [ ] Data layer with TinyDB storage
- [ ] API adapters for OpenAI and DeepSeek
- [ ] Chat bubble UI component
- [ ] Main chat screen with message input
- [ ] Settings screen for API configuration
- [ ] Streaming AI responses
- [ ] Conversation history drawer
- [ ] Markdown rendering
- [ ] Android APK build configured
- [ ] Full end-to-end testing

---

## Notes for Developer

1. **First-time setup**: Run `pip install -r requirements.txt`
2. **Testing**: Use `python main.py` to run desktop version
3. **Android build**: Use Buildozer - first build takes time to download dependencies
4. **Kivy Garden**: May need `garden install markdown`
5. **Chinese support**: Add fonts to assets if needed
