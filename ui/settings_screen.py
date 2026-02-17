# ui/settings_screen.py
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from data.storage import StorageManager
from data.models import Settings

PROVIDER_NAMES = {
    "openai": "OpenAI",
    "deepseek": "DeepSeek",
}

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
        orientation: 'vertical'
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
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage = StorageManager()
        self._load_settings()

    def _load_settings(self):
        self.settings = self.storage.get_settings()
        provider = self.settings.api_provider
        self.ids.provider_dropdown.text = PROVIDER_NAMES.get(provider, provider.capitalize())
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
        self.ids.provider_dropdown.text = PROVIDER_NAMES.get(provider, provider.capitalize())

    def save_settings(self):
        api_key = self.ids.api_key_input.text.strip()

        if not api_key:
            # Show error - for now use a simple toast
            from kivymd.toast import toast
            toast("Please enter an API key")
            return

        # Map display name back to provider key
        name_to_provider = {v: k for k, v in PROVIDER_NAMES.items()}
        self.settings.api_provider = name_to_provider.get(
            self.ids.provider_dropdown.text,
            self.ids.provider_dropdown.text.lower()
        )
        self.settings.api_key = api_key
        self.settings.model = self.ids.model_input.text or "gpt-3.5-turbo"

        self.storage.save_settings(self.settings)

        if self.callback:
            self.callback(self.settings)

        self.dismiss()

    def dismiss(self):
        if self.dialog:
            self.dialog.dismiss()

Builder.load_string(KV_CODE)
