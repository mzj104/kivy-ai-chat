from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
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

    ScreenManager:
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
