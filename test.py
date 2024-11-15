import requests
import json
from utils import util_functions as u

import globals as g

# Load instance IPs from JSON file
with open('resources/instance_ips.json', 'r') as f:
    instance_ips = json.load(f)

try:
    gatekeeper_ip = instance_ips["Gateway"]["public_ip"]
except KeyError:
    raise RuntimeError("IP not found in instance_ips.json")

print(f"Gatekeeper IP: {gatekeeper_ip}")

# Define the password for the Gatekeeper
GATEKEEPER_PASSWORD = g.GATEKEEPER_PASSWORD  # Replace with actual password if different

"""
The user should send the following:
- operation: "READ" or "WRITE" based on the type of request
- query: The SQL query to be executed

{
    "operation": "READ",  // or "WRITE" depending on the type of request
    "query": "SELECT * FROM sakila.actor"  // Example query; adjust based on the use case
}
"""

# Example payloads for testing
payload_read_all = {
    "operation": "READ",  
    "query": "SELECT * FROM actor"
}

payload_write = {
    "operation": "WRITE",  
    "query": "INSERT INTO actor (first_name, last_name, last_update) VALUES ('John', 'Doe', NOW())"
}

payload_read_specific = {
    "operation": "READ",
    "query": "SELECT * FROM actor WHERE first_name = 'John'"
}

#payload_read_all, payload_write, 
# Send the request to the Gatekeeper for each payload and endpoint
for payload in [payload_read_specific]:
    for path in ["directhit", "random", "custom"]:
        try:
            # Define the Gateway URL
            GATEWAY_URL = f"http://{gatekeeper_ip}:5000/{path}"

            # Send the request with the password header
            response = requests.post(
                GATEWAY_URL,
                json=payload,
                headers={"X-Gatekeeper-Password": GATEKEEPER_PASSWORD}
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                print(f"Response from Gateway ({path}):", json.dumps(response.json(), indent=2))
            else:
                print(f"Failed with status code {response.status_code} on path {path}")
                print("Error response:", response.text)

        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
