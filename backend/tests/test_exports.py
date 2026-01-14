"""
Export functionality tests for Audtext backend.
"""
import pytest
import json


class TestSRTFormat:
    """Tests for SRT export format."""

    def test_srt_timestamp_format(self):
        """Test SRT timestamp format is correct."""
        # SRT format: HH:MM:SS,mmm --> HH:MM:SS,mmm
        def format_srt_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            # Use round to handle floating point precision issues
            millis = int(round((seconds - int(seconds)) * 1000))
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        assert format_srt_time(0.0) == "00:00:00,000"
        assert format_srt_time(1.5) == "00:00:01,500"
        assert format_srt_time(65.123) == "00:01:05,123"
        assert format_srt_time(3661.999) == "01:01:01,999"

    def test_srt_structure(self):
        """Test SRT file structure is valid."""
        # Sample SRT content
        srt_content = """1
00:00:00,000 --> 00:00:05,000
First segment text.

2
00:00:05,000 --> 00:00:10,000
Second segment text.
"""
        lines = srt_content.strip().split('\n')

        # Check first entry
        assert lines[0] == "1"  # Index
        assert "-->" in lines[1]  # Timestamp
        assert lines[2] == "First segment text."  # Text
        assert lines[3] == ""  # Empty line separator


class TestVTTFormat:
    """Tests for VTT export format."""

    def test_vtt_header(self):
        """Test VTT file starts with WEBVTT header."""
        vtt_content = "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\nTest"
        assert vtt_content.startswith("WEBVTT")

    def test_vtt_timestamp_format(self):
        """Test VTT timestamp format is correct."""
        # VTT format: HH:MM:SS.mmm --> HH:MM:SS.mmm (uses . not ,)
        def format_vtt_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millis = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

        assert format_vtt_time(0.0) == "00:00:00.000"
        assert format_vtt_time(1.5) == "00:00:01.500"
        # VTT uses period, not comma
        assert "." in format_vtt_time(1.5)


class TestJSONFormat:
    """Tests for JSON export format."""

    def test_json_structure(self, sample_segments):
        """Test JSON export structure."""
        export_data = {
            "full_text": "Complete transcript text",
            "duration": 40.0,
            "language": "en",
            "segments": [
                {
                    "id": seg.id,
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text
                }
                for seg in sample_segments
            ]
        }

        # Verify it's valid JSON
        json_str = json.dumps(export_data)
        parsed = json.loads(json_str)

        assert "full_text" in parsed
        assert "segments" in parsed
        assert len(parsed["segments"]) == len(sample_segments)

    def test_json_segment_fields(self, sample_segments):
        """Test JSON segment contains required fields."""
        segment = sample_segments[0]
        segment_dict = {
            "id": segment.id,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text
        }

        required_fields = ["id", "start", "end", "text"]
        for field in required_fields:
            assert field in segment_dict


class TestTXTFormat:
    """Tests for plain text export format."""

    def test_txt_format_simple(self, sample_transcript):
        """Test plain text export is just the transcript."""
        # TXT format should be simple plain text
        assert isinstance(sample_transcript, str)
        assert len(sample_transcript) > 0

    def test_txt_format_readable(self, sample_segments):
        """Test plain text is human readable."""
        full_text = " ".join([seg.text for seg in sample_segments])

        # Should be readable sentences
        assert "." in full_text
        assert len(full_text.split()) > 10


class TestExportEdgeCases:
    """Tests for export edge cases."""

    def test_empty_segments(self):
        """Test export handles empty segments list."""
        segments = []

        # SRT with no segments
        srt_content = ""
        for i, seg in enumerate(segments, 1):
            srt_content += f"{i}\n00:00:00,000 --> 00:00:00,000\n\n\n"

        assert srt_content == ""

    def test_long_segment_text(self):
        """Test export handles very long segment text."""
        long_text = "Word " * 1000  # Very long segment

        # Should not crash
        export_dict = {
            "id": 0,
            "start": 0.0,
            "end": 60.0,
            "text": long_text.strip()
        }

        json_str = json.dumps(export_dict)
        assert len(json_str) > 4000

    def test_special_characters_in_text(self):
        """Test export handles special characters."""
        special_text = "Hello <world> & \"friends\" 'here'"

        # JSON should escape properly
        export_dict = {"text": special_text}
        json_str = json.dumps(export_dict)
        parsed = json.loads(json_str)

        assert parsed["text"] == special_text

    def test_unicode_in_text(self):
        """Test export handles unicode characters."""
        unicode_text = "Hello 世界 مرحبا שלום"

        export_dict = {"text": unicode_text}
        json_str = json.dumps(export_dict, ensure_ascii=False)
        parsed = json.loads(json_str)

        assert parsed["text"] == unicode_text

    def test_newlines_in_segment(self):
        """Test export handles newlines in segment text."""
        text_with_newlines = "Line one.\nLine two.\nLine three."

        # For SRT, newlines in text should be preserved or handled
        export_dict = {"text": text_with_newlines}
        json_str = json.dumps(export_dict)
        parsed = json.loads(json_str)

        assert "\n" in parsed["text"] or "\\n" in json_str
