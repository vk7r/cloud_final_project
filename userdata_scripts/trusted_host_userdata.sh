#!/bin/bash

# Update and install necessary system packages
apt-get update;
apt-get install python3 python3-pip -y;

# Install Python packages required for the app
pip3 install flask torch transformers requests gunicorn --break-system-packages;


cat <<EOF > /home/ubuntu/trusted_host_app.py
from flask import Flask, request, jsonify
import requests
import os

# Load the Proxy IP from environment variables
proxy_ip = os.getenv("PROXY_IP")
if not proxy_ip:
    raise RuntimeError("PROXY_IP environment variable not set")

app = Flask(__name__)

# Route for internal communication from the Gateway
@app.route('/process', methods=['POST'])
def forward_request():
    print("##########\n\nReceived request IN TRUSTED HOST\n\n##########")

    data = request.json

    # Forward request to the Proxy using its private IP
    proxy_url = f"http://{proxy_ip}:5002/process"
    response = requests.post(proxy_url, json=data)

    return response.json(), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
EOF

# Run the Flask app (or use gunicorn if preferred)
#gunicorn --bind 0.0.0.0:80 trusted_host_app:app