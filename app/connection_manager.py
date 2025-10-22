
from typing import Dict, List, Optional
from uuid import uuid4
import asyncio

from fastapi import WebSocket

"""
lobbies = {
    lobby1_id: {
        websocket1: {nick, role},
        websocket2: {nick, role},
    },
    lobby2_id: {
        websocket3: {nick, role},
        websocket4: {nick, role},
    },
}
"""


class ConnectionManager:
    def __init__(self):
        self.lobbies: Dict[str, Dict[WebSocket, dict]] = {}
        self.lock = asyncio.Lock()

    def _get_lobby_id_by_websocket(self, websocket: WebSocket) -> Optional[str]:
        for lobby_id, lobby in self.lobbies.items():
            if websocket in lobby:
                return lobby_id
        return None

    def is_nickname_not_available(self, nickname_to_check: str) -> bool:
        return any(
            nickname_to_check == player_data["nickname"]
            for lobby in self.lobbies.values()
            for player_data in lobby.values()
        )

    async def connect(self, websocket: WebSocket, nickname):
        await websocket.accept()

        if self.is_nickname_not_available(nickname):
            await websocket.send_json({"error": "nickname already use"})
            await websocket.close()
            return

        async with self.lock:
            for lobby_id, lobby in self.lobbies.items():
                if len(lobby) == 1:
                    role = "O"
                    lobby[websocket] = {"nickname": nickname, "role": role}
                    await websocket.send_json({"type": "role", "role": role})
                    return lobby_id
            lobby_id = str(uuid4())
            role = "X"
            self.lobbies[lobby_id] = {websocket: {"nickname": nickname, "role": role}}
            await websocket.send_json({"type": "role", "role": role})
            return lobby_id

    def disconnect(self, websocket: WebSocket):
        lobby_id = self._get_lobby_id_by_websocket(websocket)
        if not lobby_id:
            return
        
        lobby = self.lobbies[lobby_id]
        del lobby[websocket]        
        
        if not lobby:
            del self.lobbies[lobby_id]
                
    def get_players(self, lobby_id: str) -> Dict:
        if lobby_id not in self.lobbies:
            return {}
        return {
            player_data['role']: player_data['nickname']
            for player_data in self.lobbies[lobby_id].values()
        }

    def get_player_by_websocket(self, websocket: WebSocket) -> Dict | None:
        lobby_id = self._get_lobby_id_by_websocket(websocket)
        if lobby_id and self.lobbies.get(lobby_id):
            return self.lobbies[lobby_id][websocket]
        return None

    async def broadcast(self, lobby_id: str, data: dict):
        if lobby_id in self.lobbies:
            for connection in self.lobbies[lobby_id]:
                await connection.send_json(data)
