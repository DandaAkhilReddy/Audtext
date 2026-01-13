from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from api.routes.transcription import transcription_store, TaskStatus

router = APIRouter(prefix="/api/export", tags=["export"])


def format_timestamp_srt(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Convert seconds to WebVTT timestamp format (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


@router.get("/txt/{task_id}")
async def export_txt(task_id: str):
    """Export transcript as plain text."""
    if task_id not in transcription_store:
        raise HTTPException(status_code=404, detail="Task not found")

    result = transcription_store[task_id]
    if result.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Transcription not complete")

    return PlainTextResponse(
        content=result.full_text or "",
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="transcript_{task_id}.txt"'
        }
    )


@router.get("/srt/{task_id}")
async def export_srt(task_id: str):
    """Export transcript as SRT subtitles."""
    if task_id not in transcription_store:
        raise HTTPException(status_code=404, detail="Task not found")

    result = transcription_store[task_id]
    if result.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Transcription not complete")

    srt_content = []
    for i, segment in enumerate(result.segments, 1):
        start_time = format_timestamp_srt(segment.start)
        end_time = format_timestamp_srt(segment.end)
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(segment.text)
        srt_content.append("")

    return PlainTextResponse(
        content="\n".join(srt_content),
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="transcript_{task_id}.srt"'
        }
    )


@router.get("/vtt/{task_id}")
async def export_vtt(task_id: str):
    """Export transcript as WebVTT subtitles."""
    if task_id not in transcription_store:
        raise HTTPException(status_code=404, detail="Task not found")

    result = transcription_store[task_id]
    if result.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Transcription not complete")

    vtt_content = ["WEBVTT", ""]
    for segment in result.segments:
        start_time = format_timestamp_vtt(segment.start)
        end_time = format_timestamp_vtt(segment.end)
        vtt_content.append(f"{start_time} --> {end_time}")
        vtt_content.append(segment.text)
        vtt_content.append("")

    return PlainTextResponse(
        content="\n".join(vtt_content),
        media_type="text/vtt",
        headers={
            "Content-Disposition": f'attachment; filename="transcript_{task_id}.vtt"'
        }
    )


@router.get("/json/{task_id}")
async def export_json(task_id: str):
    """Export full transcript data as JSON."""
    if task_id not in transcription_store:
        raise HTTPException(status_code=404, detail="Task not found")

    result = transcription_store[task_id]
    if result.status != TaskStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Transcription not complete")

    return result
