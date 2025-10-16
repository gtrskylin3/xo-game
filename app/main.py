from typing import List
from fastapi import FastAPI
from fastapi.websockets import WebSocket, WebSocketDisconnect
from uvicorn import run
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

templates = Jinja2Templates(directory='app/templates')

class ConnectionManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.connections:
            await connection.send_text(message)

@app.get('/')
def html_response(request: Request):
    return templates.TemplateResponse(name='index.html', request=request)



@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect as e:
        print(f'connection closed {e.code}')


if __name__ == "__main__":
    run('app.main:app', reload=True)