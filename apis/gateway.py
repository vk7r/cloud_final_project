from flask import Flask, request, jsonify
import requests
import os

# Load the Trusted Host IP from environment variables
trusted_host_ip = os.getenv("TRUSTED_HOST_IP")
if not trusted_host_ip:
    raise RuntimeError("TRUSTED_HOST_IP environment variable not set")

app = Flask(__name__)

# Route for incoming requests
@app.route('/process', methods=['POST'])
def process_request():
    print("##########\n\nReceived request IN GATEWAY\n\n##########")

    data = request.json

    # Basic validation of the request
    if 'operation' not in data or 'query' not in data:
        return jsonify({"error": "Invalid request"}), 400
        

    # Forward validated requests to the Trusted Host using its private IP
    trusted_host_url = f"http://{trusted_host_ip}:5001/process"
    response = requests.post(trusted_host_url, json=data)

    return response.json(), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
