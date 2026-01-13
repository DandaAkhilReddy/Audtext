import { useEffect, useRef, useState, useCallback } from 'react';

export interface ProgressData {
  task_id: string;
  status: string;
  progress: number;
  message: string;
  current_segment?: number;
}

export function useWebSocket(taskId: string | null) {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!taskId) return;

    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/progress/${taskId}`;

    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setProgress(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('WebSocket disconnected');

        // Reconnect after 2 seconds if task is still active
        if (progress?.status === 'processing') {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 2000);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }, [taskId]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setProgress(null);
  }, []);

  useEffect(() => {
    if (taskId) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [taskId, connect, disconnect]);

  return { progress, isConnected, disconnect };
}
