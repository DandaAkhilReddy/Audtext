from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        # task_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        """Accept WebSocket connection and register it for a task."""
        await websocket.accept()
        if task_id not in self.active_connections:
            self.active_connections[task_id] = set()
        self.active_connections[task_id].add(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str):
        """Remove WebSocket connection."""
        if task_id in self.active_connections:
            self.active_connections[task_id].discard(websocket)
            if not self.active_connections[task_id]:
                del self.active_connections[task_id]

    async def send_progress(
        self,
        task_id: str,
        progress: float,
        message: str,
        status: str = "processing",
        current_segment: int = None
    ):
        """Send progress update to all connections for a task."""
        if task_id in self.active_connections:
            data = {
                "task_id": task_id,
                "status": status,
                "progress": progress,
                "message": message,
                "current_segment": current_segment
            }

            dead_connections = set()
            for websocket in self.active_connections[task_id]:
                try:
                    await websocket.send_json(data)
                except:
                    dead_connections.add(websocket)

            # Clean up dead connections
            for ws in dead_connections:
                self.active_connections[task_id].discard(ws)

# Global connection manager
manager = ConnectionManager()
