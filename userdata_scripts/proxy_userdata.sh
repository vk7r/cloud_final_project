#!/bin/bash

# Update and install necessary system packages
apt-get update;
apt-get install python3 python3-pip -y;

# Install Python packages required for the app
pip3 install flask torch transformers requests gunicorn --break-system-packages;


cat <<EOF > /home/ubuntu/proxy_app.py
from flask import Flask, request, jsonify
import random
import requests
import json

# Load database IPs from the JSON file
with open('instance_ips.json', 'r') as f:
    instance_ips = json.load(f)

try:
    # Manager DB IP
    manager_db_ip = instance_ips["db_manager"]["private_ip"]
    
    # Worker DB IPs
    worker_db_ips = [
        instance_ips["db_worker1"]["private_ip"],
        instance_ips["db_worker2"]["private_ip"]
    ]
except KeyError:
    raise RuntimeError("Database IPs not found in instance_ips.json")

app = Flask(__name__)

# Route to handle read/write differentiation
@app.route('/process', methods=['POST'])
def process_request():
    print("##########\n\nReceived request IN PROXY\n\n##########")
    
    data = request.json

    return data

# Worker selection logic (random selection for load balancing)
def select_worker():
    return random.choice(worker_db_ips)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
EOF

# Run the Flask app (or use gunicorn if preferred)
#gunicorn --bind 0.0.0.0:80 proxy_app:app