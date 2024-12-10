import asyncio
import websockets
import json


# this is an example of how to send data to the socket
async def send_message(json_data):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:

        # ! json_data has already been converted to json!!!!!!
        # Convert the input dictionary to a JSON string
        # json_message = json.dumps(json_data)

        # Send the JSON message
        await websocket.send(json_data)
        print(f"Sent message: {json_data}")


# Test message
if __name__ == "__main__":
    data = {
        "type": "greeting",
        "content": "Hello, server!",
        "timestamp": "2024-11-27T12:00:00Z"
    }
    asyncio.run(send_message(data))
