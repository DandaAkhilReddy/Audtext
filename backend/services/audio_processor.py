import os
import uuid
from pathlib import Path
from core.config import settings

class AudioProcessor:
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """Get file extension in lowercase."""
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    @staticmethod
    def is_valid_extension(filename: str) -> bool:
        """Check if file extension is allowed."""
        ext = AudioProcessor.get_file_extension(filename)
        return ext in settings.ALLOWED_EXTENSIONS

    @staticmethod
    def generate_task_id() -> str:
        """Generate unique task ID."""
        return str(uuid.uuid4())[:8]

    @staticmethod
    def get_upload_path(task_id: str, filename: str) -> Path:
        """Get path for uploaded file."""
        ext = AudioProcessor.get_file_extension(filename)
        return settings.UPLOAD_DIR / f"{task_id}.{ext}"

    @staticmethod
    async def save_upload(file_content: bytes, task_id: str, filename: str) -> str:
        """Save uploaded file and return path."""
        file_path = AudioProcessor.get_upload_path(task_id, filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        return str(file_path)

    @staticmethod
    def cleanup_file(file_path: str) -> None:
        """Remove temporary file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

audio_processor = AudioProcessor()
