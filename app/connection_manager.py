from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.lobbies: List[Dict[WebSocket, dict]] = []

    async def connect(self, websocket: WebSocket, nickname):
        await websocket.accept()

        for lobby in self.lobbies:
            if len(lobby) == 1:
                role = "O"
                lobby.update({websocket: {"nickname": nickname, "role": role}})
                await websocket.send_json({"type": "role", "role": role})
                return
        else:
            self.lobbies.append({websocket: {"nickname": nickname, "role": "X"}})
            await websocket.send_json({"type": "role", "role": "X"})

    def _find_lobby_by_websocket(self, websocket: WebSocket) -> Dict:
        for lobby in self.lobbies:
            if websocket in lobby:
                return lobby
        return {}

    def disconnect(self, websocket: WebSocket):
        lobby = self._find_lobby_by_websocket(websocket)
        if lobby:
            del lobby[websocket]
            if lobby is None:
                del lobby
            return True
        return False

    async def broadcast(self, websocket: WebSocket, data: dict):
        lobby = self._find_lobby_by_websocket(websocket)
        if lobby:
            for player in lobby:
                await player.send_json(data)
