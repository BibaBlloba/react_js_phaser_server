import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

players = {}


@app.websocket('/ws')
async def websocket(
    websocket: WebSocket,
):
    await websocket.accept()
    player = await websocket.receive_json()
    print(player)

    while True:
        message = await websocket.receive_json()
        print(message)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', reload=True)
