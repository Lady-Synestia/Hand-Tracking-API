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
            # Process and broadcast message
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Client {websocket.remote_address} disconnected with error: {e}")
    finally:
        print("Removing socket client")
        connected_clients.remove(websocket)
        # Optionally: Close the websocket explicitly here if not already closed
        await websocket.close()


async def main():
    print("e")
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run server indefinitely


if __name__ == "__main__":
    asyncio.run(main())
