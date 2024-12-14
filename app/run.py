import asyncio
import threading

from utils.HandTracking import main as start_hand_tracking
from utils.Sockets import start_socket_server
from utils.Sockets import WebSocketClient


async def run_components():
    # thread1 = threading.Thread(target=start_socket_server)
    # thread1.start()
    # Start the socket server in a separate thread without awaiting it directly

    # Initialize the WebSocketClient
    websocket_client = WebSocketClient()
    await websocket_client.initialize()  # Ensure the WebSocket client is connected

    # Start hand tracking in a separate task and pass the WebSocket client to it
    hand_tracking_task = asyncio.create_task(start_hand_tracking(websocket_client))

    # Let the tasks run in the background
    # await asyncio.gather(hand_tracking_task)

    # Optionally, wait for the server to finish (if necessary)
    # This is generally not needed unless you specifically want to wait for the server task


if __name__ == "__main__":
    # Run the components
    asyncio.run(run_components())
