import asyncio
import json

import websockets
import traceback

connected_clients = dict()


# so for each client i need to know what it like actually wants. Each client needs to be attributed to a piece of data where it says what type of data the server should send it

# Add a new client with its initial data preferences
def add_client(client, data_types):
    if client not in connected_clients:
        connected_clients[client] = data_types


def set_client_prefs(client, data_types):
    if client in connected_clients:
        connected_clients[client] = data_types


# Remove a client when it disconnects
def remove_client(client):
    if client in connected_clients:
        connected_clients.pop(client, None)


async def echo(client):
    try:
        # receive the initial handshake message
        initial_message = await client.recv()

        # check if it's already a string
        if isinstance(initial_message, str):
            print(f"Received string message: {initial_message}")

        # check if the message is a valid handshake
        if initial_message.startswith(":"):
            preferences = initial_message.split(":", 1)[1]  # extract preferences
            add_client(client, preferences)
            print(f"Client {client} connected with preferences: {connected_clients[client]}")

        while True:
            try:
                # set a timeout for receiving messages
                message = await asyncio.wait_for(client.recv(), timeout=10)  # 10 seconds
            except asyncio.TimeoutError:
                print("Receive timed out, trying again.")
                continue  # keep the loop alive after timeout

            # check if the message is a special ping frame
            if message == "ping":
                await client.pong()
                print("Sent pong.")
            else:
                # broadcast the message to all other clients
                for ListClient in connected_clients:
                    if ListClient != client:
                        preferences = connected_clients[ListClient]

                        if preferences:
                            # client is known and has preferences
                            preferences_str = preferences  # take the single preference string

                            # Convert JSON string to Python object
                            # Convert the string to a Python dictionary
                            data = json.loads(message)

                            # Accessing the Left and Right hand data
                            left_hand = data["Left"]
                            right_hand = data["Right"]

                            # For Left hand
                            left_landmarks = left_hand["Landmarks"]
                            left_gesture = left_hand["Gesture"]
                            left_orientation = left_hand["Orientation"]

                            # For Right hand
                            right_landmarks = right_hand["Landmarks"]
                            right_gesture = right_hand["Gesture"]
                            right_orientation = right_hand["Orientation"]

                            # Prepare the sections
                            left_hand = {}
                            if preferences_str[0] == '1':
                                left_hand["Landmarks"] = left_landmarks if left_landmarks != "None" else None
                            if preferences_str[1] == '1':
                                left_hand["Orientation"] = left_orientation if left_orientation != "None" else None
                            if preferences_str[2] == '1':
                                left_hand["Gesture"] = left_gesture if left_gesture != "None" else None

                            right_hand = {}
                            if preferences_str[0] == '1':
                                right_hand["Landmarks"] = right_landmarks if right_landmarks != "None" else None
                            if preferences_str[1] == '1':
                                right_hand["Orientation"] = right_orientation if right_orientation != "None" else None
                            if preferences_str[2] == '1':
                                right_hand["Gesture"] = right_gesture if right_gesture != "None" else None

                            # Construct the final output JSON, removing keys with None values
                            output = {
                                "Left": {key: value for key, value in left_hand.items() if value is not None},
                                "Right": {key: value for key, value in right_hand.items() if value is not None}
                            }

                            # Printing the requested sections as formatted JSON
                            # print(json.dumps(output, indent=4))
                            await ListClient.send(json.dumps(output))
                # await client.send(f"Echo: {message}")

    except websockets.ConnectionClosed:
        print("Connection closed.")
    finally:
        remove_client(client)


async def main():
    print("Socket Server Starting")
    async with websockets.serve(echo, "localhost", 8765, ping_interval=None, ping_timeout=None):
        await asyncio.Future()  # run server indefinitely


def start_socket_server():
    asyncio.run(main())


if __name__ == "__main__":
    start_socket_server()
