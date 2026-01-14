import { useState } from 'react';
import { Copy, Check, Clock, FileText, List } from 'lucide-react';
import type { TranscriptSegment } from '../services/api';

interface TranscriptViewerProps {
  segments: TranscriptSegment[];
  fullText: string;
  language?: string;
  duration?: number;
}

function formatTime(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatDuration(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hrs > 0) {
    return `${hrs}h ${mins}m ${secs}s`;
  }
  if (mins > 0) {
    return `${mins}m ${secs}s`;
  }
  return `${secs}s`;
}

export function TranscriptViewer({ segments, fullText, language, duration }: TranscriptViewerProps) {
  const [viewMode, setViewMode] = useState<'full' | 'segments'>('full');
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="text-xl font-semibold text-slate-100">Transcript</h2>
          <div className="flex items-center gap-4 mt-1 text-sm text-slate-400">
            {language && (
              <span className="flex items-center gap-1">
                <span className="uppercase">{language}</span>
              </span>
            )}
            {duration && (
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {formatDuration(duration)}
              </span>
            )}
            <span>{segments.length} segments</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View mode toggle */}
          <div className="flex rounded-lg bg-slate-800 p-1">
            <button
              onClick={() => setViewMode('full')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                viewMode === 'full'
                  ? 'bg-primary-500 text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <FileText className="w-4 h-4" />
              Full Text
            </button>
            <button
              onClick={() => setViewMode('segments')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                viewMode === 'segments'
                  ? 'bg-primary-500 text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <List className="w-4 h-4" />
              Segments
            </button>
          </div>

          {/* Copy button */}
          <button
            onClick={handleCopy}
            className="px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 transition-colors flex items-center gap-2"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-green-400" />
                <span className="text-sm">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span className="text-sm">Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="glass rounded-xl overflow-hidden">
        {viewMode === 'full' ? (
          <div className="p-6 max-h-96 overflow-y-auto">
            <p className="text-slate-200 leading-relaxed whitespace-pre-wrap">{fullText}</p>
          </div>
        ) : (
          <div className="max-h-96 overflow-y-auto divide-y divide-slate-800">
            {segments.map((segment) => (
              <div
                key={segment.id}
                className="p-4 hover:bg-slate-800/50 transition-colors"
              >
                <div className="flex items-start gap-4">
                  <span className="text-xs font-mono text-primary-400 bg-primary-500/10 px-2 py-1 rounded whitespace-nowrap">
                    {formatTime(segment.start)}
                  </span>
                  <p className="text-slate-200 flex-1">{segment.text}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
