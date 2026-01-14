from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str

class TranscriptionResult(BaseModel):
    task_id: str
    status: TaskStatus
    progress: float = 0.0
    message: str = ""
    language: Optional[str] = None
    duration: Optional[float] = None
    segments: List[TranscriptSegment] = []
    full_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class SummaryRequest(BaseModel):
    task_id: str
    style: str = "concise"  # concise, detailed, bullet_points

class SummaryResponse(BaseModel):
    task_id: str
    summary: str
    style: str

class UploadResponse(BaseModel):
    task_id: str
    filename: str
    message: str

class ProgressUpdate(BaseModel):
    task_id: str
    status: TaskStatus
    progress: float
    message: str
    current_segment: Optional[int] = None
    total_segments: Optional[int] = None
