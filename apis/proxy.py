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

@app.route('/directhit', methods=['POST'])
def process_request_directhit():
    print("##########\n\nReceived request IN PROXY (DIRECT HIT)\n\n##########")
    
    # Create the custom response with the required pattern
    response_data = {
        "message": "Received request in proxy! DIRECT HIT PATTERN"
    }
    
    # Return the response as JSON
    return jsonify(response_data)


@app.route('/random', methods=['POST'])
def process_request_random():
    print("##########\n\nReceived request IN PROXY (RANDOM)\n\n##########")
    
    #return random.choice(worker_db_ips)

    # Create the custom response with the required pattern
    response_data = {
        "message": "Received request in proxy! RANDOM PATTERN"
    }
    
    # Return the response as JSON
    return jsonify(response_data)


@app.route('/custom', methods=['POST'])
def process_request_custom():
    print("##########\n\nReceived request IN PROXY (CUSTOMIZED)\n\n##########")
    
    # Create the custom response with the required pattern
    response_data = {
        "message": "Received request in proxy! CUSTOMIZED PATTERN"
    }
    
    # Return the response as JSON
    return jsonify(response_data)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)


#query = data.get('query')

# # Validate the query presence
# if not query:
#     return jsonify({"error": "No query provided"}), 400

# # Determine if the query is read (SELECT) or write (INSERT, UPDATE, DELETE)
# if query.strip().upper().startswith('SELECT'):
#     # Route to one of the worker nodes for read operations
#     worker_db_ip = select_worker()
#     response = requests.post(f"http://{worker_db_ip}:5003/execute", json={"query": query})
# else:
#     # Route to the manager node for write operations
#     response = requests.post(f"http://{manager_db_ip}:5003/execute", json={"query": query})

# return response.json(), response.status_code