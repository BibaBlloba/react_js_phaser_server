import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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


async def broadcast(message: dict):
    for name, data in players.items():
        await data['socket'].send_json(message)


@app.websocket('/ws')
async def websocket(
    websocket: WebSocket,
):
    try:
        await websocket.accept()

        player_data = await websocket.receive_json()
        player_name = player_data['name']

        await broadcast(
            {
                'type': 'player_connected',
                'name': player_name,
                'x': player_data['x'],
                'y': player_data['y'],
            }
        )

        players[player_name] = {
            'x': player_data['x'],
            'y': player_data['y'],
            'socket': websocket,
        }
        print(
            f'player \033[31;1;4m"{player_name}"\033[0m connected: x: \033[31;1;4m"{player_data["x"]}"\033[0m, y: \033[31;1;4m"{player_data["y"]}"\033[0m'
        )
        print(f'Player list:\n{players}')

        await websocket.send_json(
            {
                'type': 'initial_data',
                'players': {
                    name: {'x': data['x'], 'y': data['y']}
                    for name, data in players.items()
                },
            }
        )

        while True:
            message = await websocket.receive_json()

            # if message['type'] == 'fire':
            #     for

            players[player_name]['x'] = message.get('x', players[player_name]['x'])
            players[player_name]['y'] = message.get('y', players[player_name]['y'])

            await broadcast(
                {
                    'type': 'player_update',
                    'name': player_name,
                    'x': players[player_name]['x'],
                    'y': players[player_name]['y'],
                }
            )

    except WebSocketDisconnect:
        del players[player_name]
        await broadcast(
            {
                'type': 'player_disconnected',
                'name': player_name,
            }
        )


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', reload=True)
