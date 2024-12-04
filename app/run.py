import asyncio
from utils.HandTracking import main as start_hand_tracking
from utils.Sockets import main as start_socket_server


async def run_components():
    # define the socket server hand tracking
    websocket_server_task = asyncio.create_task(start_socket_server())
    hand_tracking_task = asyncio.to_thread(start_hand_tracking)

    # wait for them to complete
    await asyncio.gather(websocket_server_task, hand_tracking_task)


if __name__ == "__main__":
    # run the components
    asyncio.run(run_components())
