from typing import List
from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
from uvicorn import run
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.connection_manager import ConnectionManager
from app.game_manager import Game

connection_manager = ConnectionManager()

app = FastAPI()
game = Game()


templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def html_response(request: Request):
    return templates.TemplateResponse(name="index.html", request=request)


@app.websocket("/ws/{nickname}")
async def websocket_endpoint(websocket: WebSocket, nickname: str):
    is_connected = await connection_manager.connect(websocket, nickname)
    if not is_connected:
        return
    if len(connection_manager.active_connections) == 2:
        game.__init__()
        players = connection_manager.get_players()
        await connection_manager.broadcast(game.game_state("game_update", players))
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "move":
                player = connection_manager.active_connections[websocket]
                success = game.make_move(data["row"], data["col"], player["role"])
                if success:
                    await connection_manager.broadcast(game.game_state("game_update", connection_manager.get_players()))
            elif data.get("type") == "reset":
                game.reset_game()
                await connection_manager.broadcast(game.game_state("game_update", connection_manager.get_players()))
    except WebSocketDisconnect as e:
        connection_manager.disconnect(websocket)
        await connection_manager.broadcast({"type": "player_left"})


if __name__ == "__main__":
    run("app.main:app", reload=True)
