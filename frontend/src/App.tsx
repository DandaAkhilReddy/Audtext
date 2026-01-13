import React, { useState, useEffect, useRef } from 'react';
import { FileAudio, Github, Mic2 } from 'lucide-react';
import { FileDropzone } from './components/FileDropzone';
import { ProgressBar } from './components/ProgressBar';
import { TranscriptViewer } from './components/TranscriptViewer';
import { SummaryPanel } from './components/SummaryPanel';
import { ExportButtons } from './components/ExportButtons';
import { uploadAudio, getStatus, getResult, TranscriptionResult, ProgressUpdate } from './services/api';

type AppState = 'idle' | 'uploading' | 'processing' | 'completed' | 'error';

function App() {
  const [state, setState] = useState<AppState>('idle');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [filename, setFilename] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<TranscriptionResult | null>(null);
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Handle file upload
  const handleFileAccepted = async (file: File) => {
    setState('uploading');
    setError(null);
    setFilename(file.name);
    setResult(null);
    setProgress(null);

    try {
      const response = await uploadAudio(file);
      setTaskId(response.task_id);
      setState('processing');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setState('error');
    }
  };

  // Poll for progress when processing
  useEffect(() => {
    if (state === 'processing' && taskId) {
      const pollStatus = async () => {
        try {
          const statusData = await getStatus(taskId);
          setProgress(statusData);

          if (statusData.status === 'completed') {
            // Fetch the full result
            const resultData = await getResult(taskId);
            setResult(resultData);
            setState('completed');
            return; // Stop polling
          } else if (statusData.status === 'failed') {
            setError(statusData.message || 'Transcription failed');
            setState('error');
            return; // Stop polling
          }

          // Continue polling
          pollingRef.current = setTimeout(pollStatus, 1500);
        } catch (err) {
          // Continue polling on error (server might be busy)
          pollingRef.current = setTimeout(pollStatus, 2000);
        }
      };

      // Start polling
      pollStatus();

      // Cleanup
      return () => {
        if (pollingRef.current) {
          clearTimeout(pollingRef.current);
        }
      };
    }
  }, [state, taskId]);

  // Reset to start new transcription
  const handleReset = () => {
    if (pollingRef.current) {
      clearTimeout(pollingRef.current);
    }
    setState('idle');
    setTaskId(null);
    setFilename('');
    setError(null);
    setResult(null);
    setProgress(null);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-slate-800">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center">
                <Mic2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Audtext</h1>
                <p className="text-xs text-slate-500">Audio Transcription & Summarization</p>
              </div>
            </div>
            <a
              href="https://github.com/DandaAkhilReddy/Audtext"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors text-slate-300"
            >
              <Github className="w-4 h-4" />
              <span className="text-sm hidden sm:inline">GitHub</span>
            </a>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero section when idle */}
        {state === 'idle' && (
          <div className="text-center mb-8">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Transcribe Audio with{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
                AI Power
              </span>
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Upload any audio file up to 1 hour long. Get accurate transcripts with timestamps
              and AI-powered summaries - all processed locally on your machine.
            </p>
          </div>
        )}

        {/* Upload section */}
        {(state === 'idle' || state === 'error') && (
          <FileDropzone
            onFileAccepted={handleFileAccepted}
            isUploading={state === 'uploading'}
            error={error}
          />
        )}

        {/* Uploading state */}
        {state === 'uploading' && (
          <ProgressBar
            progress={0}
            status="pending"
            message="Uploading file..."
            filename={filename}
          />
        )}

        {/* Processing state */}
        {state === 'processing' && (
          <ProgressBar
            progress={progress?.progress || 0}
            status={progress?.status || 'processing'}
            message={progress?.message || 'Starting transcription...'}
            filename={filename}
          />
        )}

        {/* Completed state - show results */}
        {state === 'completed' && result && taskId && (
          <div className="space-y-8">
            {/* Success banner */}
            <div className="glass rounded-2xl p-6 text-center">
              <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4">
                <FileAudio className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">
                Transcription Complete!
              </h3>
              <p className="text-slate-400 mb-4">{filename}</p>
              <button
                onClick={handleReset}
                className="px-6 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 transition-colors"
              >
                Transcribe Another File
              </button>
            </div>

            {/* Transcript viewer */}
            <TranscriptViewer
              segments={result.segments}
              fullText={result.full_text || ''}
              language={result.language}
              duration={result.duration}
            />

            {/* Export buttons */}
            <ExportButtons taskId={taskId} />

            {/* Summary panel */}
            <SummaryPanel taskId={taskId} />
          </div>
        )}

        {/* Features section when idle */}
        {state === 'idle' && (
          <div className="mt-16 grid sm:grid-cols-3 gap-6">
            <div className="glass rounded-xl p-6 text-center">
              <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center mx-auto mb-4">
                <Mic2 className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Local Processing</h3>
              <p className="text-sm text-slate-400">
                All transcription happens on your machine. Your audio never leaves your computer.
              </p>
            </div>
            <div className="glass rounded-xl p-6 text-center">
              <div className="w-12 h-12 rounded-xl bg-yellow-500/20 flex items-center justify-center mx-auto mb-4">
                <FileAudio className="w-6 h-6 text-yellow-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">Long Audio Support</h3>
              <p className="text-sm text-slate-400">
                Handle audio files up to 1 hour long with real-time progress tracking.
              </p>
            </div>
            <div className="glass rounded-xl p-6 text-center">
              <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-semibold text-white mb-2">AI Summaries</h3>
              <p className="text-sm text-slate-400">
                Generate intelligent summaries using local LLM - no API costs required.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-16">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-500">
            <p>Powered by Whisper & Ollama</p>
            <p>Built by Akhil Reddy</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
