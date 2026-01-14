import os
import asyncio
from pathlib import Path
from typing import Callable, Optional
from faster_whisper import WhisperModel
from core.config import settings
from models.schemas import TranscriptSegment, TranscriptionResult, TaskStatus

class WhisperService:
    _instance: Optional['WhisperService'] = None
    _model: Optional[WhisperModel] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            print(f"Loading Whisper model: {settings.WHISPER_MODEL}...")
            self._model = WhisperModel(
                settings.WHISPER_MODEL,
                device=settings.WHISPER_DEVICE,
                compute_type=settings.WHISPER_COMPUTE_TYPE,
                cpu_threads=settings.WHISPER_CPU_THREADS
            )
            print("Whisper model loaded successfully!")

    async def transcribe(
        self,
        audio_path: str,
        task_id: str,
        progress_callback: Optional[Callable] = None
    ) -> TranscriptionResult:
        """
        Transcribe an audio file with progress updates.
        """
        try:
            # Run transcription in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                audio_path,
                task_id,
                progress_callback
            )
            return result
        except Exception as e:
            return TranscriptionResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                message=f"Transcription failed: {str(e)}"
            )

    def _transcribe_sync(
        self,
        audio_path: str,
        task_id: str,
        progress_callback: Optional[Callable] = None
    ) -> TranscriptionResult:
        """
        Synchronous transcription with progress tracking.
        Optimized for accuracy on long files.
        """
        segments_list = []
        full_text_parts = []

        try:
            # Transcribe with optimized settings for accuracy
            # beam_size=5 provides better accuracy than beam_size=1
            # vad_filter helps skip silence and improves accuracy
            # condition_on_previous_text helps with context continuity
            segments, info = self._model.transcribe(
                audio_path,
                beam_size=5,  # Better accuracy (1=fast, 5=balanced, 10=best)
                best_of=5,    # Number of candidates to consider
                patience=1.0,  # Beam search patience factor
                length_penalty=1.0,
                vad_filter=True,
                vad_parameters=dict(
                    threshold=0.5,  # Speech detection threshold
                    min_speech_duration_ms=250,
                    max_speech_duration_s=float('inf'),
                    min_silence_duration_ms=500,
                    speech_pad_ms=400  # Padding around speech
                ),
                condition_on_previous_text=True,  # Use context from previous segments
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.6,
                word_timestamps=False,  # Disable for speed, enable if needed
            )

            # Process segments
            segment_id = 0
            total_duration = info.duration if info.duration else 0

            for segment in segments:
                text = segment.text.strip()
                if text:  # Only add non-empty segments
                    segment_data = TranscriptSegment(
                        id=segment_id,
                        start=round(segment.start, 2),
                        end=round(segment.end, 2),
                        text=text
                    )
                    segments_list.append(segment_data)
                    full_text_parts.append(text)
                    segment_id += 1

                # Calculate progress
                if total_duration > 0 and progress_callback:
                    progress = min((segment.end / total_duration) * 100, 99.0)
                    progress_callback(
                        task_id=task_id,
                        progress=progress,
                        message=f"Transcribing... {int(progress)}%",
                        current_segment=segment_id
                    )

            # Final progress update
            if progress_callback:
                progress_callback(
                    task_id=task_id,
                    progress=100.0,
                    message="Transcription complete!",
                    current_segment=segment_id
                )

            # Join text with proper spacing
            full_text = " ".join(full_text_parts)

            # Clean up common transcription artifacts
            full_text = self._clean_transcript(full_text)

            return TranscriptionResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                progress=100.0,
                message="Transcription complete!",
                language=info.language,
                duration=round(info.duration, 2) if info.duration else None,
                segments=segments_list,
                full_text=full_text
            )

        except Exception as e:
            return TranscriptionResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                message=f"Transcription error: {str(e)}"
            )

    def _clean_transcript(self, text: str) -> str:
        """Clean up common transcription artifacts."""
        import re

        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)

        # Remove repeated phrases (common hallucination)
        # This is a simple heuristic - repeated 3+ word phrases
        words = text.split()
        if len(words) > 10:
            # Check for repeated patterns at the end (hallucination symptom)
            for pattern_len in range(3, 8):
                if len(words) >= pattern_len * 3:
                    last_pattern = ' '.join(words[-pattern_len:])
                    prev_pattern = ' '.join(words[-pattern_len*2:-pattern_len])
                    if last_pattern == prev_pattern:
                        # Remove the repeated pattern
                        words = words[:-pattern_len]
                        text = ' '.join(words)

        return text.strip()

# Singleton instance
whisper_service = WhisperService()
