from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
import json

app = Flask(__name__)

# Load MySQL host IP from the JSON file
with open('instance_ips.json', 'r') as f:
    instance_ips = json.load(f)

try:
    # Assuming the MySQL server runs on the db_manager node
    mysql_host_ip = instance_ips["db_manager"]["private_ip"]
except KeyError:
    raise RuntimeError("MySQL host IP (db_manager) not found in instance_ips.json")

# MySQL connection configuration
db_config = {
    'user': 'root',                # MySQL user (root)
    'password': 'hej',             # MySQL root password as per the setup script
    'host': mysql_host_ip,         # MySQL host IP from the JSON file
    'database': 'sakila'           # Using the Sakila database as configured
}

@app.route('/execute', methods=['POST'])
def execute_query():
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Connect to MySQL using the defined configuration
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Execute the query and handle the result based on the query type
        cursor.execute(query)
        
        # For SELECT queries, fetch the results
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [col[0] for col in cursor.description]  # Column names for readability
            result_list = [dict(zip(columns, row)) for row in results]
            result = {"results": result_list}
        else:
            # For write queries (INSERT, UPDATE, DELETE)
            conn.commit()
            result = {"message": "Query executed successfully"}

    except Error as err:
        # Handle any MySQL errors
        result = {"error": str(err)}
    finally:
        cursor.close()
        conn.close()

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
