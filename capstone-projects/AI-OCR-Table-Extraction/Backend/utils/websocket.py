from fastapi import WebSocket
from typing import Dict, List, Optional
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, document_id: int):
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []
        self.active_connections[document_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, document_id: int):
        self.active_connections[document_id].remove(websocket)
        if not self.active_connections[document_id]:
            del self.active_connections[document_id]
    
    async def broadcast_status(self, document_id: int, status: str, progress: Optional[float] = None):
        if document_id in self.active_connections:
            message = json.dumps({
                "status": status,
                "progress": progress,
                "document_id": document_id
            })
            for connection in self.active_connections[document_id]:
                try:
                    await connection.send_text(message)
                except:
                    continue

# Create a global instance
ws_manager = WebSocketManager()