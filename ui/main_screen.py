# ui/main_screen.py
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from ui.chat_bubble import ChatBubble
from ui.settings_screen import SettingsScreen
from data.models import Conversation, Message, Settings
from data.storage import StorageManager
from api.config import get_client
import threading

KV_CODE = """
<MainScreen>:
    MDBoxLayout:
        orientation: 'vertical'

        # Top Bar
        MDTopAppBar:
            title: "AI Chat"
            elevation: 2
            left_action_items: [["menu", lambda x: root.toggle_drawer()]]
            right_action_items: [["cog", lambda x: root.open_settings()], ["delete", lambda x: root.clear_chat()]]

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
                disabled: root.is_loading
                on_release: root.send_message()
"""

class MainScreen(MDScreen):
    current_conversation = ObjectProperty(None, allownone=True)
    drawer = ObjectProperty(None, allownone=True)
    storage = None
    is_loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = StorageManager()
        # Defer conversation loading until after KV is loaded
        Clock.schedule_once(lambda dt: self._load_or_create_conversation(), 0)

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
        if self.is_loading:
            return

        input_field = self.ids.message_input
        message = input_field.text.strip()

        if not message:
            return

        input_field.text = ""
        self.is_loading = True  # Start loading

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
            self.is_loading = False  # Stop loading on error
            return

        # Start AI response in thread
        thread = threading.Thread(target=self._get_ai_response, args=(settings,))
        thread.start()

    def _get_ai_response(self, settings: Settings):
        try:
            client = get_client(settings.api_provider, settings.api_key, settings.model)

            # Stream response FIRST, without modifying shared state
            response_text = ""
            for chunk in client.send_message(self.current_conversation.messages):
                response_text += chunk
                Clock.schedule_once(lambda dt: self._update_last_bubble(response_text), 0)

            # Add to conversation on main thread AFTER streaming completes
            def save_message(dt):
                ai_msg = Message(role="assistant", content=response_text)
                self.current_conversation.messages.append(ai_msg)
                self.storage.save_conversation(self.current_conversation)
                self.is_loading = False  # Stop loading
            Clock.schedule_once(save_message, 0)

        except Exception as e:
            Clock.schedule_once(lambda dt: self._show_error(str(e)), 0)
            self.is_loading = False  # Stop loading on error

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

    def toggle_drawer(self):
        if self.drawer:
            self.drawer.set_state("toggle")

    def open_settings(self):
        settings_screen = SettingsScreen()
        settings_dialog = MDDialog(
            title="Settings",
            type="custom",
            content_cls=settings_screen,
        )
        settings_screen.dialog = settings_dialog  # Store reference
        settings_dialog.open()

    def clear_chat(self):
        self.current_conversation.messages = []
        self._refresh_messages()
        self.storage.save_conversation(self.current_conversation)

Builder.load_string(KV_CODE)
