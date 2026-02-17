# tests/test_storage.py
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tinydb import TinyDB

from data.models import Message, Conversation, Settings
from data.storage import StorageManager


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Handle Windows file locking issues during cleanup
    try:
        shutil.rmtree(temp_dir)
    except (PermissionError, OSError):
        # On Windows, TinyDB may still have the file locked
        # Just leave the temp directory; it will be cleaned up by the OS
        pass


@pytest.fixture
def mock_app(temp_data_dir):
    """Create a mock Kivy App with temporary data directory."""
    app = Mock()
    app.user_data_dir = str(temp_data_dir)
    return app


@pytest.fixture
def storage_manager(mock_app):
    """Create a StorageManager instance with mocked app."""
    with patch('data.storage.App.get_running_app', return_value=mock_app):
        storage = StorageManager()
        # Clear any existing data
        storage.db.truncate()
        yield storage


class TestMessage:
    def test_message_creation(self):
        """Test creating a Message object."""
        message = Message(role="user", content="Hello, AI!")
        assert message.role == "user"
        assert message.content == "Hello, AI!"
        assert message.timestamp is not None
        assert isinstance(message.timestamp, str)

    def test_message_with_custom_timestamp(self):
        """Test creating a Message with custom timestamp."""
        custom_time = "2024-01-01T12:00:00"
        message = Message(role="assistant", content="Hi there!", timestamp=custom_time)
        assert message.timestamp == custom_time


class TestConversation:
    def test_conversation_creation(self):
        """Test creating a Conversation object."""
        conv = Conversation()
        assert conv.id is not None
        assert conv.title == "New Chat"
        assert conv.created_at is not None
        assert isinstance(conv.messages, list)
        assert len(conv.messages) == 0

    def test_conversation_with_custom_title(self):
        """Test creating a Conversation with custom title."""
        conv = Conversation(title="My Chat")
        assert conv.title == "My Chat"

    def test_conversation_with_messages(self):
        """Test creating a Conversation with messages."""
        msg1 = Message(role="user", content="Hello")
        msg2 = Message(role="assistant", content="Hi there!")
        conv = Conversation(messages=[msg1, msg2])
        assert len(conv.messages) == 2
        assert conv.messages[0].content == "Hello"
        assert conv.messages[1].content == "Hi there!"


class TestSettings:
    def test_settings_defaults(self):
        """Test Settings default values."""
        settings = Settings()
        assert settings.api_provider == "openai"
        assert settings.api_key == ""
        assert settings.model == "gpt-3.5-turbo"
        assert settings.current_conversation_id == ""

    def test_settings_custom_values(self):
        """Test Settings with custom values."""
        settings = Settings(
            api_provider="anthropic",
            api_key="test-key",
            model="claude-3",
            current_conversation_id="conv-123"
        )
        assert settings.api_provider == "anthropic"
        assert settings.api_key == "test-key"
        assert settings.model == "claude-3"
        assert settings.current_conversation_id == "conv-123"


class TestStorageManager:
    def test_storage_manager_initialization(self, storage_manager, temp_data_dir):
        """Test StorageManager initializes correctly."""
        assert storage_manager.data_dir == temp_data_dir
        assert storage_manager.db is not None
        assert (temp_data_dir / "chat_data.json").exists()

    def test_save_and_get_conversation(self, storage_manager):
        """Test saving and retrieving a conversation."""
        conv = Conversation(title="Test Chat")
        conv.messages.append(Message(role="user", content="Test message"))

        storage_manager.save_conversation(conv)
        retrieved = storage_manager.get_conversation(conv.id)

        assert retrieved.id == conv.id
        assert retrieved.title == "Test Chat"
        assert len(retrieved.messages) == 1
        assert retrieved.messages[0].content == "Test message"

    def test_get_nonexistent_conversation(self, storage_manager):
        """Test retrieving a conversation that doesn't exist."""
        result = storage_manager.get_conversation("nonexistent-id")
        assert isinstance(result, Conversation)
        assert result.id != "nonexistent-id"  # Should return new Conversation

    def test_get_all_conversations(self, storage_manager):
        """Test retrieving all conversations."""
        conv1 = Conversation(title="Chat 1")
        conv2 = Conversation(title="Chat 2")

        storage_manager.save_conversation(conv1)
        storage_manager.save_conversation(conv2)

        all_convs = storage_manager.get_all_conversations()
        assert len(all_convs) == 2
        titles = [c.title for c in all_convs]
        assert "Chat 1" in titles
        assert "Chat 2" in titles

    def test_delete_conversation(self, storage_manager):
        """Test deleting a conversation."""
        conv = Conversation(title="To be deleted")
        storage_manager.save_conversation(conv)

        # Verify it exists
        retrieved = storage_manager.get_conversation(conv.id)
        assert retrieved.id == conv.id

        # Delete it
        storage_manager.delete_conversation(conv.id)

        # Verify it's gone
        result = storage_manager.db.get(lambda d: d['id'] == conv.id)
        assert result is None

    def test_save_and_get_settings(self, storage_manager):
        """Test saving and retrieving settings."""
        settings = Settings(
            api_provider="anthropic",
            api_key="test-key-123",
            model="claude-3-opus",
            current_conversation_id="conv-456"
        )

        storage_manager.save_settings(settings)
        retrieved = storage_manager.get_settings()

        assert retrieved.api_provider == "anthropic"
        assert retrieved.api_key == "test-key-123"
        assert retrieved.model == "claude-3-opus"
        assert retrieved.current_conversation_id == "conv-456"

    def test_get_default_settings(self, storage_manager):
        """Test getting settings when none exist."""
        settings = storage_manager.get_settings()
        assert isinstance(settings, Settings)
        assert settings.api_provider == "openai"
        assert settings.model == "gpt-3.5-turbo"

    def test_update_conversation(self, storage_manager):
        """Test updating an existing conversation."""
        conv = Conversation(title="Original Title")
        storage_manager.save_conversation(conv)

        # Update the conversation
        conv.title = "Updated Title"
        conv.messages.append(Message(role="user", content="New message"))
        storage_manager.save_conversation(conv)

        # Retrieve and verify
        retrieved = storage_manager.get_conversation(conv.id)
        assert retrieved.title == "Updated Title"
        assert len(retrieved.messages) == 1
        assert retrieved.messages[0].content == "New message"

    def test_conversation_with_multiple_messages(self, storage_manager):
        """Test saving conversation with multiple messages."""
        conv = Conversation(title="Multi-message Chat")
        conv.messages.extend([
            Message(role="user", content="First message"),
            Message(role="assistant", content="First response"),
            Message(role="user", content="Second message"),
            Message(role="assistant", content="Second response"),
        ])

        storage_manager.save_conversation(conv)
        retrieved = storage_manager.get_conversation(conv.id)

        assert len(retrieved.messages) == 4
        assert retrieved.messages[0].role == "user"
        assert retrieved.messages[1].role == "assistant"
        assert retrieved.messages[2].content == "Second message"
        assert retrieved.messages[3].content == "Second response"
