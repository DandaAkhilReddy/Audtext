"""
API endpoint tests for Audtext backend.
"""
import pytest
import json
from unittest.mock import patch, AsyncMock, Mock
from fastapi.testclient import TestClient
from models.schemas import TaskStatus, TranscriptionResult, TranscriptSegment


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns app info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "Audtext" in data["name"]

    def test_health_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestTranscriptionEndpoints:
    """Tests for transcription-related endpoints."""

    def test_upload_without_file(self, client):
        """Test upload endpoint without file returns error."""
        response = client.post("/api/upload")
        assert response.status_code == 422  # Unprocessable Entity

    def test_upload_invalid_file_type(self, client, tmp_path):
        """Test upload endpoint with invalid file type."""
        # Create a text file
        text_file = tmp_path / "test.txt"
        text_file.write_text("This is not an audio file")

        with open(text_file, "rb") as f:
            response = client.post(
                "/api/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        # Should be rejected or fail during processing
        assert response.status_code in [400, 422, 500]

    def test_get_status_nonexistent_task(self, client):
        """Test getting status of non-existent task."""
        response = client.get("/api/status/nonexistent-task-id")
        assert response.status_code == 404

    def test_get_result_nonexistent_task(self, client):
        """Test getting result of non-existent task."""
        response = client.get("/api/result/nonexistent-task-id")
        assert response.status_code == 404


class TestSummaryEndpoints:
    """Tests for summary-related endpoints."""

    def test_summary_without_body(self, client):
        """Test summary endpoint without request body."""
        response = client.post("/api/summarize")
        assert response.status_code == 422

    def test_summary_nonexistent_task(self, client):
        """Test summary endpoint with non-existent task."""
        response = client.post(
            "/api/summarize",
            json={"task_id": "nonexistent-task", "style": "concise"}
        )
        # Should return 404 for non-existent task
        assert response.status_code == 404

    @patch('api.routes.summarization.transcription_store', {
        'test-task': Mock(
            status=TaskStatus.COMPLETED,
            full_text="",
            segments=[]
        )
    })
    def test_summary_with_empty_transcript(self, client):
        """Test summary endpoint with empty transcript text."""
        response = client.post(
            "/api/summarize",
            json={"task_id": "test-task", "style": "concise"}
        )
        # Should return error for empty transcript
        assert response.status_code == 400

    @patch('api.routes.summarization.transcription_store', {
        'test-task': Mock(
            status=TaskStatus.COMPLETED,
            full_text="This is a test transcript with some content to summarize.",
            segments=[]
        )
    })
    def test_summary_with_valid_transcript(self, client):
        """Test summary endpoint with valid transcript."""
        response = client.post(
            "/api/summarize",
            json={"task_id": "test-task", "style": "concise"}
        )
        # May succeed or fail depending on Ollama availability
        assert response.status_code in [200, 500]

    @patch('api.routes.summarization.transcription_store', {
        'test-task': Mock(
            status=TaskStatus.COMPLETED,
            full_text="This is a test transcript with some content to summarize.",
            segments=[]
        )
    })
    def test_summary_styles(self, client):
        """Test different summary styles are accepted."""
        styles = ["concise", "detailed", "bullet_points"]

        for style in styles:
            response = client.post(
                "/api/summarize",
                json={"task_id": "test-task", "style": style}
            )
            # Request should be accepted (may fail due to Ollama not running)
            assert response.status_code in [200, 500]


class TestExportEndpoints:
    """Tests for export-related endpoints."""

    @patch('api.routes.export.transcription_store', {
        'test-task': Mock(
            status=TaskStatus.COMPLETED,
            full_text="Test transcript text",
            segments=[
                Mock(id=0, start=0.0, end=5.0, text="Test segment one."),
                Mock(id=1, start=5.0, end=10.0, text="Test segment two.")
            ],
            duration=10.0,
            language="en"
        )
    })
    def test_export_txt(self, client):
        """Test TXT export format."""
        response = client.get("/api/export/txt/test-task")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")

    @patch('api.routes.export.transcription_store', {
        'test-task': Mock(
            status=TaskStatus.COMPLETED,
            full_text="Test transcript text",
            segments=[
                Mock(id=0, start=0.0, end=5.0, text="Test segment one."),
                Mock(id=1, start=5.0, end=10.0, text="Test segment two.")
            ],
            duration=10.0,
            language="en"
        )
    })
    def test_export_srt(self, client):
        """Test SRT export format."""
        response = client.get("/api/export/srt/test-task")
        assert response.status_code == 200
        assert "text/plain" in response.headers.get("content-type", "")
        # Check SRT format structure
        content = response.text
        assert "1\n" in content  # SRT index
        assert "-->" in content  # SRT timestamp separator

    @patch('api.routes.export.transcription_store', {
        'test-task': Mock(
            status=TaskStatus.COMPLETED,
            full_text="Test transcript text",
            segments=[
                Mock(id=0, start=0.0, end=5.0, text="Test segment one."),
                Mock(id=1, start=5.0, end=10.0, text="Test segment two.")
            ],
            duration=10.0,
            language="en"
        )
    })
    def test_export_vtt(self, client):
        """Test VTT export format."""
        response = client.get("/api/export/vtt/test-task")
        assert response.status_code == 200
        content = response.text
        assert "WEBVTT" in content  # VTT header

    @patch('api.routes.export.transcription_store')
    def test_export_json(self, mock_store, client):
        """Test JSON export format."""
        # Create proper Pydantic model for JSON serialization
        mock_store.__contains__ = lambda self, key: key == 'test-task'
        mock_store.__getitem__ = lambda self, key: TranscriptionResult(
            task_id='test-task',
            status=TaskStatus.COMPLETED,
            progress=100.0,
            message="Complete",
            full_text="Test transcript text",
            segments=[
                TranscriptSegment(id=0, start=0.0, end=5.0, text="Test segment one."),
                TranscriptSegment(id=1, start=5.0, end=10.0, text="Test segment two.")
            ],
            duration=10.0,
            language="en"
        )
        response = client.get("/api/export/json/test-task")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")
        # Verify it's valid JSON
        data = response.json()
        assert "segments" in data or "full_text" in data

    def test_export_nonexistent_task(self, client):
        """Test export for non-existent task."""
        response = client.get("/api/export/txt/nonexistent")
        assert response.status_code == 404

    def test_export_invalid_format(self, client):
        """Test export with invalid format."""
        response = client.get("/api/export/invalid/test-task")
        assert response.status_code in [400, 404, 422]


class TestOllamaHealth:
    """Tests for Ollama health check."""

    def test_ollama_health_endpoint(self, client):
        """Test Ollama health check endpoint."""
        response = client.get("/api/ollama/health")
        # Should return status regardless of Ollama availability
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model" in data
        assert "message" in data
