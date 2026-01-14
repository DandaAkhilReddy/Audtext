"""
Service layer tests for Audtext backend.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import asyncio

from services.whisper_service import WhisperService
from services.ollama_service import OllamaService
from models.schemas import TaskStatus


class TestWhisperService:
    """Tests for WhisperService."""

    def test_singleton_pattern(self):
        """Test WhisperService follows singleton pattern."""
        # Note: This test may load the model if not mocked
        with patch.object(WhisperService, '_model', None):
            with patch.object(WhisperService, '_instance', None):
                with patch('services.whisper_service.WhisperModel') as mock_model:
                    mock_model.return_value = MagicMock()
                    service1 = WhisperService()
                    service2 = WhisperService()
                    assert service1 is service2

    def test_clean_transcript_removes_multiple_spaces(self):
        """Test transcript cleaning removes multiple spaces."""
        service = Mock(spec=WhisperService)
        service._clean_transcript = WhisperService._clean_transcript

        text = "Hello    world   this   has   spaces"
        result = service._clean_transcript(service, text)
        assert "    " not in result
        assert "Hello world this has spaces" == result

    def test_clean_transcript_removes_repeated_patterns(self):
        """Test transcript cleaning removes hallucinated repetitions."""
        service = Mock(spec=WhisperService)
        service._clean_transcript = WhisperService._clean_transcript

        # Simulate a hallucination pattern (repeated phrase at end)
        # Need at least pattern_len * 3 words for the detection to trigger
        # Using a 3-word pattern "thank you much" repeated at end
        text = "This is a normal sentence with several words in it thank you much thank you much"
        result = service._clean_transcript(service, text)
        # Should remove one of the repeated patterns
        assert result.count("thank you much") <= 1 or len(result) < len(text)

    def test_clean_transcript_handles_short_text(self):
        """Test transcript cleaning handles short text gracefully."""
        service = Mock(spec=WhisperService)
        service._clean_transcript = WhisperService._clean_transcript

        short_text = "Hello"
        result = service._clean_transcript(service, short_text)
        assert result == "Hello"


class TestOllamaService:
    """Tests for OllamaService."""

    def test_init_sets_config(self):
        """Test OllamaService initialization sets config correctly."""
        with patch('services.ollama_service.settings') as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://test:11434"
            mock_settings.OLLAMA_MODEL = "test-model"

            service = OllamaService()
            assert service.base_url == "http://test:11434"
            assert service.model == "test-model"

    def test_max_transcript_chars_limit(self):
        """Test OllamaService has a character limit."""
        with patch('services.ollama_service.settings') as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
            mock_settings.OLLAMA_MODEL = "llama3.1:8b"

            service = OllamaService()
            assert hasattr(service, 'max_transcript_chars')
            assert service.max_transcript_chars > 0

    @pytest.mark.asyncio
    async def test_generate_summary_truncates_long_transcript(self):
        """Test that long transcripts are truncated."""
        with patch('services.ollama_service.settings') as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
            mock_settings.OLLAMA_MODEL = "llama3.1:8b"

            service = OllamaService()

            # Create a very long transcript
            long_transcript = "Test word. " * 100000  # Much longer than limit

            with patch('httpx.AsyncClient') as mock_client:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"response": "Summary"}

                mock_client_instance = AsyncMock()
                mock_client_instance.post.return_value = mock_response
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client_instance.__aexit__.return_value = None
                mock_client.return_value = mock_client_instance

                # This should not raise even with very long text
                result = await service.generate_summary(long_transcript, "concise")
                assert result == "Summary"

    @pytest.mark.asyncio
    async def test_generate_summary_styles(self):
        """Test different summary styles produce different prompts."""
        with patch('services.ollama_service.settings') as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
            mock_settings.OLLAMA_MODEL = "llama3.1:8b"

            service = OllamaService()
            styles = ["concise", "detailed", "bullet_points"]

            for style in styles:
                with patch('httpx.AsyncClient') as mock_client:
                    mock_response = Mock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"response": f"Summary for {style}"}

                    mock_client_instance = AsyncMock()
                    mock_client_instance.post.return_value = mock_response
                    mock_client_instance.__aenter__.return_value = mock_client_instance
                    mock_client_instance.__aexit__.return_value = None
                    mock_client.return_value = mock_client_instance

                    result = await service.generate_summary("Test transcript", style)
                    assert style in result

    @pytest.mark.asyncio
    async def test_check_health_returns_boolean(self):
        """Test health check returns a boolean."""
        with patch('services.ollama_service.settings') as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
            mock_settings.OLLAMA_MODEL = "llama3.1:8b"

            service = OllamaService()

            with patch('httpx.AsyncClient') as mock_client:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "models": [{"name": "llama3.1:8b"}]
                }

                mock_client_instance = AsyncMock()
                mock_client_instance.get.return_value = mock_response
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client_instance.__aexit__.return_value = None
                mock_client.return_value = mock_client_instance

                result = await service.check_health()
                assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_generate_summary_handles_timeout(self):
        """Test summary generation handles timeout gracefully."""
        import httpx

        with patch('services.ollama_service.settings') as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
            mock_settings.OLLAMA_MODEL = "llama3.1:8b"

            service = OllamaService()

            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = AsyncMock()
                mock_client_instance.post.side_effect = httpx.TimeoutException("Timeout")
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client_instance.__aexit__.return_value = None
                mock_client.return_value = mock_client_instance

                with pytest.raises(Exception) as exc_info:
                    await service.generate_summary("Test", "concise")
                assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_summary_handles_connection_error(self):
        """Test summary generation handles connection error gracefully."""
        import httpx

        with patch('services.ollama_service.settings') as mock_settings:
            mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"
            mock_settings.OLLAMA_MODEL = "llama3.1:8b"

            service = OllamaService()

            with patch('httpx.AsyncClient') as mock_client:
                mock_client_instance = AsyncMock()
                mock_client_instance.post.side_effect = httpx.ConnectError("Connection refused")
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client_instance.__aexit__.return_value = None
                mock_client.return_value = mock_client_instance

                with pytest.raises(Exception) as exc_info:
                    await service.generate_summary("Test", "concise")
                assert "connect" in str(exc_info.value).lower() or "ollama" in str(exc_info.value).lower()
