<div align="center">

# 🎙️ Audtext

### *Transform Audio into Text & Insights — 100% Local, 100% Private*

[![GitHub stars](https://img.shields.io/github/stars/DandaAkhilReddy/Audtext?style=for-the-badge&logo=github&color=yellow)](https://github.com/DandaAkhilReddy/Audtext/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/DandaAkhilReddy/Audtext?style=for-the-badge&logo=github&color=blue)](https://github.com/DandaAkhilReddy/Audtext/network/members)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)

<br/>

<img src="https://raw.githubusercontent.com/DandaAkhilReddy/Audtext/main/docs/demo.gif" alt="Audtext Demo" width="800"/>

<br/>

**[🚀 Quick Start](#-quick-start)** • **[✨ Features](#-features)** • **[📖 Documentation](#-installation)** • **[🤝 Contributing](#-contributing)**

</div>

---

## 🌟 Why Audtext?

<table>
<tr>
<td width="50%">

### 🔒 **Privacy First**
Your audio **never leaves your computer**. Everything runs locally using OpenAI's Whisper model - no cloud uploads, no API keys needed, no subscription costs.

</td>
<td width="50%">

### ⚡ **Lightning Fast**
CPU-optimized transcription with `faster-whisper`. Process 1-hour audio files in minutes, not hours. Real-time progress tracking included.

</td>
</tr>
<tr>
<td width="50%">

### 🤖 **AI-Powered Summaries**
Get intelligent summaries using Ollama's local LLM. Choose from concise, detailed, or bullet-point formats - all without API costs.

</td>
<td width="50%">

### 📤 **Multiple Export Formats**
Export your transcripts as **TXT**, **SRT**, **VTT**, or **JSON**. Perfect for subtitles, documentation, or further processing.

</td>
</tr>
</table>

---

## ✨ Features

<div align="center">

| Feature | Description |
|:-------:|:------------|
| 🎵 **Multi-Format Support** | MP3, WAV, M4A, FLAC, OGG, WEBM, MP4 |
| 📊 **Real-Time Progress** | Watch transcription progress live |
| 🕐 **Timestamps** | Every segment includes precise timing |
| 🌍 **Multi-Language** | Automatic language detection |
| 📱 **Responsive UI** | Beautiful interface on any device |
| 🔄 **No Size Limits** | Upload audio files of any length |

</div>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         AUDTEXT                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│   │              │     │              │     │              │   │
│   │   Frontend   │────▶│   Backend    │────▶│   Whisper    │   │
│   │   React 18   │     │   FastAPI    │     │   (Local)    │   │
│   │              │     │              │     │              │   │
│   └──────────────┘     └──────┬───────┘     └──────────────┘   │
│                               │                                  │
│                               ▼                                  │
│                        ┌──────────────┐                         │
│                        │              │                         │
│                        │   Ollama     │                         │
│                        │   (LLM)      │                         │
│                        │              │                         │
│                        └──────────────┘                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Installation |
|-------------|---------|--------------|
| Python | 3.11+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| FFmpeg | Latest | See below |
| Ollama | Latest | [ollama.ai](https://ollama.ai) |

<details>
<summary><b>📦 Install FFmpeg</b></summary>

```bash
# Windows (winget)
winget install ffmpeg

# Windows (chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg
```

</details>

### ⚡ 3-Step Setup

```bash
# 1️⃣ Clone & Setup Backend
git clone https://github.com/DandaAkhilReddy/Audtext.git
cd Audtext/backend
python -m venv venv && .\venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2️⃣ Setup Frontend
cd ../frontend
npm install

# 3️⃣ Download AI Model
ollama pull llama3.1:8b
```

### 🎬 Run the App

Open **3 terminals**:

```bash
# Terminal 1 - AI Engine
ollama serve

# Terminal 2 - Backend (activate venv first!)
cd Audtext/backend && .\venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Terminal 3 - Frontend
cd Audtext/frontend
npm run dev
```

🌐 **Open** → [http://localhost:5173](http://localhost:5173)

---

## 📖 Installation

<details>
<summary><b>🔧 Detailed Backend Setup</b></summary>

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Dependencies include:**
- `fastapi` - Modern web framework
- `faster-whisper` - Optimized speech recognition
- `httpx` - Async HTTP client for Ollama
- `pydantic` - Data validation

</details>

<details>
<summary><b>🎨 Detailed Frontend Setup</b></summary>

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

**Built with:**
- `React 18` - UI framework
- `Vite` - Lightning fast bundler
- `Tailwind CSS` - Utility-first styling
- `Lucide React` - Beautiful icons

</details>

---

## ⚙️ Configuration

### 🎤 Whisper Models

Edit `backend/core/config.py`:

```python
WHISPER_MODEL: str = "base"  # Options: tiny, base, small, medium, large
```

| Model | RAM | Speed (1hr audio) | Quality |
|:-----:|:---:|:-----------------:|:-------:|
| `tiny` | 1GB | ~5 min | ⭐⭐ |
| `base` | 1.5GB | ~10 min | ⭐⭐⭐ |
| `small` | 2.5GB | ~20 min | ⭐⭐⭐⭐ |
| `medium` | 5GB | ~40 min | ⭐⭐⭐⭐⭐ |

### 🤖 Ollama Models

```python
OLLAMA_MODEL: str = "llama3.1:8b"  # Or any Ollama model
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|----------|:------:|-------------|
| `/api/upload` | `POST` | Upload audio file |
| `/api/status/{task_id}` | `GET` | Get transcription progress |
| `/api/result/{task_id}` | `GET` | Get full transcript |
| `/api/summarize` | `POST` | Generate AI summary |
| `/api/export/{format}/{task_id}` | `GET` | Export (txt/srt/vtt/json) |
| `/api/ollama/health` | `GET` | Check Ollama status |

📚 **Interactive Docs** → [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📁 Project Structure

```
Audtext/
├── 🐍 backend/
│   ├── main.py              # FastAPI entry point
│   ├── requirements.txt     # Python dependencies
│   ├── api/routes/          # API endpoints
│   ├── services/            # Business logic
│   │   ├── whisper_service.py   # Transcription
│   │   └── ollama_service.py    # Summarization
│   ├── core/config.py       # Settings
│   └── tests/               # Test suite
│
├── ⚛️ frontend/
│   ├── src/
│   │   ├── App.tsx          # Main component
│   │   ├── components/      # UI components
│   │   └── services/api.ts  # API client
│   └── package.json
│
└── 📂 uploads/              # Temporary storage
```

---

## 🐛 Troubleshooting

<details>
<summary><b>❌ "Failed to fetch" on upload</b></summary>

Make sure the backend is running on port 8000:
```bash
uvicorn main:app --reload --port 8000
```

</details>

<details>
<summary><b>❌ Summary returns 500 error</b></summary>

1. Ensure Ollama is running: `ollama serve`
2. Download the model: `ollama pull llama3.1:8b`
3. Verify: `curl http://localhost:11434/api/tags`

</details>

<details>
<summary><b>❌ First transcription is slow</b></summary>

The first run downloads the Whisper model (~150MB for base). Subsequent runs are faster.

</details>

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 **Fork** the repository
2. 🌿 **Create** a feature branch (`git checkout -b feature/amazing`)
3. 💾 **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. 📤 **Push** to the branch (`git push origin feature/amazing`)
5. 🔃 **Open** a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

<div align="center">

| Technology | Purpose |
|:----------:|:--------|
| [🎤 OpenAI Whisper](https://github.com/openai/whisper) | Speech Recognition |
| [⚡ faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Optimized Inference |
| [🦙 Ollama](https://ollama.ai) | Local LLM Runtime |
| [🚀 FastAPI](https://fastapi.tiangolo.com) | Backend Framework |
| [⚛️ React](https://react.dev) | Frontend Framework |

</div>

---

<div align="center">

### ⭐ Star this repo if you find it useful!

Made with ❤️ by [Akhil Reddy](https://github.com/DandaAkhilReddy)

<br/>

[![Star History Chart](https://api.star-history.com/svg?repos=DandaAkhilReddy/Audtext&type=Date)](https://star-history.com/#DandaAkhilReddy/Audtext&Date)

</div>
