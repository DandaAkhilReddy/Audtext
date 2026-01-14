import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TranscriptViewer } from '../components/TranscriptViewer'
import { SummaryPanel } from '../components/SummaryPanel'

// Mock navigator.clipboard
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockResolvedValue(undefined)
  }
})

// Mock the API module
vi.mock('../services/api', () => ({
  generateSummary: vi.fn()
}))

import * as api from '../services/api'

describe('TranscriptViewer Component', () => {
  const mockSegments = [
    { id: 0, start: 0, end: 5, text: 'Hello world.' },
    { id: 1, start: 5, end: 10, text: 'This is a test.' },
    { id: 2, start: 10, end: 15, text: 'Third segment here.' }
  ]

  const mockFullText = 'Hello world. This is a test. Third segment here.'

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render transcript header', () => {
    render(
      <TranscriptViewer
        segments={mockSegments}
        fullText={mockFullText}
        language="en"
        duration={15}
      />
    )

    expect(screen.getByText('Transcript')).toBeInTheDocument()
    expect(screen.getByText('EN')).toBeInTheDocument()
    expect(screen.getByText('3 segments')).toBeInTheDocument()
  })

  it('should display full text by default', () => {
    render(
      <TranscriptViewer
        segments={mockSegments}
        fullText={mockFullText}
        language="en"
        duration={15}
      />
    )

    expect(screen.getByText(mockFullText)).toBeInTheDocument()
  })

  it('should toggle to segments view', async () => {
    render(
      <TranscriptViewer
        segments={mockSegments}
        fullText={mockFullText}
        language="en"
        duration={15}
      />
    )

    const segmentsButton = screen.getByText('Segments')
    fireEvent.click(segmentsButton)

    // Should show timestamps
    expect(screen.getByText('0:00')).toBeInTheDocument()
    expect(screen.getByText('0:05')).toBeInTheDocument()
    expect(screen.getByText('0:10')).toBeInTheDocument()
  })

  it('should copy text to clipboard', async () => {
    render(
      <TranscriptViewer
        segments={mockSegments}
        fullText={mockFullText}
        language="en"
        duration={15}
      />
    )

    const copyButton = screen.getByText('Copy')
    fireEvent.click(copyButton)

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockFullText)

    await waitFor(() => {
      expect(screen.getByText('Copied!')).toBeInTheDocument()
    })
  })

  it('should format duration correctly', () => {
    // Short duration
    const { rerender } = render(
      <TranscriptViewer
        segments={mockSegments}
        fullText={mockFullText}
        duration={45}
      />
    )
    expect(screen.getByText('45s')).toBeInTheDocument()

    // Medium duration
    rerender(
      <TranscriptViewer
        segments={mockSegments}
        fullText={mockFullText}
        duration={125}
      />
    )
    expect(screen.getByText('2m 5s')).toBeInTheDocument()

    // Long duration
    rerender(
      <TranscriptViewer
        segments={mockSegments}
        fullText={mockFullText}
        duration={3665}
      />
    )
    expect(screen.getByText('1h 1m 5s')).toBeInTheDocument()
  })
})

describe('SummaryPanel Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render summary panel with style options', () => {
    render(<SummaryPanel taskId="test-123" />)

    expect(screen.getByText('AI Summary')).toBeInTheDocument()
    expect(screen.getByText('Concise')).toBeInTheDocument()
    expect(screen.getByText('Detailed')).toBeInTheDocument()
    expect(screen.getByText('Bullet Points')).toBeInTheDocument()
  })

  it('should show generate button initially', () => {
    render(<SummaryPanel taskId="test-123" />)

    expect(screen.getByText('Generate Summary')).toBeInTheDocument()
  })

  it('should generate summary on button click', async () => {
    vi.mocked(api.generateSummary).mockResolvedValueOnce({
      task_id: 'test-123',
      summary: 'This is a test summary.',
      style: 'concise'
    })

    render(<SummaryPanel taskId="test-123" />)

    const generateButton = screen.getByText('Generate Summary')
    fireEvent.click(generateButton)

    await waitFor(() => {
      expect(screen.getByText('This is a test summary.')).toBeInTheDocument()
    })

    expect(api.generateSummary).toHaveBeenCalledWith('test-123', 'concise')
  })

  it('should show loading state while generating', async () => {
    vi.mocked(api.generateSummary).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    )

    render(<SummaryPanel taskId="test-123" />)

    const generateButton = screen.getByText('Generate Summary')
    fireEvent.click(generateButton)

    expect(screen.getByText('Generating Summary...')).toBeInTheDocument()
  })

  it('should show error message on failure', async () => {
    vi.mocked(api.generateSummary).mockRejectedValueOnce(
      new Error('Ollama not available')
    )

    render(<SummaryPanel taskId="test-123" />)

    const generateButton = screen.getByText('Generate Summary')
    fireEvent.click(generateButton)

    await waitFor(() => {
      expect(screen.getByText('Ollama not available')).toBeInTheDocument()
    })
  })

  it('should allow changing summary style', async () => {
    vi.mocked(api.generateSummary).mockResolvedValueOnce({
      task_id: 'test-123',
      summary: 'Detailed summary content.',
      style: 'detailed'
    })

    render(<SummaryPanel taskId="test-123" />)

    // Select detailed style
    const detailedButton = screen.getByText('Detailed')
    fireEvent.click(detailedButton)

    // Generate summary
    const generateButton = screen.getByText('Generate Summary')
    fireEvent.click(generateButton)

    await waitFor(() => {
      expect(api.generateSummary).toHaveBeenCalledWith('test-123', 'detailed')
    })
  })

  it('should show regenerate button after summary is generated', async () => {
    vi.mocked(api.generateSummary).mockResolvedValueOnce({
      task_id: 'test-123',
      summary: 'Test summary.',
      style: 'concise'
    })

    render(<SummaryPanel taskId="test-123" />)

    const generateButton = screen.getByText('Generate Summary')
    fireEvent.click(generateButton)

    await waitFor(() => {
      expect(screen.getByText('Regenerate Summary')).toBeInTheDocument()
    })
  })

  it('should copy summary to clipboard', async () => {
    vi.mocked(api.generateSummary).mockResolvedValueOnce({
      task_id: 'test-123',
      summary: 'Summary to copy.',
      style: 'concise'
    })

    render(<SummaryPanel taskId="test-123" />)

    const generateButton = screen.getByText('Generate Summary')
    fireEvent.click(generateButton)

    await waitFor(() => {
      expect(screen.getByText('Summary to copy.')).toBeInTheDocument()
    })

    const copyButton = screen.getByText('Copy')
    fireEvent.click(copyButton)

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('Summary to copy.')
  })
})
