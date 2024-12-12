import asyncio
from utils.HandTracking import main as start_hand_tracking
from utils.Sockets import main as start_socket_server
from utils.Sockets import initialize


async def run_components():
    # start the socket server
    websocket_server_task = asyncio.create_task(start_socket_server())

    # initialize the WebSocket sender singleton
    await initialize()
    print("WebSocket sender initialized")

    # start hand tracking in a separate thread
    hand_tracking_task = asyncio.to_thread(start_hand_tracking)

    # let both tasks run in background
    await asyncio.gather(websocket_server_task, hand_tracking_task)


if __name__ == "__main__":
    # run the components
    asyncio.run(run_components())
