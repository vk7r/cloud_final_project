import requests
import json
from utils import util_functions as u


with open('instance_ips.json', 'r') as f:
    instance_ips = json.load(f)

try:
    gatekeeper_ip = instance_ips["Gateway"]["public_ip"]
except KeyError:
    raise RuntimeError("IP not found in instance_ips.json")

print(f"Gatekeeper IP: {gatekeeper_ip}")


# Define the Gateway URL (replace with your Gateway's public IP)
GATEWAY_URL = f"http://{gatekeeper_ip}:5000/process"

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

# from utils import util_functions as u
# import globals as g

# u.ssh_and_run_command(u.get_instance_ip_by_name("gatekeeper"), g.pem_file_path, "nohup python3 gateway_app.py > app.log 2>&1 &")
# u.ssh_and_run_command(u.get_instance_ip_by_name("trusted-host"), g.pem_file_path, "nohup python3 trusted_host_app.py > app.log 2>&1 &")
# u.ssh_and_run_command(u.get_instance_ip_by_name("proxy"), g.pem_file_path, "nohup python3 proxy_app.py  > app.log 2>&1 &")
