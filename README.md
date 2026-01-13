# Audtext - Audio Transcription & Summarization

A modern web application that transcribes audio files (up to 1 hour) using OpenAI Whisper locally and generates AI-powered summaries with Ollama. All processing happens on your machine - your audio never leaves your computer.

![Audtext](https://img.shields.io/badge/Powered%20by-Whisper%20%26%20Ollama-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Local Processing** - All transcription happens on your machine. Your audio never leaves your computer.
- **Long Audio Support** - Handle audio files up to 1 hour long with real-time progress tracking.
- **AI Summaries** - Generate intelligent summaries using local LLM with Ollama (no API costs).
- **Multiple Export Formats** - Export transcripts as TXT, SRT (subtitles), VTT, or JSON.
- **Beautiful UI** - Modern, responsive interface built with React and Tailwind CSS.
- **No File Size Limit** - Upload audio files of any size.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | FastAPI + Python 3.11+ |
| Transcription | faster-whisper (CPU-optimized) |
| Summarization | Ollama (llama3.1:8b) |

---

## Prerequisites

Before running Audtext, install the following:

### 1. Python 3.11+
- Download from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

### 2. Node.js 18+
- Download from [nodejs.org](https://nodejs.org/)

### 3. FFmpeg (Required for audio processing)
```bash
# Windows (using winget)
winget install ffmpeg

# Windows (using chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg
```

### 4. Ollama (Required for AI Summaries)
1. Download from [ollama.ai](https://ollama.ai/)
2. Install it
3. Open a terminal and download the model:
```bash
ollama pull llama3.1:8b
```

---

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/DandaAkhilReddy/Audtext.git
cd Audtext
```

### Step 2: Set Up the Backend
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Set Up the Frontend
```bash
cd ../frontend
npm install
```

---

## Running the Application

You need **3 terminals** to run the full application:

### Terminal 1: Start Ollama
```bash
ollama serve
```
> Note: If you see "address already in use", Ollama is already running. That's fine!

### Terminal 2: Start the Backend
```bash
cd Audtext/backend

# Activate virtual environment first
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start the server
uvicorn main:app --reload --port 8000
```

### Terminal 3: Start the Frontend
```bash
cd Audtext/frontend
npm run dev
```

### Open the App
Navigate to **http://localhost:5173** (or the port shown in the terminal)

---

## Usage

1. **Upload Audio** - Drag and drop or click to select an audio file (MP3, WAV, M4A, FLAC, OGG, WEBM, MP4)
2. **Wait for Transcription** - Watch the progress bar as Whisper processes your audio
3. **View Transcript** - See the full transcript with timestamps
4. **Generate Summary** - Click to generate an AI-powered summary with Ollama
5. **Export** - Download your transcript in various formats (TXT, SRT, VTT, JSON)

---

## Troubleshooting

### Issue: "Failed to fetch" or connection errors on upload
**Solution:** Make sure the backend is running on port 8000. Check the terminal for errors.

### Issue: Transcription shows "failed" status
**Solution:** This was fixed by using polling instead of WebSocket for progress updates. Make sure you have the latest code.

### Issue: Summary returns 500 error
**Solution:**
1. Make sure Ollama is installed and running (`ollama serve`)
2. Make sure you have the model downloaded (`ollama pull llama3.1:8b`)
3. Verify Ollama is working: `curl http://localhost:11434/api/tags`

### Issue: "ModuleNotFoundError: No module named 'pyaudioop'"
**Solution:** This happens on Python 3.13. The code has been updated to not require pydub. Make sure you have the latest code.

### Issue: First transcription is slow
**Solution:** The first transcription downloads the Whisper model (~150MB for base model). Subsequent transcriptions will be faster.

### Issue: Port already in use
**Solution:**
- Backend port 8000 in use: `netstat -ano | findstr :8000` then kill the process
- Ollama port 11434 in use: Ollama is already running, which is fine
- Frontend will automatically use the next available port

---

## Configuration

### Whisper Model Selection
Edit `backend/core/config.py` to change the Whisper model:

```python
WHISPER_MODEL: str = "base"  # Options: tiny, base, small, medium, large
```

| Model | RAM | Speed (1hr audio) | Quality |
|-------|-----|-------------------|---------|
| tiny | 1GB | ~5 min | Fair |
| base | 1.5GB | ~10 min | Good (default) |
| small | 2.5GB | ~20 min | Better |
| medium | 5GB | ~40 min | Great |

### Ollama Model
Change the summarization model in `backend/core/config.py`:

```python
OLLAMA_MODEL: str = "llama3.1:8b"  # Or any other Ollama model
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/upload` | POST | Upload audio file |
| `/api/status/{task_id}` | GET | Get transcription progress |
| `/api/result/{task_id}` | GET | Get full transcript |
| `/api/summarize` | POST | Generate summary |
| `/api/export/{format}/{task_id}` | GET | Export transcript (txt/srt/vtt/json) |
| `/api/ollama/health` | GET | Check Ollama status |

API Documentation available at: http://localhost:8000/docs

---

## Project Structure

```
Audtext/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt     # Python dependencies
│   ├── api/routes/          # API endpoints
│   │   ├── transcription.py # Upload, status, results
│   │   ├── summarization.py # AI summary generation
│   │   └── export.py        # Export to TXT/SRT/VTT
│   ├── services/            # Business logic
│   │   ├── whisper_service.py   # Whisper transcription
│   │   ├── ollama_service.py    # Ollama summarization
│   │   └── audio_processor.py   # File handling
│   ├── core/                # Configuration
│   │   └── config.py        # App settings
│   └── models/              # Data models
│       └── schemas.py       # Pydantic schemas
├── frontend/
│   ├── package.json         # Node dependencies
│   ├── src/
│   │   ├── App.tsx          # Main app component
│   │   ├── components/      # React components
│   │   │   ├── FileDropzone.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   ├── TranscriptViewer.tsx
│   │   │   ├── SummaryPanel.tsx
│   │   │   └── ExportButtons.tsx
│   │   ├── services/        # API client
│   │   │   └── api.ts
│   │   └── hooks/           # Custom hooks
│   └── ...
└── uploads/                 # Temporary audio storage
```

---

## Known Issues & Fixes Applied

1. **Async callback in thread pool** - Fixed by using sync callbacks for progress updates
2. **WebSocket reliability** - Replaced with HTTP polling for more reliable progress tracking
3. **Python 3.13 compatibility** - Removed pydub dependency that required deprecated audioop module
4. **File size limits** - Removed to allow unlimited file sizes

---

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Akhil Reddy** - [GitHub](https://github.com/DandaAkhilReddy)

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Optimized CPU inference
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend framework
