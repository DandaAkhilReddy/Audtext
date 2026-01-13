from fastapi import APIRouter, HTTPException
from models.schemas import SummaryRequest, SummaryResponse
from services.ollama_service import ollama_service
from api.routes.transcription import transcription_store, TaskStatus

router = APIRouter(prefix="/api", tags=["summarization"])


@router.post("/summarize", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest):
    """Generate a summary from a completed transcription."""
    # Check if transcription exists
    if request.task_id not in transcription_store:
        raise HTTPException(status_code=404, detail="Transcription not found")

    result = transcription_store[request.task_id]

    # Check if transcription is complete
    if result.status != TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Transcription not complete yet"
        )

    # Check if we have text to summarize
    if not result.full_text:
        raise HTTPException(
            status_code=400,
            detail="No transcript text available"
        )

    # Generate summary using Ollama
    try:
        summary = await ollama_service.generate_summary(
            result.full_text,
            request.style
        )

        return SummaryResponse(
            task_id=request.task_id,
            summary=summary,
            style=request.style
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.get("/ollama/health")
async def check_ollama_health():
    """Check if Ollama is running and model is available."""
    is_healthy = await ollama_service.check_health()
    return {
        "status": "healthy" if is_healthy else "unavailable",
        "model": ollama_service.model,
        "message": "Ollama is ready" if is_healthy else "Ollama is not running or model not found"
    }
