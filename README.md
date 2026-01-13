# Audtext - Audio Transcription & Summarization

A modern web application that transcribes audio files using OpenAI Whisper locally and generates AI-powered summaries with Ollama.

![Audtext](https://img.shields.io/badge/Powered%20by-Whisper%20%26%20Ollama-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Local Processing** - All transcription happens on your machine. Your audio never leaves your computer.
- **Long Audio Support** - Handle audio files up to 1 hour long with real-time progress tracking.
- **AI Summaries** - Generate intelligent summaries using local LLM with Ollama.
- **Multiple Export Formats** - Export transcripts as TXT, SRT, VTT, or JSON.
- **Beautiful UI** - Modern, responsive interface built with React and Tailwind CSS.
- **Real-time Progress** - WebSocket-based progress updates during transcription.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | FastAPI + Python 3.11+ |
| Transcription | faster-whisper (CPU-optimized) |
| Summarization | Ollama (llama3.1:8b) |

## Prerequisites

Before running Audtext, make sure you have:

1. **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download Node.js](https://nodejs.org/)
3. **FFmpeg** - Required for audio processing
   - Windows: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/)
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
4. **Ollama** - For AI summaries
   - Download from [ollama.ai](https://ollama.ai/)
   - After installing, run: `ollama pull llama3.1:8b`

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/DandaAkhilReddy/Audtext.git
cd Audtext
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Set up the frontend

```bash
cd ../frontend
npm install
```

## Running the Application

### 1. Start Ollama (in a separate terminal)

```bash
ollama serve
```

### 2. Start the backend

```bash
cd backend
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
uvicorn main:app --reload --port 8000
```

### 3. Start the frontend

```bash
cd frontend
npm run dev
```

### 4. Open in browser

Navigate to [http://localhost:5173](http://localhost:5173)

## Usage

1. **Upload Audio** - Drag and drop or click to select an audio file (MP3, WAV, M4A, FLAC, OGG, WEBM)
2. **Wait for Transcription** - Watch the real-time progress bar as Whisper processes your audio
3. **View Transcript** - See the full transcript with timestamps
4. **Generate Summary** - Click to generate an AI-powered summary with Ollama
5. **Export** - Download your transcript in various formats (TXT, SRT, VTT, JSON)

## Configuration

### Whisper Model Selection

Edit `backend/core/config.py` to change the Whisper model:

```python
WHISPER_MODEL: str = "base"  # Options: tiny, base, small, medium, large
```

| Model | RAM | Speed (1hr audio) | Quality |
|-------|-----|-------------------|---------|
| tiny | 1GB | ~5 min | Fair |
| base | 1.5GB | ~10 min | Good |
| small | 2.5GB | ~20 min | Better |
| medium | 5GB | ~40 min | Great |

### Ollama Model

Change the summarization model in `backend/core/config.py`:

```python
OLLAMA_MODEL: str = "llama3.1:8b"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload audio file |
| `/api/status/{task_id}` | GET | Get transcription progress |
| `/api/result/{task_id}` | GET | Get full transcript |
| `/api/summarize` | POST | Generate summary |
| `/api/export/{format}/{task_id}` | GET | Export transcript |
| `/ws/progress/{task_id}` | WebSocket | Real-time progress |

## Project Structure

```
Audtext/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── api/routes/          # API endpoints
│   ├── services/            # Whisper & Ollama services
│   ├── core/                # Configuration & WebSocket
│   └── models/              # Pydantic schemas
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   └── services/        # API client
│   └── ...
└── uploads/                 # Temporary audio storage
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Akhil Reddy** - [GitHub](https://github.com/DandaAkhilReddy)

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Optimized inference
- [Ollama](https://ollama.ai/) - Local LLM runtime
