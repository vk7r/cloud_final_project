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
import os

# Load database IPs from environment variables
manager_db_ip = os.getenv("MANAGER_DB_IP")
worker_db_ips = os.getenv("WORKER_DB_IPS").split(",") if os.getenv("WORKER_DB_IPS") else []

if not manager_db_ip or not worker_db_ips:
    raise RuntimeError("Database IP environment variables not set")

app = Flask(__name__)

# Route to handle read/write differentiation
@app.route('/process', methods=['POST'])
def process_request():
    print("##########\n\nReceived request IN PROXY\n\n##########")
    
    data = request.json
    query = data.get('query')
    
    # Validate the query presence
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Determine if the query is read (SELECT) or write (INSERT, UPDATE, DELETE)
    if query.strip().upper().startswith('SELECT'):
        # Route to one of the worker nodes for read operations
        worker_db_ip = select_worker()
        response = requests.post(f"http://{worker_db_ip}:5003/execute", json={"query": query})
    else:
        # Route to the manager node for write operations
        response = requests.post(f"http://{manager_db_ip}:5003/execute", json={"query": query})

    return response.json(), response.status_code

# Worker selection logic (random selection for load balancing)
def select_worker():
    return random.choice(worker_db_ips)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
EOF

# Run the Flask app (or use gunicorn if preferred)
#gunicorn --bind 0.0.0.0:80 proxy_app:app