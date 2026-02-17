# ui/history_screen.py
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty
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
    main_screen = ObjectProperty(None, allownone=True)

    def __init__(self, main_screen=None, **kwargs):
        super().__init__(**kwargs)
        if main_screen:
            self.main_screen = main_screen
        self.storage = StorageManager()
        # Don't load conversations in __init__ - wait until main_screen is set
        Clock.schedule_once(lambda dt: self._load_conversations(), 0)

    def on_main_screen(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self._load_conversations(), 0)

    def _load_conversations(self):
        if not self.ids:
            return

        self.ids.conversation_list.clear_widgets()

        conversations = self.storage.get_all_conversations()
        for conv in conversations:
            item = OneLineListItem(
                text=conv.title if hasattr(conv, 'title') else 'New Chat',
                on_release=lambda x, c=conv.id if hasattr(conv, 'id') else None: self.load_conversation(c)
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
