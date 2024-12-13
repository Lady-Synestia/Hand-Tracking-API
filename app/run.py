import asyncio
from utils.HandTracking import main as start_hand_tracking
from utils.Sockets import main as start_socket_server
from utils.Sockets import WebSocketClient


async def run_components():
    # start the socket server
    websocket_client_task = asyncio.create_task(start_socket_server())

    # Initialize the WebSocketClient
    websocket_client = WebSocketClient()
    await websocket_client.initialize()  # Ensure the WebSocket client is connected

    # Start hand tracking in a separate thread and pass the WebSocket client to it
    hand_tracking_task = asyncio.create_task(start_hand_tracking(websocket_client))

    # Let both tasks run in the background
    await asyncio.gather(websocket_client_task, hand_tracking_task)


if __name__ == "__main__":
    # Run the components
    asyncio.run(run_components())
