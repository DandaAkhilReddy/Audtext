import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileAudio, AlertCircle } from 'lucide-react';

interface FileDropzoneProps {
  onFileAccepted: (file: File) => void;
  isUploading: boolean;
  error: string | null;
}

const ACCEPTED_FORMATS = {
  'audio/mpeg': ['.mp3'],
  'audio/wav': ['.wav'],
  'audio/x-m4a': ['.m4a'],
  'audio/mp4': ['.m4a'],
  'audio/flac': ['.flac'],
  'audio/ogg': ['.ogg'],
  'audio/webm': ['.webm'],
  'video/webm': ['.webm'],
  'video/mp4': ['.mp4'],
};

export function FileDropzone({ onFileAccepted, isUploading, error }: FileDropzoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileAccepted(acceptedFiles[0]);
      }
    },
    [onFileAccepted]
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_FORMATS,
    maxFiles: 1,
    disabled: isUploading,
  });

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          relative overflow-hidden rounded-2xl border-2 border-dashed p-12 text-center
          transition-all duration-300 cursor-pointer
          ${isDragActive && !isDragReject ? 'border-primary-400 bg-primary-500/10 scale-[1.02]' : ''}
          ${isDragReject ? 'border-red-400 bg-red-500/10' : ''}
          ${!isDragActive && !isUploading ? 'border-slate-600 hover:border-primary-500 hover:bg-slate-800/50' : ''}
          ${isUploading ? 'border-slate-700 bg-slate-800/30 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-4">
          {isUploading ? (
            <>
              <div className="w-16 h-16 rounded-full bg-primary-500/20 flex items-center justify-center animate-pulse">
                <FileAudio className="w-8 h-8 text-primary-400" />
              </div>
              <div>
                <p className="text-lg font-medium text-slate-200">Uploading...</p>
                <p className="text-sm text-slate-400 mt-1">Please wait</p>
              </div>
            </>
          ) : isDragReject ? (
            <>
              <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center">
                <AlertCircle className="w-8 h-8 text-red-400" />
              </div>
              <div>
                <p className="text-lg font-medium text-red-300">Invalid file type</p>
                <p className="text-sm text-slate-400 mt-1">
                  Please use MP3, WAV, M4A, FLAC, OGG, or WEBM
                </p>
              </div>
            </>
          ) : isDragActive ? (
            <>
              <div className="w-16 h-16 rounded-full bg-primary-500/20 flex items-center justify-center">
                <Upload className="w-8 h-8 text-primary-400 animate-bounce" />
              </div>
              <p className="text-lg font-medium text-primary-300">Drop your audio file here</p>
            </>
          ) : (
            <>
              <div className="w-16 h-16 rounded-full bg-slate-700/50 flex items-center justify-center group-hover:bg-primary-500/20 transition-colors">
                <Upload className="w-8 h-8 text-slate-400" />
              </div>
              <div>
                <p className="text-lg font-medium text-slate-200">
                  Drag & drop your audio file here
                </p>
                <p className="text-sm text-slate-400 mt-1">or click to browse</p>
              </div>
              <div className="flex flex-wrap justify-center gap-2 mt-2">
                {['MP3', 'WAV', 'M4A', 'FLAC', 'OGG', 'WEBM'].map((format) => (
                  <span
                    key={format}
                    className="px-2 py-1 text-xs font-medium text-slate-400 bg-slate-800 rounded-md"
                  >
                    {format}
                  </span>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Decorative gradient */}
        <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary-500/5 to-transparent pointer-events-none" />
      </div>

      {error && (
        <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}
    </div>
  );
}
