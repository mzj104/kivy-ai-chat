# tests/test_history_screen.py
"""Unit tests for HistoryDrawer component"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import Mock, MagicMock, patch
from kivymd.app import MDApp
from kivy.lang import Builder
from ui.history_screen import HistoryDrawer
from data.models import Conversation, Message
from data.storage import StorageManager


class TestApp(MDApp):
    """Test app for KivyMD initialization"""
    def build(self):
        return Builder.load_string('MDBoxLayout:')


@pytest.fixture(scope="function")
def kivy_app():
    """Initialize KivyMD app for testing"""
    app = TestApp()
    app.theme_cls.theme_style = "Light"
    app.theme_cls.primary_palette = "Blue"
    return app


class TestHistoryDrawer:
    """Test suite for HistoryDrawer component"""

    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage manager"""
        with patch('ui.history_screen.StorageManager') as mock:
            storage = Mock()
            storage.get_all_conversations.return_value = []
            storage.get_settings.return_value = Mock(current_conversation_id="")
            mock.return_value = storage
            yield storage

    @pytest.fixture
    def mock_main_screen(self):
        """Create a mock main screen"""
        main_screen = Mock()
        main_screen._load_or_create_conversation = Mock()
        return main_screen

    def test_history_drawer_initialization(self, kivy_app, mock_storage, mock_main_screen):
        """Test that HistoryDrawer initializes correctly"""
        drawer = HistoryDrawer(mock_main_screen)
        assert drawer.main_screen == mock_main_screen
        assert drawer.storage == mock_storage
        mock_storage.get_all_conversations.assert_called_once()

    def test_load_conversations_empty(self, kivy_app, mock_storage, mock_main_screen):
        """Test loading conversations when none exist"""
        mock_storage.get_all_conversations.return_value = []
        drawer = HistoryDrawer(mock_main_screen)
        # Should not raise any errors and conversation list should be empty
        assert len(drawer.ids.conversation_list.children) == 0

    def test_load_conversations_with_data(self, kivy_app, mock_storage, mock_main_screen):
        """Test loading conversations with existing data"""
        conv1 = Conversation(
            id="conv1",
            title="Test Chat 1",
            messages=[Message(role="user", content="Hello")]
        )
        conv2 = Conversation(
            id="conv2",
            title="Test Chat 2",
            messages=[Message(role="assistant", content="Hi there")]
        )
        mock_storage.get_all_conversations.return_value = [conv1, conv2]

        drawer = HistoryDrawer(mock_main_screen)

        # Should have 2 items in the conversation list
        assert len(drawer.ids.conversation_list.children) == 2

    def test_load_conversation(self, kivy_app, mock_storage, mock_main_screen):
        """Test loading a specific conversation"""
        settings = Mock()
        settings.current_conversation_id = ""
        mock_storage.get_settings.return_value = settings

        drawer = HistoryDrawer(mock_main_screen)

        # Mock the parent's set_state method
        drawer.parent = Mock()
        drawer.parent.set_state = Mock()

        drawer.load_conversation("test_conv_id")

        # Verify settings were saved
        mock_storage.save_settings.assert_called_once()

        # Verify main screen was notified
        mock_main_screen._load_or_create_conversation.assert_called_once()

        # Verify drawer was closed
        drawer.parent.set_state.assert_called_with("close")

    def test_new_conversation(self, kivy_app, mock_storage, mock_main_screen):
        """Test creating a new conversation"""
        settings = Mock()
        settings.current_conversation_id = ""
        mock_storage.get_settings.return_value = settings
        mock_storage.save_conversation = Mock()

        new_conv = Conversation(id="new_conv_id")
        mock_storage.save_conversation.return_value = new_conv

        drawer = HistoryDrawer(mock_main_screen)

        # Mock the parent's set_state method
        drawer.parent = Mock()
        drawer.parent.set_state = Mock()

        with patch('data.models.Conversation') as MockConv:
            MockConv.return_value = new_conv
            drawer.new_conversation()

        # Verify conversation was created
        mock_storage.save_conversation.assert_called()

        # Verify main screen was notified
        mock_main_screen._load_or_create_conversation.assert_called()

        # Verify drawer was closed and conversations reloaded
        drawer.parent.set_state.assert_called_with("close")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
