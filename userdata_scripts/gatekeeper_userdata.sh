#!/bin/bash

# Update and install necessary system packages
apt-get update;
apt-get install python3 python3-pip -y;

# Install Python packages required for the app
pip3 install flask torch transformers requests gunicorn --break-system-packages;


cat <<EOF > /home/ubuntu/gatekeeper_app.py
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

# Define the hardcoded password (ideally, this should be set as an environment variable)
GATEKEEPER_PASSWORD = "your_secure_password"

# Authentication Middleware
# Is always run before any request is processed
@app.before_request
def authenticate():
    # Check for the password in the headers
    password = request.headers.get("X-Gatekeeper-Password")
    if password != GATEKEEPER_PASSWORD:
        # If password is incorrect, deny access
        return jsonify({"status": "error", "error": "Unauthorized access"}), 403

# Direct Hit Route
@app.route('/directhit', methods=['POST'])
def directhit():
    print("##########\n\nReceived request IN GATEWAY (DIRECT HIT)\n\n##########")

    data = request.json

    # Basic validation of the request
    if 'operation' not in data or 'query' not in data:
        return jsonify({"error": "Invalid request"}), 400

    # Forward request to Trusted Host's Direct Hit endpoint
    trusted_host_url = f"http://{trusted_host_ip}:5001/directhit"
    response = requests.post(trusted_host_url, json=data)

    return response.json(), response.status_code

# Random Route
@app.route('/random', methods=['POST'])
def random_pattern():
    print("##########\n\nReceived request IN GATEWAY (RANDOM)\n\n##########")

    data = request.json

    # Basic validation of the request
    if 'operation' not in data or 'query' not in data:
        return jsonify({"error": "Invalid request"}), 400

    # Forward request to Trusted Host's Random endpoint
    trusted_host_url = f"http://{trusted_host_ip}:5001/random"
    response = requests.post(trusted_host_url, json=data)

    return response.json(), response.status_code

# Custom Route
@app.route('/custom', methods=['POST'])
def custom_pattern():
    print("##########\n\nReceived request IN GATEWAY (CUSTOMIZED)\n\n##########")

    data = request.json

    # Basic validation of the request
    if 'operation' not in data or 'query' not in data:
        return jsonify({"error": "Invalid request"}), 400

    # Forward request to Trusted Host's Custom endpoint
    trusted_host_url = f"http://{trusted_host_ip}:5001/custom"
    response = requests.post(trusted_host_url, json=data)

    return response.json(), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Run the Flask app (or use gunicorn if preferred)
#gunicorn --bind 0.0.0.0:80 gateway_app:app