"""
Pytest configuration and fixtures for Audtext backend tests.
"""
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from models.schemas import TranscriptSegment, TranscriptionResult, TaskStatus


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_transcript():
    """Sample transcript text for testing."""
    return """Hello and welcome to this test audio recording.
    Today we're going to discuss several important topics.
    First, let's talk about the weather. The weather has been quite nice lately.
    Second, we'll discuss current events. There have been many interesting developments.
    Finally, we'll wrap up with some concluding thoughts.
    Thank you for listening to this test recording."""


@pytest.fixture
def sample_segments():
    """Sample transcript segments for testing."""
    return [
        TranscriptSegment(id=0, start=0.0, end=5.0, text="Hello and welcome to this test audio recording."),
        TranscriptSegment(id=1, start=5.0, end=10.0, text="Today we're going to discuss several important topics."),
        TranscriptSegment(id=2, start=10.0, end=15.0, text="First, let's talk about the weather."),
        TranscriptSegment(id=3, start=15.0, end=20.0, text="The weather has been quite nice lately."),
        TranscriptSegment(id=4, start=20.0, end=25.0, text="Second, we'll discuss current events."),
        TranscriptSegment(id=5, start=25.0, end=30.0, text="There have been many interesting developments."),
        TranscriptSegment(id=6, start=30.0, end=35.0, text="Finally, we'll wrap up with some concluding thoughts."),
        TranscriptSegment(id=7, start=35.0, end=40.0, text="Thank you for listening to this test recording."),
    ]


@pytest.fixture
def sample_transcription_result(sample_segments, sample_transcript):
    """Sample transcription result for testing."""
    return TranscriptionResult(
        task_id="test-task-123",
        status=TaskStatus.COMPLETED,
        progress=100.0,
        message="Transcription complete!",
        language="en",
        duration=40.0,
        segments=sample_segments,
        full_text=sample_transcript
    )


@pytest.fixture
def mock_whisper_service():
    """Mock WhisperService for testing without actual model."""
    with patch('services.whisper_service.WhisperService') as mock:
        mock_instance = Mock()
        mock_instance.transcribe = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_ollama_service():
    """Mock OllamaService for testing without actual Ollama."""
    with patch('services.ollama_service.OllamaService') as mock:
        mock_instance = Mock()
        mock_instance.generate_summary = AsyncMock(return_value="This is a test summary.")
        mock_instance.check_health = AsyncMock(return_value=True)
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def temp_audio_file(tmp_path):
    """Create a temporary audio file for testing."""
    # Create a minimal WAV file header (empty audio)
    audio_file = tmp_path / "test_audio.wav"
    # Minimal WAV header for empty file
    wav_header = bytes([
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x00, 0x00, 0x00,  # File size - 8
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # Subchunk1Size (16)
        0x01, 0x00,              # AudioFormat (PCM)
        0x01, 0x00,              # NumChannels (1)
        0x44, 0xAC, 0x00, 0x00,  # SampleRate (44100)
        0x88, 0x58, 0x01, 0x00,  # ByteRate
        0x02, 0x00,              # BlockAlign
        0x10, 0x00,              # BitsPerSample (16)
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x00, 0x00, 0x00, 0x00,  # Subchunk2Size (0 - empty)
    ])
    audio_file.write_bytes(wav_header)
    return str(audio_file)
