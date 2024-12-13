import asyncio
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
                open_timeout=10,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=10
            )
            print(f"Connected to {uri}")
        except Exception as e:
            print(f"Connection error: {e}. Retrying...")
            await asyncio.sleep(2)  # Retry after delay
            await self.connect(uri)  # Retry connection

    async def send_socket_message(self, json_data):
        if self.websocket_client is not None:
            try:
                # Check if the websocket is open using the `state` property
                if self.websocket_client.state != websockets.protocol.State.OPEN:
                    print("WebSocket is closed or closing, reconnecting...")
                    await self.connect()  # Reconnect if closed or closing

                await self.websocket_client.send(json_data)
                print(f"Sent message: {json_data}")
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("WebSocket is not connected.")

    async def close(self):
        if self.websocket_client and not self.websocket_client.closed:
            await self.websocket_client.close()
            print("WebSocket closed.")
        else:
            print("WebSocket is already closed.")


# Example usage
async def main():
    ws_client = WebSocketClient()
    await ws_client.initialize()  # This will automatically connect to ws://localhost:8765

    # Keep sending messages
    await ws_client.send_socket_message("Hello, WebSocket!")
    await ws_client.send_socket_message("Another message!")

    # If you're done, you can close it manually
    await ws_client.close()


if __name__ == "__main__":
    asyncio.run(main())
