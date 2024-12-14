import asyncio
import collections
import time

import websockets
import websockets.protocol  # Import the State class


class WebSocketClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'websocket_client'):
            self.websocket_client = None
        self.uri = "ws://localhost:8765"  # Default WebSocket URI

        # a deque to store timestamps of messages sent in the last `window_size` seconds
        self.message_queue = collections.deque()
        self.max_messages_per_window = 70  # Maximum messages per second
        self.window_size = 1  # Time window in seconds (1 second window for rate-limiting)
        self.message_interval = 1 / self.max_messages_per_window  # Interval between messages in seconds


    async def initialize(self):
        # Connect automatically on initialization
        if self.websocket_client is None or self.websocket_client.closed:
            print("Initializing WebSocketClient...")
            await self.connect(self.uri)

    async def get_client(self):
        await asyncio.sleep(0)
        return self.websocket_client

    async def reset_connection(self):
        if self.websocket_client:
            print("Closing existing connection.")
            await self.websocket_client.close()
            self.websocket_client = None
            print("Connection closed.")

    async def connect(self, uri):
        print("Starting connection process.")
        await self.reset_connection()  # Ensure any previous connection is closed
        try:
            self.websocket_client = await websockets.connect(
                uri,
                open_timeout=None,
                ping_interval=None,
                ping_timeout=None,
                close_timeout=None
            )
            print(f"Connected to {uri}")
        except Exception as e:
            print(f"Connection error: {e}. Retrying...")
            await asyncio.sleep(2)  # Retry after delay
            await self.connect(uri)  # Retry connection

    async def send_socket_message(self, json_data):
        if self.websocket_client is not None:
            try:
                # Add the new message to the queue
                current_time = time.time()

                # Clean up old messages in the queue that fall outside the time window
                while self.message_queue and self.message_queue[0][0] < current_time - self.window_size:
                    self.message_queue.popleft()

                # Add the new message to the queue
                self.message_queue.append((current_time, json_data))

                # If we have more than the maximum allowed messages in the window, discard the oldest
                while len(self.message_queue) > self.max_messages_per_window:
                    self.message_queue.popleft()  # Discard the oldest message

                # Send messages evenly spaced throughout the second
                while self.message_queue:
                    message_time, message = self.message_queue.popleft()

                    # Check if the websocket is open using the `state` property
                    if self.websocket_client.state != websockets.protocol.State.OPEN:
                        print("WebSocket is closed or closing, reconnecting...")
                        await self.connect(self.uri)  # Reconnect if closed or closing

                    # Send the message
                    await self.websocket_client.send(message)

                    pong_waiter = await self.websocket_client.ping()
                    # only if you want to wait for the corresponding pong
                    latency = await pong_waiter
                    print(latency)

                    # Wait until the next message interval (evenly spaced)
                    time_to_wait = self.message_interval - (time.time() - current_time) % self.message_interval
                    await asyncio.sleep(time_to_wait)

                print(f"Sent message: {json_data}")
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("WebSocket is not connected.")


# Example usage
async def main():
    ws_client = WebSocketClient()
    await ws_client.initialize()  # This will automatically connect to ws://localhost:8765

    # Keep sending messages
    while True:
        task = asyncio.create_task(ws_client.send_socket_message("Hello, WebSocket!"))
        await asyncio.gather(task)

    # await ws_client.send_socket_message("Another message!")

    # If you're done, you can close it manually
    await ws_client.close()


if __name__ == "__main__":
    asyncio.run(main())
