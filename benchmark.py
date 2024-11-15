import requests
import json
import os
from utils import util_functions as u
import globals as g
import time

# Load instance IPs from JSON file
with open('resources/instance_ips.json', 'r') as f:
    instance_ips = json.load(f)

try:
    gatekeeper_ip = instance_ips["Gateway"]["public_ip"]
except KeyError:
    raise RuntimeError("IP not found in instance_ips.json")

print(f"Gatekeeper IP: {gatekeeper_ip}")

# Oassword for the Gatekeeper
GATEKEEPER_PASSWORD = g.GATEKEEPER_PASSWORD  # Replace with actual password

ITERATIONS = 1000

# Cloud patterns to test
patterns = ["directhit", "random", "custom"]

# Perform 1000 WRITE and 1000 READ operations for each cloud pattern
for pattern in patterns:
    # Start time for the current pattern
    start_time = time.time()

    print(f"Testing pattern: {pattern}")
    # Define file path for the current pattern
    file_path = f"test_results/{pattern}_results.txt"

    # Open a results file for the current pattern (create if it doesn’t exist)
    with open(file_path, "w") as results_file:
        print("writing to file...")
        results_file.write(f"Testing pattern: {pattern}\n")
        results_file.write("="*40 + "\n\n")

        # Define the Gateway URL
        GATEWAY_URL = f"http://{gatekeeper_ip}:5000/{pattern}"

        # Track success and failure counts for read and write
        write_success, write_fail = 0, 0
        read_success, read_fail = 0, 0

        # Store detailed results to print after the summary
        detailed_results = []

        # Run 1000 WRITE and 1000 READ tests
        for i in range(ITERATIONS):
            # Write payload with a unique name for each iteration
            payload_write = {
                "operation": "WRITE",
                "query": f"INSERT INTO actor (first_name, last_name, last_update) VALUES ('TestName{i}', 'TestSurname', NOW())"
            }
            
            # Attempt WRITE request
            try:
                response = requests.post(
                    GATEWAY_URL,
                    json=payload_write,
                    headers={"X-Gatekeeper-Password": GATEKEEPER_PASSWORD}
                )
                if response.status_code == 200:
                    write_success += 1
                    detailed_results.append(f"WRITE {i+1}: Status {response.status_code}, Response: {payload_write}\n")

                else:
                    write_fail += 1
                    detailed_results.append(f"WRITE {i+1}: Status {response.status_code}, Response: {response.text}\n")
            except requests.exceptions.RequestException as e:
                write_fail += 1
                detailed_results.append(f"WRITE error on attempt {i+1}: {e}\n")

            # Read payload to confirm the WRITE using the same unique first_name
            payload_read = {
                "operation": "READ",
                "query": f"SELECT * FROM actor WHERE first_name = 'TestName{i}'"
            }
            
            # Attempt READ request
            try:
                response = requests.post(
                    GATEWAY_URL,
                    json=payload_read,
                    headers={"X-Gatekeeper-Password": GATEKEEPER_PASSWORD}
                )
                if response.status_code == 200 and response.json().get("data"):
                    read_success += 1
                    detailed_results.append(f"READ {i+1}: Status {response.status_code}, Response: {response.text}\n")
                else:
                    read_fail += 1
                    detailed_results.append(f"READ {i+1}: Status {response.status_code}, Response: {response.text}\n")
            except requests.exceptions.RequestException as e:
                read_fail += 1
                detailed_results.append(f"READ error on attempt {i+1}: {e}\n")

        # Calculate elapsed time for the current pattern
        elapsed_time = time.time() - start_time

        # Write summary results for the current pattern
        results_file.write(f"Total Elapsed Time: {elapsed_time:.2f} seconds\n\n")
        results_file.write(f"Total WRITE operations: 1000\n")
        results_file.write(f"WRITE Success: {write_success}\n")
        results_file.write(f"WRITE Failures: {write_fail}\n\n")
        results_file.write(f"Total READ operations: 1000\n")
        results_file.write(f"READ Success: {read_success}\n")
        results_file.write(f"READ Failures: {read_fail}\n")

        # Append detailed results after the summary
        results_file.write("\nDetailed Results:\n")
        results_file.write("="*40 + "\n")
        results_file.writelines(detailed_results)
