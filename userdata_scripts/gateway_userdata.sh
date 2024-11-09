#!/bin/bash

# Update and install necessary system packages
apt-get update;
apt-get install python3 python3-pip -y;

# Install Python packages required for the app
pip3 install flask torch transformers requests gunicorn --break-system-packages;


cat <<EOF > /home/ubuntu/gateway_app.py
from flask import Flask, request, jsonify
import requests
import json

# Load the Trusted Host IP from the JSON file
with open('instance_ips.json', 'r') as f:
    instance_ips = json.load(f)

try:
    trusted_host_ip = instance_ips["Trusted_host"]["private_ip"]
except KeyError:
    raise RuntimeError("Trusted Host IP not found in instance_ips.json")

app = Flask(__name__)

# Route for incoming requests
@app.route('/process', methods=['POST'])
def process_request():
    print("##########\n\nReceived request IN GATEWAY\n\n##########")

    data = request.json

    # Basic validation of the request
    if 'operation' not igunicorn --bind 0.0.0.0:80 gateway_app:appn data or 'query' not in data:
        return jsonify({"error": "Invalid request"}), 400

    # Forward validated requests to the Trusted Host using its private IP
    trusted_host_url = f"http://{trusted_host_ip}:5001/process"
    response = requests.post(trusted_host_url, json=data)

    return response.json(), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Run the Flask app (or use gunicorn if preferred)
#gunicorn --bind 0.0.0.0:80 gateway_app:app