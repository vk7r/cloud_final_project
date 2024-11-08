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
