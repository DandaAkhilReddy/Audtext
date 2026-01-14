import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'

// Mock the API module
vi.mock('../services/api', () => ({
  uploadAudio: vi.fn(),
  getStatus: vi.fn(),
  getResult: vi.fn(),
  generateSummary: vi.fn(),
  checkOllamaHealth: vi.fn(),
  getExportUrl: vi.fn((taskId, format) => `/api/export/${format}/${taskId}`)
}))

import * as api from '../services/api'

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should render the app title', () => {
      render(<App />)
      expect(screen.getByText('Audtext')).toBeInTheDocument()
    })

    it('should show the hero section', () => {
      render(<App />)
      expect(screen.getByText(/Transcribe Audio with/i)).toBeInTheDocument()
    })

    it('should show upload dropzone', () => {
      render(<App />)
      expect(screen.getByText(/Drag & drop/i)).toBeInTheDocument()
    })

    it('should show feature cards', () => {
      render(<App />)
      expect(screen.getByText('Local Processing')).toBeInTheDocument()
      expect(screen.getByText('Long Audio Support')).toBeInTheDocument()
      expect(screen.getByText('AI Summaries')).toBeInTheDocument()
    })

    it('should have GitHub link', () => {
      render(<App />)
      const githubLink = screen.getByRole('link', { name: /github/i })
      expect(githubLink).toHaveAttribute('href', 'https://github.com/DandaAkhilReddy/Audtext')
    })
  })

  describe('File Upload Flow', () => {
    it('should handle successful file upload', async () => {
      const mockUploadResponse = {
        task_id: 'test-task-123',
        filename: 'test.mp3',
        message: 'Upload successful'
      }

      const mockStatusProcessing = {
        task_id: 'test-task-123',
        status: 'processing',
        progress: 50,
        message: 'Transcribing...'
      }

      const mockStatusComplete = {
        task_id: 'test-task-123',
        status: 'completed',
        progress: 100,
        message: 'Complete'
      }

      const mockResult = {
        task_id: 'test-task-123',
        status: 'completed',
        progress: 100,
        message: 'Complete',
        language: 'en',
        duration: 30.5,
        segments: [
          { id: 0, start: 0, end: 5, text: 'Hello world' }
        ],
        full_text: 'Hello world'
      }

      vi.mocked(api.uploadAudio).mockResolvedValueOnce(mockUploadResponse)
      vi.mocked(api.getStatus)
        .mockResolvedValueOnce(mockStatusProcessing)
        .mockResolvedValueOnce(mockStatusComplete)
      vi.mocked(api.getResult).mockResolvedValueOnce(mockResult)

      render(<App />)

      // Create and drop a file
      const file = new File(['audio content'], 'test.mp3', { type: 'audio/mpeg' })
      const dropzone = screen.getByText(/Drag & drop/i).closest('div')!

      // Simulate file drop
      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
          types: ['Files']
        }
      })

      // Wait for upload to be called
      await waitFor(() => {
        expect(api.uploadAudio).toHaveBeenCalledWith(file)
      })
    })

    it('should show error on upload failure', async () => {
      vi.mocked(api.uploadAudio).mockRejectedValueOnce(new Error('Network error'))

      render(<App />)

      const file = new File(['audio'], 'test.mp3', { type: 'audio/mpeg' })
      const dropzone = screen.getByText(/Drag & drop/i).closest('div')!

      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
          types: ['Files']
        }
      })

      await waitFor(() => {
        expect(screen.getByText(/Network error/i)).toBeInTheDocument()
      })
    })
  })

  describe('Footer', () => {
    it('should show footer credits', () => {
      render(<App />)
      expect(screen.getByText(/Powered by Whisper & Ollama/i)).toBeInTheDocument()
      expect(screen.getByText(/Built by Akhil Reddy/i)).toBeInTheDocument()
    })
  })
})
