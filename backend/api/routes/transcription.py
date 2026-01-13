from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict
import asyncio

from models.schemas import (
    UploadResponse, TranscriptionResult, TaskStatus, ProgressUpdate
)
from services.whisper_service import whisper_service
from services.audio_processor import audio_processor
from core.websocket import manager
from core.config import settings

router = APIRouter(prefix="/api", tags=["transcription"])

# In-memory storage for transcription results
transcription_store: Dict[str, TranscriptionResult] = {}

def progress_callback(task_id: str, progress: float, message: str, current_segment: int = None):
    """Callback to update progress (runs in sync context)."""
    if task_id in transcription_store:
        transcription_store[task_id].progress = progress
        transcription_store[task_id].message = message

async def run_transcription(task_id: str, file_path: str):
    """Background task to run transcription."""
    try:
        # Update status to processing
        transcription_store[task_id].status = TaskStatus.PROCESSING
        transcription_store[task_id].message = "Starting transcription..."

        # Send initial progress via WebSocket
        await manager.send_progress(task_id, 0, "Starting transcription...")

        # Create async progress callback wrapper
        async def async_progress(task_id: str, progress: float, message: str, current_segment: int = None):
            progress_callback(task_id, progress, message, current_segment)
            await manager.send_progress(task_id, progress, message, "processing", current_segment)

        # Run transcription
        result = await whisper_service.transcribe(
            file_path,
            task_id,
            lambda **kwargs: asyncio.create_task(async_progress(**kwargs))
        )

        # Store result
        transcription_store[task_id] = result

        # Send completion via WebSocket
        await manager.send_progress(
            task_id, 100, "Transcription complete!", "completed"
        )

    except Exception as e:
        transcription_store[task_id].status = TaskStatus.FAILED
        transcription_store[task_id].message = str(e)
        await manager.send_progress(task_id, 0, f"Error: {str(e)}", "failed")

    finally:
        # Cleanup uploaded file
        audio_processor.cleanup_file(file_path)


@router.post("/upload", response_model=UploadResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload an audio file for transcription."""
    # Validate file extension
    if not audio_processor.is_valid_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Check file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
        )

    # Generate task ID and save file
    task_id = audio_processor.generate_task_id()
    file_path = await audio_processor.save_upload(content, task_id, file.filename)

    # Initialize transcription result
    transcription_store[task_id] = TranscriptionResult(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="File uploaded, waiting to start..."
    )

    # Start transcription in background
    background_tasks.add_task(run_transcription, task_id, file_path)

    return UploadResponse(
        task_id=task_id,
        filename=file.filename,
        message="File uploaded successfully. Transcription started."
    )


@router.get("/status/{task_id}", response_model=ProgressUpdate)
async def get_status(task_id: str):
    """Get transcription progress status."""
    if task_id not in transcription_store:
        raise HTTPException(status_code=404, detail="Task not found")

    result = transcription_store[task_id]
    return ProgressUpdate(
        task_id=task_id,
        status=result.status,
        progress=result.progress,
        message=result.message
    )


@router.get("/result/{task_id}", response_model=TranscriptionResult)
async def get_result(task_id: str):
    """Get full transcription result."""
    if task_id not in transcription_store:
        raise HTTPException(status_code=404, detail="Task not found")

    result = transcription_store[task_id]
    if result.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Transcription not complete. Status: {result.status}"
        )

    return result
