from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
from uvicorn import run
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from uvicorn.server import HANDLED_SIGNALS
from app.connection_manager import ConnectionManager
from app.game_manager import Game, GameManager
from pprint import pprint


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
connection_manager = ConnectionManager()
game_manager = GameManager()

async def handle_move(lobby_id: str, player: dict, data: dict):
    game_id = game_manager.get_game_by_nickname(player['nickname'])
    if not game_id:
        return
    success = game_manager.make_move(data['row'], data['col'], player)
    if success:
        await connection_manager.broadcast(
            lobby_id=lobby_id,
            data=game_manager.game_state(game_id, 'game_update')
        )

async def handle_reset(lobby_id: str, player: dict, data: dict):
    game_id = game_manager.get_game_by_nickname(player['nickname'])
    if not game_id:
        return
    game_manager.reset_game(game_id)
    await connection_manager.broadcast(
        lobby_id, game_manager.game_state(game_id, "game_update")
    )

message_handlers = {
    'move': handle_move,
    'reset': handle_reset,
}

@app.get("/")
def html_response(request: Request):
    return templates.TemplateResponse(name="index.html", request=request)


@app.websocket("/ws/{nickname}")
async def websocket_endpoint(websocket: WebSocket, nickname: str):
    lobby_id = await connection_manager.connect(websocket, nickname)
    if not lobby_id:
        return
        
    player = connection_manager.get_player_by_websocket(websocket)
    if not player:
        return
    
    players_in_lobby = connection_manager.get_players(lobby_id)
    if len(players_in_lobby) == 2:
        game_id = game_manager.create_game(players_in_lobby)
        await connection_manager.broadcast(
            lobby_id=lobby_id,
            data=game_manager.game_state(game_id, "game_update"),
        )
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get('type')
            handler = message_handlers.get(message_type)
            if handler:
                await handler(lobby_id, player, data)

    except WebSocketDisconnect:
        game_id = game_manager.get_game_by_nickname(nickname)
        
        connection_manager.disconnect(websocket)
        
        if game_id and game_id in game_manager.games:
            await connection_manager.broadcast(lobby_id, {"type": "player_left"})
            del game_manager.games[game_id]
        


if __name__ == "__main__":
    run("app.main:app", reload=True)
