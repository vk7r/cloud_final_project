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

@app.route('/process', methods=['POST'])
def process_request():
    print("##########\n\nReceived request IN PROXY\n\n##########")
    data = request.json
    return data

@app.route('/directhit', methods=['POST'])
def process_request_directhit():
    print("##########\n\nReceived request IN PROXY (DIRECT HIT)\n\n##########")
    
    data = request.json
    try:
        manager_response = requests.post(f"http://{MANAGER_IP}:5003/execute", json=data)
        manager_response.raise_for_status()
        
        db_response = manager_response.json()
        db_response.update({
            "pattern": "Direct Hit",
            "selected_instance": MANAGER_IP
        })
        return jsonify(db_response), manager_response.status_code

    except requests.RequestException as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "pattern": "Direct Hit",
            "selected_instance": MANAGER_IP
        }), 500

@app.route('/random', methods=['POST'])
def process_request_random():
    print("##########\n\nReceived request IN PROXY (RANDOM)\n\n##########")
    
    data = request.json
    operation = data.get('operation', '').upper()

    if operation == "WRITE":
        target_url = f"http://{MANAGER_IP}:5003/execute"
        selected_instance = MANAGER_IP
        pattern = "Random (WRITE to Manager)"
    elif operation == "READ":
        selected_worker_ip = random.choice(worker_db_ips)
        target_url = f"http://{selected_worker_ip}:5003/execute"
        selected_instance = selected_worker_ip
        pattern = "Random (READ to Worker - chosen randomly)"
    else:
        return jsonify({"status": "error", "error": "Invalid operation type"}), 400

    try:
        response = requests.post(target_url, json=data)
        response.raise_for_status()
        
        db_response = response.json()
        db_response.update({
            "pattern": pattern,
            "selected_instance": selected_instance
        })
        return jsonify(db_response), response.status_code

    except requests.RequestException as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "pattern": pattern,
            "selected_instance": selected_instance
        }), 500

@app.route('/custom', methods=['POST'])
def process_request_custom():
    print("##########\n\nReceived request IN PROXY (CUSTOMIZED)\n\n##########")
    
    data = request.json
    worker1_response_time = measure_instance_response_time(WORKER1_IP)
    worker2_response_time = measure_instance_response_time(WORKER2_IP)

    if worker1_response_time is None and worker2_response_time is None:
        return jsonify({
            "status": "error",
            "error": "Both workers are down",
            "pattern": "Custom (No Available Workers)"
        }), 503
    elif worker1_response_time is None:
        selected_worker_ip = WORKER2_IP
        response_time = worker2_response_time
    elif worker2_response_time is None:
        selected_worker_ip = WORKER1_IP
        response_time = worker1_response_time
    else:
        if worker1_response_time < worker2_response_time:
            selected_worker_ip = WORKER1_IP
            response_time = worker1_response_time
        else:
            selected_worker_ip = WORKER2_IP
            response_time = worker2_response_time

    operation = data.get('operation', '').upper()
    
    if operation == "WRITE":
        target_url = f"http://{MANAGER_IP}:5003/execute"
        selected_instance = MANAGER_IP
        pattern = "Custom (WRITE to Manager)"
    elif operation == "READ":
        target_url = f"http://{selected_worker_ip}:5003/execute"
        selected_instance = selected_worker_ip
        pattern = f"Custom (READ to Fastest Worker - {response_time}s response time)"
    else:
        return jsonify({"status": "error", "error": "Invalid operation type"}), 400

    try:
        worker_response = requests.post(target_url, json=data)
        worker_response.raise_for_status()
        
        db_response = worker_response.json()
        db_response.update({
            "pattern": pattern,
            "selected_instance": selected_instance,
        })
        return jsonify(db_response), worker_response.status_code

    except requests.RequestException as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "pattern": pattern,
            "selected_instance": selected_instance
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
