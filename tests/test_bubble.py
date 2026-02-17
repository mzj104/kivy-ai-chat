# tests/test_bubble.py
"""Visual test for ChatBubble component"""
import sys
import os

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from kivymd.app import MDApp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from ui.chat_bubble import ChatBubble


class ScrollContainer(MDBoxLayout):
    pass


class ChatBubbleTestApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.message_count = 0

    def build(self):
        # Main container
        main_layout = MDBoxLayout(orientation='vertical')

        # Button bar
        button_bar = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height='50dp',
            padding='10dp',
            spacing='10dp'
        )

        btn_user = MDRaisedButton(text='Add User Message')
        btn_user.bind(on_release=self.add_user_message)

        btn_ai = MDRaisedButton(text='Add AI Message')
        btn_ai.bind(on_release=self.add_ai_message)

        btn_clear = MDRaisedButton(text='Clear')
        btn_clear.bind(on_release=self.clear_messages)

        button_bar.add_widget(btn_user)
        button_bar.add_widget(btn_ai)
        button_bar.add_widget(btn_clear)

        # Scroll view for messages
        scroll = ScrollView(do_scroll_x=False)
        self.scroll_container = ScrollContainer(
            orientation='vertical',
            size_hint_y=None,
            padding='10dp',
            spacing='10dp'
        )
        scroll.add_widget(self.scroll_container)

        main_layout.add_widget(button_bar)
        main_layout.add_widget(scroll)

        return main_layout

    def add_user_message(self, instance):
        self.message_count += 1
        messages = [
            "Hello, how are you today?",
            "Can you help me with my coding project?",
            "What's the weather like?",
            "Tell me a joke!",
            "This is a test message with some [b]bold text[/b] and [i]italic text[/i]."
        ]
        content = messages[self.message_count % len(messages)]
        bubble = ChatBubble(content=content, role="user")
        self.scroll_container.add_widget(bubble)

    def add_ai_message(self, instance):
        self.message_count += 1
        messages = [
            "I'm doing well, thank you for asking!",
            "Of course! I'd be happy to help with your coding project. What do you need assistance with?",
            "I don't have access to real-time weather data, but you can check weather.com for accurate forecasts.",
            "Why did the programmer quit his job? Because he didn't get arrays!",
            "I can format text with [b]bold[/b], [i]italic[/i], and [color=#FF0000]colors[/color] using markup!"
        ]
        content = messages[self.message_count % len(messages)]
        bubble = ChatBubble(content=content, role="assistant")
        self.scroll_container.add_widget(bubble)

    def clear_messages(self, instance):
        self.scroll_container.clear_widgets()
        self.message_count = 0


if __name__ == '__main__':
    ChatBubbleTestApp().run()
