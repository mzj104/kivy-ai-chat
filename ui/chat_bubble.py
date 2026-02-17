# ui/chat_bubble.py
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from ui.markdown_label import MarkdownLabel

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

        MarkdownLabel:
            source_text: root.content
            font_style: "Body1"
            size_hint_y: None
            height: self.minimum_height
            width: root.width - "16dp"
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
