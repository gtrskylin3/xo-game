from typing import Dict, List, Optional
from uuid import uuid4

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

    def _get_lobby_id_by_websocket(self, websocket: WebSocket) -> Optional[str]:
        for lobby_id, lobby in self.lobbies.items():
            if websocket in lobby:
                return lobby_id
        return None
    
    def check_unique_nickname(self, nickname):
        nicknames = []
        for lobby_data in self.lobbies.values():
            print(lobby_data.values())
            for i in lobby_data.values():
                nicknames.append(i['nickname'])
        if nickname not in nicknames:
            return True
        return False
        
    async def connect(self, websocket: WebSocket, nickname):
        await websocket.accept()
       
        if not self.check_unique_nickname(nickname):
            await websocket.send_json({'error': 'nickname already use'})
            await websocket.close()
            return
            
        for lobby_id, lobby in self.lobbies.items():
            if len(lobby) == 1:
                role = "O"
                lobby[websocket] = {"nickname": nickname, "role": role}
                await websocket.send_json({"type": "role", "role": role})
                return lobby_id
        else:
            lobby_id = str(uuid4())
            role = "X"
            self.lobbies[lobby_id] = {websocket: {"nickname": nickname, "role": role}}
            await websocket.send_json({"type": "role", "role": role})
            return lobby_id

    def disconnect(self, websocket: WebSocket):
        lobby_id = self._get_lobby_id_by_websocket(websocket)
        if lobby_id and lobby_id in self.lobbies:
            lobby = self.lobbies[lobby_id]
            if websocket in lobby:
                del lobby[websocket]
                if not lobby:
                    del self.lobbies[lobby_id]

    def get_players(self, lobby_id: str) -> Dict[str, str]:
        players = {}
        if lobby_id in self.lobbies:
            for player_data in self.lobbies[lobby_id].values():
                players[player_data["role"]] = player_data["nickname"]
        return players
    
    def get_player_by_websocket(self, websocket: WebSocket) -> Dict | None:
        lobby_id = self._get_lobby_id_by_websocket(websocket)
        if lobby_id and self.lobbies.get(lobby_id):
            return self.lobbies[lobby_id][websocket]
        return None
        
    async def broadcast(self, lobby_id: str, data: dict):
        if lobby_id in self.lobbies:
            for connection in self.lobbies[lobby_id]:
                await connection.send_json(data)
