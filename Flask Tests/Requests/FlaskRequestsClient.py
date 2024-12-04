import requests

# Define the URL for the Flask app endpoint
url = "http://135.181.160.44:25575/"

# Send a GET request
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    print("Response Data:", response.json())
else:
    print("Failed to access endpoint. Status code:", response.status_code)
