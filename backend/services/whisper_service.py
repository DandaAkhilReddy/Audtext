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
                message=str(e)
            )

    def _transcribe_sync(
        self,
        audio_path: str,
        task_id: str,
        progress_callback: Optional[Callable] = None
    ) -> TranscriptionResult:
        """
        Synchronous transcription with progress tracking.
        """
        segments_list = []
        full_text_parts = []

        # Transcribe with VAD filter to skip silence
        segments, info = self._model.transcribe(
            audio_path,
            beam_size=1,  # Fastest for CPU
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=200
            )
        )

        # Process segments
        segment_id = 0
        total_duration = info.duration if info.duration else 0

        for segment in segments:
            segment_data = TranscriptSegment(
                id=segment_id,
                start=segment.start,
                end=segment.end,
                text=segment.text.strip()
            )
            segments_list.append(segment_data)
            full_text_parts.append(segment.text.strip())

            # Calculate progress
            if total_duration > 0 and progress_callback:
                progress = min((segment.end / total_duration) * 100, 99.0)
                progress_callback(
                    task_id=task_id,
                    progress=progress,
                    message=f"Transcribing... {int(progress)}%",
                    current_segment=segment_id
                )

            segment_id += 1

        # Final progress update
        if progress_callback:
            progress_callback(
                task_id=task_id,
                progress=100.0,
                message="Transcription complete!",
                current_segment=segment_id
            )

        return TranscriptionResult(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            progress=100.0,
            message="Transcription complete!",
            language=info.language,
            duration=info.duration,
            segments=segments_list,
            full_text=" ".join(full_text_parts)
        )

# Singleton instance
whisper_service = WhisperService()
