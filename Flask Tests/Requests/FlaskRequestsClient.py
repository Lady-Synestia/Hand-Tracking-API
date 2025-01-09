import requests
import time

url = "http://135.181.160.44:25575/"

num_requests = 100
total_duration = 0.0

for i in range(num_requests):
    # record the start time
    start_time = time.time()

    # send a GET request
    response = requests.get(url)

    # record the end time
    end_time = time.time()

    # calculate the duration in milliseconds
    duration_ms = (end_time - start_time) * 1000
    total_duration += duration_ms

    # check if the request was successful
    if response.status_code == 200:
        print(f"Request {i+1} - Response Data:", response.json())
        print(f"Request {i+1} took {duration_ms:.2f} ms.")
    else:
        print(f"Request {i+1} failed. Status code:", response.status_code)
        print(f"Request {i+1} took {duration_ms:.2f} ms.")

# calculate average duration
average_duration = total_duration / num_requests
print(f"\nAverage request time over {num_requests} requests: {average_duration:.2f} ms")
