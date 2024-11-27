import asyncio
import websockets


# this is an example of basically how the unity side would function or whatever needs to access the data stream
async def listen():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            print(f"Received message: {message}")


asyncio.run(listen())
