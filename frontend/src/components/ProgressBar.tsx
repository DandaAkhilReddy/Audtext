import React from 'react';
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';

interface ProgressBarProps {
  progress: number;
  status: string;
  message: string;
  filename?: string;
}

export function ProgressBar({ progress, status, message, filename }: ProgressBarProps) {
  const isComplete = status === 'completed';
  const isFailed = status === 'failed';
  const isProcessing = status === 'processing';

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="glass rounded-2xl p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {isComplete ? (
              <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
            ) : isFailed ? (
              <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center">
                <XCircle className="w-5 h-5 text-red-400" />
              </div>
            ) : isProcessing ? (
              <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center">
                <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />
              </div>
            ) : (
              <div className="w-10 h-10 rounded-full bg-slate-700/50 flex items-center justify-center">
                <Clock className="w-5 h-5 text-slate-400" />
              </div>
            )}
            <div>
              <p className="font-medium text-slate-200">
                {isComplete ? 'Transcription Complete' : isFailed ? 'Transcription Failed' : 'Transcribing Audio'}
              </p>
              {filename && (
                <p className="text-sm text-slate-400 truncate max-w-xs">{filename}</p>
              )}
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-primary-400">{Math.round(progress)}%</p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="relative h-3 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`absolute inset-y-0 left-0 rounded-full transition-all duration-500 ease-out ${
              isComplete
                ? 'bg-gradient-to-r from-green-500 to-green-400'
                : isFailed
                ? 'bg-gradient-to-r from-red-500 to-red-400'
                : 'bg-gradient-to-r from-primary-600 to-primary-400'
            }`}
            style={{ width: `${progress}%` }}
          />
          {isProcessing && (
            <div
              className="absolute inset-y-0 left-0 animate-shimmer rounded-full"
              style={{ width: `${progress}%` }}
            />
          )}
        </div>

        {/* Message */}
        <p className={`mt-3 text-sm ${isFailed ? 'text-red-300' : 'text-slate-400'}`}>
          {message}
        </p>
      </div>
    </div>
  );
}
