from collections import defaultdict
import random
from typing import Any, Dict, List, Tuple

from fastapi import WebSocket

# {
#     game1: [
#         (WebSocket, role),
#         (WebSocket, role)
#     ]
# }

# class ConnectionManager:
#     def __init__(self):
#         self.lobby = {}
#         self.lobby_id = 0
#         self.used_role = ''
    
#     def init_lobby(self, lobby_id: int):
#         self.lobby[lobby_id] = []

#     def create_lobby(self, websocket: WebSocket):
#         role = ['X', '0']
#         current_lobby = self.lobby.get(self.lobby_id)
#         if not current_lobby:
#             self.init_lobby(self.lobby_id)
#             self.lobby[self.lobby_id].append((websocket, 'X'))
#             return
#         if len(current_lobby) < 2:
#             self.lobby[self.lobby_id].append((websocket, '0'))
#         self.lobby_id += 1
        

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.create_lobby(websocket)

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[WebSocket, Any[str]] = {}
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()

        if len(self.active_connections) >= 2:
            await websocket.send_text("Game is full")
            await websocket.close()
            return
        
        used_roles = self.active_connections.values()
        role =  'O' if 'X' in used_roles else 'X'
        self.active_connections[websocket] = role
        await websocket.send_json({'type': 'role', 'role': role})
    
    async def disconnect(self, websocket: WebSocket):
        del self.active_connections[websocket]

    async def broadcast(self, message: str):      
        # Отправляем сообщение всем в словаре     
        for connection in self.active_connections:
            await connection.send_text(message) 

