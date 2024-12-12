import asyncio
import websockets


class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.websocket = None

    async def connect(self):
        if self.websocket is None or self.websocket.closed:
            self.websocket = await websockets.connect(self.uri)
            print("WebSocket connected.")

    async def send_message(self, json_data):
        await self.connect()  # make sure connection is open
        await self.websocket.send(json_data)
        print(f"Sent message: {json_data}")

    async def close(self):
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
            print("WebSocket closed.")


# make the like singleton
websocket_client = WebSocketClient("ws://localhost:8765")


async def initialize():
    # initialises the client
    await websocket_client.connect()


async def send_message(json_data):
    # sends messages
    await websocket_client.send_message(json_data)
    print("sent")


async def close_connection():
    # closes conn
    await websocket_client.close()
