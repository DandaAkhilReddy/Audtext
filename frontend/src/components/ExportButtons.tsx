import React from 'react';
import { Download, FileText, Subtitles, FileJson } from 'lucide-react';
import { getExportUrl } from '../services/api';

interface ExportButtonsProps {
  taskId: string;
}

const EXPORT_OPTIONS = [
  { format: 'txt' as const, label: 'Plain Text', icon: FileText, description: '.txt' },
  { format: 'srt' as const, label: 'SRT Subtitles', icon: Subtitles, description: '.srt' },
  { format: 'vtt' as const, label: 'WebVTT', icon: Subtitles, description: '.vtt' },
  { format: 'json' as const, label: 'JSON Data', icon: FileJson, description: '.json' },
];

export function ExportButtons({ taskId }: ExportButtonsProps) {
  const handleExport = (format: 'txt' | 'srt' | 'vtt' | 'json') => {
    const url = getExportUrl(taskId, format);
    window.open(url, '_blank');
  };

  return (
    <div className="w-full">
      <div className="flex items-center gap-2 mb-4">
        <Download className="w-5 h-5 text-slate-400" />
        <h2 className="text-xl font-semibold text-slate-100">Export</h2>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {EXPORT_OPTIONS.map((option) => {
          const Icon = option.icon;
          return (
            <button
              key={option.format}
              onClick={() => handleExport(option.format)}
              className="glass glass-hover rounded-xl p-4 text-left transition-all group"
            >
              <Icon className="w-6 h-6 text-primary-400 mb-2 group-hover:scale-110 transition-transform" />
              <p className="font-medium text-slate-200 text-sm">{option.label}</p>
              <p className="text-xs text-slate-500">{option.description}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
