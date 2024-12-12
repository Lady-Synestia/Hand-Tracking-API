import asyncio
import websockets

# List to keep track of all connected clients
connected_clients = set()


# this will recieve like all the data and then for each connection we will handle it
async def echo(websocket):
    # Register the client connection
    connected_clients.add(websocket)
    try:
        print(f"New client connected: {websocket.remote_address}")
        async for message in websocket:
            # categorise the message into what its for. Direction, gesture, etc. Could preface it with the type or just work it out

            # Broadcast the message to all connected clients
            for client in connected_clients:
                if client != websocket:  # Avoid sending the message back to the sender
                    await client.send(message)
    finally:
        # Unregister the client when disconnected
        connected_clients.remove(websocket)


async def main():
    print("e")
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run server indefinitely


if __name__ == "__main__":
    asyncio.run(main())
