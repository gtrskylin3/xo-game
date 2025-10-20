from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
from uvicorn import run
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from app.connection_manager import ConnectionManager
from app.game_manager import Game
from pprint import pprint

connection_manager = ConnectionManager()

app = FastAPI()
game = Game()


templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def html_response(request: Request):
    return templates.TemplateResponse(name="index.html", request=request)


@app.websocket("/ws/{nickname}")
async def websocket_endpoint(websocket: WebSocket, nickname: str):
    lobby_id = await connection_manager.connect(websocket, nickname)
    players_in_lobby = connection_manager.get_players(lobby_id)
    if len(players_in_lobby) == 2:
        game_id = game.create_game(players_in_lobby)
        await connection_manager.broadcast(
            lobby_id=lobby_id,
            data=game.game_state(game_id, "game_update"),
        )
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "move":
                player = connection_manager.get_player_by_websocket(websocket)
                # print(player)
                game_id = game.get_game_by_nickname(player["nickname"])
                pprint(game.games)
                success = None
                if player:
                    success = game.make_move(data["row"], data["col"], player)
                if success:
                    await connection_manager.broadcast(
                        lobby_id=lobby_id,
                        data= game.game_state(
                            game_id=game_id,
                            type="game_update",
                        )
                    )
            elif data.get("type") == "reset":
                game.reset_game(game_id)
                await connection_manager.broadcast(
                    lobby_id,
                    game.game_state(game_id, "game_update")
                )
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        del game.games[game_id]
        game.reset_game(game_id)
        await connection_manager.broadcast(lobby_id, {"type": "player_left"})


if __name__ == "__main__":
    run("app.main:app", reload=True)
