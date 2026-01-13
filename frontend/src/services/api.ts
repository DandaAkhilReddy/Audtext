const API_BASE = '/api';

export interface TranscriptSegment {
  id: number;
  start: number;
  end: number;
  text: string;
}

export interface TranscriptionResult {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  language?: string;
  duration?: number;
  segments: TranscriptSegment[];
  full_text?: string;
}

export interface UploadResponse {
  task_id: string;
  filename: string;
  message: string;
}

export interface SummaryResponse {
  task_id: string;
  summary: string;
  style: string;
}

export interface ProgressUpdate {
  task_id: string;
  status: string;
  progress: number;
  message: string;
  current_segment?: number;
}

// Upload audio file
export async function uploadAudio(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return response.json();
}

// Get transcription status
export async function getStatus(taskId: string): Promise<ProgressUpdate> {
  const response = await fetch(`${API_BASE}/status/${taskId}`);

  if (!response.ok) {
    throw new Error('Failed to get status');
  }

  return response.json();
}

// Get transcription result
export async function getResult(taskId: string): Promise<TranscriptionResult> {
  const response = await fetch(`${API_BASE}/result/${taskId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get result');
  }

  return response.json();
}

// Generate summary
export async function generateSummary(
  taskId: string,
  style: 'concise' | 'detailed' | 'bullet_points' = 'concise'
): Promise<SummaryResponse> {
  const response = await fetch(`${API_BASE}/summarize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ task_id: taskId, style }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate summary');
  }

  return response.json();
}

// Check Ollama health
export async function checkOllamaHealth(): Promise<{
  status: string;
  model: string;
  message: string;
}> {
  const response = await fetch(`${API_BASE}/ollama/health`);
  return response.json();
}

// Export functions
export function getExportUrl(taskId: string, format: 'txt' | 'srt' | 'vtt' | 'json'): string {
  return `${API_BASE}/export/${format}/${taskId}`;
}
