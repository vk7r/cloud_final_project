import requests
import json

# Define the Gateway URL (replace with your Gateway's public IP)
GATEWAY_URL = "http://34.207.193.21:5000/process"

# Define the payload for the request
payload = {
    "operation": "read",  # or "write" based on what you want to test
    "query": "SELECT * FROM actor"  # example query for a read operation
}

# Send the request to the Gateway
try:
    response = requests.post(GATEWAY_URL, json=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Response from Gateway:", json.dumps(response.json(), indent=2))
    else:
        print(f"Failed with status code {response.status_code}")
        print("Error response:", response.text)

except requests.exceptions.RequestException as e:
    print("An error occurred:", e)

