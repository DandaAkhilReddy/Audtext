import { useState } from 'react';
import { Sparkles, Copy, Check, Loader2, RefreshCw } from 'lucide-react';
import { generateSummary } from '../services/api';

interface SummaryPanelProps {
  taskId: string;
}

type SummaryStyle = 'concise' | 'detailed' | 'bullet_points';

const STYLE_OPTIONS: { value: SummaryStyle; label: string; description: string }[] = [
  { value: 'concise', label: 'Concise', description: '2-3 paragraph summary' },
  { value: 'detailed', label: 'Detailed', description: 'Comprehensive summary' },
  { value: 'bullet_points', label: 'Bullet Points', description: 'Key points list' },
];

export function SummaryPanel({ taskId }: SummaryPanelProps) {
  const [summary, setSummary] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedStyle, setSelectedStyle] = useState<SummaryStyle>('concise');
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await generateSummary(taskId, selectedStyle);
      setSummary(result.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate summary');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = async () => {
    if (summary) {
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-yellow-400" />
          AI Summary
        </h2>
      </div>

      <div className="glass rounded-xl p-6">
        {/* Style selector */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Summary Style
          </label>
          <div className="flex flex-wrap gap-2">
            {STYLE_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => setSelectedStyle(option.value)}
                disabled={isLoading}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedStyle === option.value
                    ? 'bg-primary-500 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {option.label}
              </button>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {STYLE_OPTIONS.find((o) => o.value === selectedStyle)?.description}
          </p>
        </div>

        {/* Generate button */}
        <button
          onClick={handleGenerate}
          disabled={isLoading}
          className={`w-full py-3 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
            isLoading
              ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 text-white'
          }`}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Generating Summary...
            </>
          ) : summary ? (
            <>
              <RefreshCw className="w-5 h-5" />
              Regenerate Summary
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Generate Summary
            </>
          )}
        </button>

        {/* Error message */}
        {error && (
          <div className="mt-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
            <p className="text-sm text-red-300">{error}</p>
            <p className="text-xs text-slate-500 mt-1">
              Make sure Ollama is running with the llama3.1:8b model
            </p>
          </div>
        )}

        {/* Summary content */}
        {summary && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-slate-400">Generated Summary</span>
              <button
                onClick={handleCopy}
                className="text-sm text-slate-400 hover:text-slate-200 flex items-center gap-1"
              >
                {copied ? (
                  <>
                    <Check className="w-4 h-4 text-green-400" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4" />
                    Copy
                  </>
                )}
              </button>
            </div>
            <div className="p-4 rounded-lg bg-slate-800/50 max-h-64 overflow-y-auto">
              <p className="text-slate-200 whitespace-pre-wrap leading-relaxed">{summary}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
