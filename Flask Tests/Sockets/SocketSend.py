import asyncio
import websockets


async def send_message():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        message = "Hello, server!"
        await websocket.send(message)
        print(f"Sent message: {message}")


asyncio.run(send_message())
