import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  uploadAudio,
  getStatus,
  getResult,
  generateSummary,
  checkOllamaHealth,
  getExportUrl
} from '../services/api'

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('uploadAudio', () => {
    it('should upload a file and return task ID', async () => {
      const mockResponse = {
        task_id: 'test-123',
        filename: 'test.mp3',
        message: 'Upload successful'
      }

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })

      const file = new File(['test'], 'test.mp3', { type: 'audio/mpeg' })
      const result = await uploadAudio(file)

      expect(result.task_id).toBe('test-123')
      expect(result.filename).toBe('test.mp3')
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/upload',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData)
        })
      )
    })

    it('should throw error on upload failure', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'File too large' })
      })

      const file = new File(['test'], 'test.mp3', { type: 'audio/mpeg' })

      await expect(uploadAudio(file)).rejects.toThrow('File too large')
    })
  })

  describe('getStatus', () => {
    it('should return progress update', async () => {
      const mockStatus = {
        task_id: 'test-123',
        status: 'processing',
        progress: 50,
        message: 'Transcribing...'
      }

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockStatus)
      })

      const result = await getStatus('test-123')

      expect(result.progress).toBe(50)
      expect(result.status).toBe('processing')
      expect(global.fetch).toHaveBeenCalledWith('/api/status/test-123')
    })

    it('should throw on status fetch failure', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false
      })

      await expect(getStatus('test-123')).rejects.toThrow('Failed to get status')
    })
  })

  describe('getResult', () => {
    it('should return transcription result', async () => {
      const mockResult = {
        task_id: 'test-123',
        status: 'completed',
        progress: 100,
        message: 'Complete',
        language: 'en',
        duration: 120.5,
        segments: [
          { id: 0, start: 0, end: 5, text: 'Hello world' }
        ],
        full_text: 'Hello world'
      }

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResult)
      })

      const result = await getResult('test-123')

      expect(result.status).toBe('completed')
      expect(result.segments).toHaveLength(1)
      expect(result.full_text).toBe('Hello world')
    })

    it('should throw on result fetch failure', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Task not found' })
      })

      await expect(getResult('nonexistent')).rejects.toThrow('Task not found')
    })
  })

  describe('generateSummary', () => {
    it('should generate summary with default style', async () => {
      const mockSummary = {
        task_id: 'test-123',
        summary: 'This is a summary of the transcript.',
        style: 'concise'
      }

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockSummary)
      })

      const result = await generateSummary('test-123')

      expect(result.summary).toBe('This is a summary of the transcript.')
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/summarize',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task_id: 'test-123', style: 'concise' })
        })
      )
    })

    it('should support different summary styles', async () => {
      const styles = ['concise', 'detailed', 'bullet_points'] as const

      for (const style of styles) {
        global.fetch = vi.fn().mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ task_id: 'test', summary: 'Summary', style })
        })

        const result = await generateSummary('test', style)
        expect(result.style).toBe(style)
      }
    })

    it('should throw on summary generation failure', async () => {
      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Ollama not available' })
      })

      await expect(generateSummary('test-123')).rejects.toThrow('Ollama not available')
    })
  })

  describe('checkOllamaHealth', () => {
    it('should return Ollama health status', async () => {
      const mockHealth = {
        status: 'healthy',
        model: 'llama3.1:8b',
        message: 'Ollama is running'
      }

      global.fetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockHealth)
      })

      const result = await checkOllamaHealth()

      expect(result.status).toBe('healthy')
      expect(result.model).toBe('llama3.1:8b')
    })
  })

  describe('getExportUrl', () => {
    it('should return correct export URL for each format', () => {
      const formats = ['txt', 'srt', 'vtt', 'json'] as const

      for (const format of formats) {
        const url = getExportUrl('test-123', format)
        expect(url).toBe(`/api/export/${format}/test-123`)
      }
    })
  })
})
