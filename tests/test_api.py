# tests/test_api.py
import pytest
from unittest.mock import Mock, MagicMock, patch
from api.base import AIClientAdapter
from api.openai_client import OpenAIClient
from api.deepseek_client import DeepSeekClient
from api.config import get_client, CLIENTS
from openai import OpenAIError
import requests


class TestAIClientAdapter:
    """Test the base adapter class"""

    def test_base_adapter_is_abstract(self):
        """Base adapter cannot be instantiated directly"""
        with pytest.raises(TypeError):
            AIClientAdapter("test_key", "test_model")


class TestOpenAIClient:
    """Test OpenAI client implementation"""

    def test_initialization(self):
        """Test client can be initialized with API key and model"""
        client = OpenAIClient("sk-test-key", "gpt-4")
        assert client.api_key == "sk-test-key"
        assert client.model == "gpt-4"

    def test_default_model(self):
        """Test default model is gpt-3.5-turbo"""
        client = OpenAIClient("sk-test-key")
        assert client.model == "gpt-3.5-turbo"

    @patch('api.openai_client.OpenAI')
    def test_send_message_with_mock_messages(self, mock_openai_class):
        """Test send_message formats messages correctly"""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Create mock response
        mock_response = MagicMock()
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = "Hello"

        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = " World"

        mock_chunk3 = MagicMock()
        mock_chunk3.choices = [MagicMock()]
        mock_chunk3.choices[0].delta.content = None

        mock_response.__iter__ = Mock(return_value=iter([mock_chunk1, mock_chunk2, mock_chunk3]))
        mock_client.chat.completions.create.return_value = mock_response

        # Create test messages
        mock_msg1 = Mock()
        mock_msg1.role = "user"
        mock_msg1.content = "Hi"

        # Run test
        client = OpenAIClient("sk-test-key")
        result = list(client.send_message([mock_msg1]))

        # Verify
        assert result == ["Hello", " World"]
        mock_client.chat.completions.create.assert_called_once()

    @patch('api.openai_client.OpenAI')
    def test_send_message_handles_errors(self, mock_openai_class):
        """Test send_message handles exceptions gracefully"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        mock_msg = Mock()
        mock_msg.role = "user"
        mock_msg.content = "Hi"

        client = OpenAIClient("sk-test-key")
        result = list(client.send_message([mock_msg]))

        assert result == ["Error: API Error"]

    @patch('api.openai_client.OpenAI')
    def test_validate_api_key_success(self, mock_openai_class):
        """Test validate_api_key returns True on success"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.models.list.return_value = []

        client = OpenAIClient("sk-test-key")
        assert client.validate_api_key() is True

    @patch('api.openai_client.OpenAI')
    def test_validate_api_key_failure(self, mock_openai_class):
        """Test validate_api_key returns False on error"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.models.list.side_effect = OpenAIError("Invalid key")

        client = OpenAIClient("invalid-key")
        assert client.validate_api_key() is False


class TestDeepSeekClient:
    """Test DeepSeek client implementation"""

    def test_initialization(self):
        """Test client can be initialized with API key and model"""
        client = DeepSeekClient("ds-test-key", "deepseek-coder")
        assert client.api_key == "ds-test-key"
        assert client.model == "deepseek-coder"

    def test_default_model(self):
        """Test default model is deepseek-chat"""
        client = DeepSeekClient("ds-test-key")
        assert client.model == "deepseek-chat"

    def test_base_url(self):
        """Test base URL is set correctly"""
        client = DeepSeekClient("ds-test-key")
        assert client.base_url == "https://api.deepseek.com/v1"

    @patch('api.deepseek_client.requests.post')
    def test_send_message_success(self, mock_post):
        """Test send_message processes SSE stream correctly"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()

        # Simulate SSE stream
        lines = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}',
            b'data: {"choices":[{"delta":{"content":" World"}}]}',
            b'data: [DONE]'
        ]
        mock_response.iter_lines.return_value = lines
        mock_post.return_value = mock_response

        # Create test messages
        mock_msg1 = Mock()
        mock_msg1.role = "user"
        mock_msg1.content = "Hi"

        # Run test
        client = DeepSeekClient("ds-test-key")
        result = list(client.send_message([mock_msg1]))

        # Verify
        assert result == ["Hello", " World"]

    @patch('api.deepseek_client.requests.post')
    def test_send_message_handles_http_error(self, mock_post):
        """Test send_message handles HTTP errors gracefully"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.RequestException("HTTP 401")
        mock_post.return_value = mock_response

        mock_msg = Mock()
        mock_msg.role = "user"
        mock_msg.content = "Hi"

        client = DeepSeekClient("invalid-key")
        result = list(client.send_message([mock_msg]))

        assert result == ["Error: HTTP 401"]

    @patch('api.deepseek_client.requests.get')
    def test_validate_api_key_success(self, mock_get):
        """Test validate_api_key returns True on success"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = DeepSeekClient("ds-test-key")
        assert client.validate_api_key() is True

    @patch('api.deepseek_client.requests.get')
    def test_validate_api_key_failure(self, mock_get):
        """Test validate_api_key returns False on error"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        client = DeepSeekClient("invalid-key")
        assert client.validate_api_key() is False

    @patch('api.deepseek_client.requests.get')
    def test_validate_api_key_exception(self, mock_get):
        """Test validate_api_key returns False on exception"""
        mock_get.side_effect = requests.RequestException("Network error")

        client = DeepSeekClient("ds-test-key")
        assert client.validate_api_key() is False


class TestConfig:
    """Test config module functionality"""

    def test_clients_dict_has_providers(self):
        """Test CLIENTS dict has expected providers"""
        assert "openai" in CLIENTS
        assert "deepseek" in CLIENTS

    def test_get_client_openai(self):
        """Test get_client returns OpenAI client for openai provider"""
        client = get_client("openai", "sk-test-key", "gpt-4")
        assert isinstance(client, OpenAIClient)
        assert client.api_key == "sk-test-key"
        assert client.model == "gpt-4"

    def test_get_client_deepseek(self):
        """Test get_client returns DeepSeek client for deepseek provider"""
        client = get_client("deepseek", "ds-test-key", "deepseek-coder")
        assert isinstance(client, DeepSeekClient)
        assert client.api_key == "ds-test-key"
        assert client.model == "deepseek-coder"

    def test_get_client_unknown_provider(self):
        """Test get_client raises ValueError for unknown provider"""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_client("unknown", "test-key", "test-model")
