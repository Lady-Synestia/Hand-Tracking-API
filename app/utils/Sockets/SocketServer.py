import asyncio
import websockets

connected_clients = set()


async def echo(client):
    connected_clients.add(client)
    try:
        while True:
            try:
                # set a timeout for receiving messages
                message = await asyncio.wait_for(client.recv(), timeout=10)  # 10 seconds
            except asyncio.TimeoutError:
                print("No message received. Checking connection...")
                continue  # keep the loop alive after timeout

            # check if the message is a special ping frame
            if message == "ping":
                await client.pong()
                print("Sent pong")
            else:
                # print(f"Received message: {message}")
                for ListClient in connected_clients:
                    if ListClient != client:
                        await ListClient.send(message)
                        print("Forwarded message")
                await client.send(f"Echo: {message}")

    except websockets.ConnectionClosed:
        print("Connection closed")
    finally:
        connected_clients.remove(client)


async def main():
    print("Socket Server Starting")
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run server indefinitely


def start_socket_server():
    asyncio.run(main())


if __name__ == "__main__":
    start_socket_server()
