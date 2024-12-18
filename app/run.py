import asyncio
import threading

from utils.HandTracking import main as start_hand_tracking
from utils.Sockets import start_socket_server
from utils.Sockets import websocket_manager


async def run_components():
    thread1 = threading.Thread(target=start_socket_server)
    thread1.start()
    # start the socket server in a separate thread without awaiting it directly

    # start the WebSocket thread
    websocket_manager.start()

    # start hand tracking and pass the WebSocket manager to send messages
    hand_tracking_task = asyncio.create_task(start_hand_tracking(websocket_manager))

    # let tasks run
    await asyncio.gather(hand_tracking_task)


if __name__ == "__main__":
    # run the components
    asyncio.run(run_components())
