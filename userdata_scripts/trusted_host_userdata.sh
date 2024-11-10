#!/bin/bash

# Update and install necessary system packages
apt-get update;
apt-get install python3 python3-pip -y;

# Install Python packages required for the app
pip3 install flask torch transformers requests gunicorn --break-system-packages;


cat <<EOF > /home/ubuntu/trusted_host_app.py
from flask import Flask, request, jsonify
import requests
import json

# Load the Proxy IP from the JSON file
with open('instance_ips.json', 'r') as f:
    instance_ips = json.load(f)

try:
    proxy_ip = instance_ips["Proxy"]["private_ip"]
except KeyError:
    raise RuntimeError("Proxy private IP not found in instance_ips.json")

app = Flask(__name__)

# Direct Hit Route
@app.route('/directhit', methods=['POST'])
def forward_directhit():
    print("##########\n\nReceived request IN TRUSTED HOST (DIRECT HIT)\n\n##########")

    data = request.json

    # Forward request to Proxy's Direct Hit endpoint
    proxy_url = f"http://{proxy_ip}:5002/directhit"
    response = requests.post(proxy_url, json=data)

    return response.json(), response.status_code

# Random Route
@app.route('/random', methods=['POST'])
def forward_random():
    print("##########\n\nReceived request IN TRUSTED HOST (RANDOM)\n\n##########")

    data = request.json

    # Forward request to Proxy's Random endpoint
    proxy_url = f"http://{proxy_ip}:5002/random"
    response = requests.post(proxy_url, json=data)

    return response.json(), response.status_code

# Custom Route
@app.route('/custom', methods=['POST'])
def forward_custom():
    print("##########\n\nReceived request IN TRUSTED HOST (CUSTOMIZED)\n\n##########")

    data = request.json

    # Forward request to Proxy's Custom endpoint
    proxy_url = f"http://{proxy_ip}:5002/custom"
    response = requests.post(proxy_url, json=data)

    return response.json(), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
EOF

# Run the Flask app (or use gunicorn if preferred)
#gunicorn --bind 0.0.0.0:80 trusted_host_app:app