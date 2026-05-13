# Connection Manager for WebSocket broadcasting
from typing import Dict, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts updates."""
    
    def __init__(self):
        # Dictionary of poll_id -> set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, poll_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        if poll_id not in self.active_connections:
            self.active_connections[poll_id] = set()
        
        self.active_connections[poll_id].add(websocket)
        logger.info(f"Client connected to poll {poll_id}. Total connections: {len(self.active_connections[poll_id])}")
    
    def disconnect(self, websocket: WebSocket, poll_id: int):
        """Remove a WebSocket connection."""
        if poll_id in self.active_connections:
            self.active_connections[poll_id].discard(websocket)
            logger.info(f"Client disconnected from poll {poll_id}. Total connections: {len(self.active_connections[poll_id])}")
            
            # Clean up empty sets
            if not self.active_connections[poll_id]:
                del self.active_connections[poll_id]
    
    async def broadcast(self, poll_id: int, message: dict):
        """Broadcast a message to all connected clients for a poll."""
        if poll_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[poll_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection, poll_id)
    
    async def broadcast_poll_update(self, poll: dict):
        """Broadcast a poll update from REST API."""
        await self.broadcast(poll["id"], {
            "type": "poll_update",
            "data": poll
        })
