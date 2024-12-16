import asyncio
import threading
import collections
import time
from queue import Queue

import websockets
import websockets.protocol


class WebSocketClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'websocket_client'):
            self.websocket_client = None
        self.uri = "ws://localhost:8765"

        self.message_queue = collections.deque()
        self.max_messages_per_window = 70
        self.window_size = 1
        self.message_interval = 1 / self.max_messages_per_window

    async def initialize(self):
        if self.websocket_client is None or self.websocket_client.closed:
            print("initializing websocketclient...")
            await self.connect(self.uri)

    async def reset_connection(self):
        if self.websocket_client:
            print("closing existing connection")
            await self.websocket_client.close()
            self.websocket_client = None
            print("connection closed")

    async def connect(self, uri):
        print("starting connection process")
        await self.reset_connection()
        try:
            self.websocket_client = await websockets.connect(
                uri,
                open_timeout=None,
                ping_interval=None,
                ping_timeout=None,
                close_timeout=None
            )
            print(f"connected to {uri}")
        except Exception as e:
            print(f"connection error: {e} retrying...")
            await asyncio.sleep(2)
            await self.connect(uri)

    async def send_socket_message(self, json_data):
        if self.websocket_client is not None:
            try:
                if self.websocket_client.state != websockets.protocol.State.OPEN:
                    print("websocket closed reconnecting...")
                    await self.connect(self.uri)

                await self.websocket_client.send(json_data)
                # await self.websocket_client.ping()
                # print(f"sent message: {json_data}")
            except Exception as e:
                print(f"error sending message: {e}")
        else:
            print("websocket is not connected")


class WebSocketThread:
    def __init__(self):
        self.client = WebSocketClient()
        self.message_queue = Queue()
        self.loop = None
        self.thread = threading.Thread(target=self._start_async_loop, daemon=True)

    def start(self):
        # start the websocket thread
        self.thread.start()

    def _start_async_loop(self):
        # initialize and run the asyncio event loop
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.client.initialize())
        self.loop.create_task(self._process_messages())
        self.loop.run_forever()

    async def _process_messages(self):
        # continuously check the queue and send messages
        while True:
            if not self.message_queue.empty():
                message = self.message_queue.get()
                await self.client.send_socket_message(message)
            await asyncio.sleep(0.01)  # small delay to prevent busy waiting

    def send_message(self, message):
        # put a message into the queue to be sent by the websocket client
        self.message_queue.put(message)

    def stop(self):
        # stop the thread and clean up the event loop
        if self.loop and self.loop.is_running():
            async def shutdown():
                # cancel all pending tasks
                tasks = [task for task in asyncio.all_tasks(self.loop) if task is not asyncio.current_task()]
                for task in tasks:
                    task.cancel()
                # give tasks time to cancel cleanly
                await asyncio.gather(*tasks, return_exceptions=True)
                self.loop.stop()

            # schedule the shutdown coroutine
            asyncio.run_coroutine_threadsafe(shutdown(), self.loop)
        self.thread.join()
        print("websocket thread stopped cleanly")


# example to like confirm it works
if __name__ == "__main__":
    ws_thread = WebSocketThread()
    ws_thread.start()

    # simulate another thread sending messages
    def send_messages():
        for i in range(10):
            print(f"sending message {i}")
            ws_thread.send_message(f"hello websocket {i}")
            time.sleep(0)  # simulate delay between messages


    sender_thread = threading.Thread(target=send_messages)
    sender_thread.start()
    sender_thread.join()

    # stop the websocket thread when done
    ws_thread.stop()
