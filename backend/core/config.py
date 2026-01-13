from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Audtext"
    DEBUG: bool = True

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # Whisper settings
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium
    WHISPER_DEVICE: str = "cpu"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_CPU_THREADS: int = 4

    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"

    # File settings
    MAX_FILE_SIZE_MB: int = 500
    ALLOWED_EXTENSIONS: list = ["mp3", "wav", "m4a", "flac", "ogg", "webm", "mp4"]

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
