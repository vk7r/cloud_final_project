from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

# Database connection settings
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'hej'  # Use the password set in the userdata script
MYSQL_DB = 'sakila'

def connect_to_db():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/ping', methods=['GET'])
def ping():
    # Respond immediately to indicate the instance is reachable
    return jsonify({"status": "ok"}), 200

@app.route('/execute', methods=['POST'])
def execute_query():
    data = request.json

    # Validate request JSON
    if 'operation' not in data or 'query' not in data:
        return jsonify({"status": "error", "error": "Invalid request format"}), 400

    operation = data['operation'].upper()
    query = data['query']

    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            # Execute the query based on operation type
            cursor.execute(query)
            
            if operation == 'READ':
                # Fetch results for read operations
                result = cursor.fetchall()
                return jsonify({"status": "success", "data": result}), 200
            elif operation == 'WRITE':
                # Commit the transaction for write operations
                connection.commit()
                return jsonify({"status": "success", "message": "Write operation completed"}), 200
            else:
                return jsonify({"status": "error", "error": "Unknown operation type"}), 400

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)  # Run on port 5003 for database instances
