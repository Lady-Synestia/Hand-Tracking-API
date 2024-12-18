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
                            data = json.loads(message)
                            requested_sections = []

                            # checking each position in the preferences
                            if preferences_str[0] == '1':
                                # print("Sending Orientations")
                                requested_sections.append(data[0])
                            if preferences_str[1] == '1':
                                # print("Sending tracking points")
                                requested_sections.append(data[1])
                            if preferences_str[2] == '1':
                                # print("Sending Gestures")
                                requested_sections.append(data[2])

                            # print(json.dumps(requested_sections))
                            await ListClient.send(json.dumps(requested_sections))
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
