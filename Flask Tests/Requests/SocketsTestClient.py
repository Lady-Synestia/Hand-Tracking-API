import asyncio
import json
import time

import websockets


async def client():
    uri = "ws://localhost:8001"
    num_iterations = 100
    total_latency = 0.0

    async with websockets.connect(uri) as websocket:
        for i in range(num_iterations):
            data = {
                "vector": {"x": 1.0, "y": 2.0, "z": 3.0},
                "integer": 42,
                "float": 3.14
            }

            message = json.dumps(data)

            # start timing
            start_time = time.perf_counter()

            await websocket.send(message)
            print(f"Sent {i + 1}: {message}")

            # wait for the echoed response
            response = await websocket.recv()
            end_time = time.perf_counter()

            latency = (end_time - start_time) * 1000  # convert to ms
            total_latency += latency
            print(f"Received {i + 1}: {response}")
            print(f"Round-trip latency: {latency:.6f} ms")

        average_latency = total_latency / num_iterations
        print(f"\nAverage latency over {num_iterations} messages: {average_latency:.6f} ms")


if __name__ == "__main__":
    asyncio.run(client())
