from typing import List
from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
from uvicorn import run
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.connection_manager import ConnectionManager


connection_manager = ConnectionManager()

app = FastAPI()




templates = Jinja2Templates(directory='app/templates')


@app.get('/')
def html_response(request: Request):
    return templates.TemplateResponse(name='index.html', request=request)



@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(connection_manager.connections)
            await connection_manager.broadcast(data)
    except WebSocketDisconnect as e:
        print(f'connection closed {e.code}')


if __name__ == "__main__":
    run('app.main:app', reload=True)