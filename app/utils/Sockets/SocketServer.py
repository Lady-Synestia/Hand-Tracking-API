import asyncio
import websockets

connected_clients = set()


# async def echo(websocket):
#     # Register the client connection
#     connected_clients.add(websocket)
#     try:
#         print(f"New client connected: {websocket.remote_address}")
#
#         async for message in websocket:
#             print(message)
#             websocket.pong()
#             # await websocket.send(message)
#         #
#         # async for message in websocket:
#         #     print("gotmsg")
#         #     # Process and broadcast message
#         #     for client in connected_clients:
#         #         if client != websocket:
#         #             await client.send(message)
#         #             print("sentmsg")
#     except websockets.exceptions.ConnectionClosed as e:
#         print(f"Client {websocket.remote_address} disconnected with error: {e}")
#     finally:
#         print("Removing socket client")
#         connected_clients.remove(websocket)
#         # Optionally: Close the websocket explicitly here if not already closed
#         await websocket.close()


async def echo(client):
    connected_clients.add(client)
    async for message in client:
        print(message)
        client.pong()
        # await websocket.send(message)

async def main():
    print("Socket Server Starting")
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # Run server indefinitely

def start_socket_server():
    asyncio.run(main())


if __name__ == "__main__":
    start_socket_server()
