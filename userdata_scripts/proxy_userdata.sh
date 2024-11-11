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
    MANAGER_IP = instance_ips["db_manager"]["private_ip"]
    
    # Worker DB IPs
    worker_db_ips = [
        instance_ips["db_worker1"]["private_ip"],
        instance_ips["db_worker2"]["private_ip"]
    ]

    WORKER1_IP = instance_ips["db_worker1"]["private_ip"]
    WORKER2_IP = instance_ips["db_worker2"]["private_ip"]


except KeyError:
    raise RuntimeError("Database IPs not found in instance_ips.json")


# Function to measure the response time of an instance
def measure_instance_response_time(ip):
    try:
        response = requests.get(f"http://{ip}:5003/ping")
        response.raise_for_status()
        return response.elapsed.total_seconds()
    except requests.RequestException:
        return None


app = Flask(__name__)

# Route to handle read/write differentiation
@app.route('/process', methods=['POST'])
def process_request():
    print("##########\n\nReceived request IN PROXY\n\n##########")
    
    data = request.json

    return data


@app.route('/directhit', methods=['POST'])
def process_request_directhit():
    print("##########\n\nReceived request IN PROXY (DIRECT HIT)\n\n##########")
    
    # Get the JSON data from the user's request
    data = request.json

    # Forward the request to the manager instance's Flask app
    try:
        manager_response = requests.post(f"http://{MANAGER_IP}:5003/execute", json=data)
        manager_response.raise_for_status()  # Raise an error for bad responses

        # Return the response received from the manager instance back to the client
        return jsonify(manager_response.json()), manager_response.status_code

    except requests.RequestException as e:
        # Handle request errors
        return jsonify({"status": "error", "error": str(e)}), 500


@app.route('/random', methods=['POST'])
def process_request_random():
    print("##########\n\nReceived request IN PROXY (RANDOM)\n\n##########")
    
    # Get the JSON data from the user's request
    data = request.json
    
    # MAKE FUNCITON:
    # Check the operation type
    operation = data.get('operation', '').upper()

    # Choose the target URL based on the operation type
    if operation == "WRITE":
        # Forward to the manager instance for write operations
        target_url = f"http://{MANAGER_IP}:5003/execute"
        print("Operation is WRITE; sending request to manager instance.")
    elif operation == "READ":
        # Choose a random worker instance for read operations
        selected_worker_ip = random.choice(worker_db_ips)
        target_url = f"http://{selected_worker_ip}:5003/execute"
        print(f"Operation is READ; sending request to worker instance at {selected_worker_ip}.")
    else:
        # Return an error if the operation type is invalid
        return jsonify({"status": "error", "error": "Invalid operation type"}), 400

    # Forward the request to the selected instance's Flask app
    try:
        response = requests.post(target_url, json=data)
        response.raise_for_status()  # Raise an error for bad responses

        # Return the response received from the selected instance back to the client
        return jsonify(response.json()), response.status_code

    except requests.RequestException as e:
        # Handle request errors
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/custom', methods=['POST'])
def process_request_custom():
    print("##########\n\nReceived request IN PROXY (CUSTOMIZED)\n\n##########")
    
    # Get the JSON data from the user's request
    data = request.json


    # Measure the response time of each worker
    worker1_response_time = measure_instance_response_time(WORKER1_IP)
    print(f"Worker 1 response time: {worker1_response_time}")

    worker2_response_time = measure_instance_response_time(WORKER2_IP)
    print(f"Worker 2 response time: {worker2_response_time}")

    # Choose the worker with the faster response time
    if worker1_response_time is None and worker2_response_time is None:
        return jsonify({"status": "error", "error": "Both workers are down"}), 503
    elif worker1_response_time is None:
        selected_worker_ip = WORKER2_IP
    elif worker2_response_time is None:
        selected_worker_ip = WORKER1_IP
    else:
        selected_worker_ip = WORKER1_IP if worker1_response_time < worker2_response_time else WORKER2_IP

    print(f"Selected worker IP: {selected_worker_ip}")


    # Check the operation type
    operation = data.get('operation', '').upper()
    
    # Choose the target URL based on the operation type
    if operation == "WRITE":
        # Forward to the manager instance for write operations
        target_url = f"http://{MANAGER_IP}:5003/execute"
        print("Operation is WRITE; sending request to manager instance.")
    elif operation == "READ":
        # Choose a random worker instance for read operations
        selected_worker_ip = random.choice(worker_db_ips)
        target_url = f"http://{selected_worker_ip}:5003/execute"
        print(f"Operation is READ; sending request to worker instance at {selected_worker_ip}.")
    else:
        # Return an error if the operation type is invalid
        return jsonify({"status": "error", "error": "Invalid operation type"}), 400

    # Forward the request to the manager instance's Flask app
    try:
        worker_response = requests.post(target_url, json=data)
        worker_response.raise_for_status()  # Raise an error for bad responses

        # Return the response received from the manager instance back to the client
        return jsonify(worker_response.json()), worker_response.status_code

    except requests.RequestException as e:
        # Handle request errors
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
EOF

# Run the Flask app (or use gunicorn if preferred)
#gunicorn --bind 0.0.0.0:80 proxy_app:app