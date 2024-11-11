


# DOESNT WORK


def generate_worker_userdata(manager_ip, bin_file, position):
    return f"""#!/bin/bash

    # Update and install MySQL
    sudo apt-get update -y
    sudo apt-get install -y mysql-server

    # Start and enable MySQL service
    sudo systemctl start mysql
    sudo systemctl enable mysql

    # Set MySQL root password
    MYSQL_ROOT_PASSWORD="hej"

    # Configure MySQL root user with a password
    sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY '$MYSQL_ROOT_PASSWORD';"
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;"

    # Configure MySQL to allow remote connections (optional, for administration)
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE USER 'root'@'%' IDENTIFIED BY '$MYSQL_ROOT_PASSWORD';"
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;"
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;"

    # Configure the server ID (unique for each worker node)
    SERVER_ID=$(shuf -i 2-10000 -n 1)
    sudo sed -i "/[mysqld]/a server-id=$SERVER_ID" /etc/mysql/mysql.conf.d/mysqld.cnf

    # Allow connections from any IP address
    sudo sed -i "s/bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.cnf

    # Restart MySQL to apply changes
    sudo systemctl restart mysql

    # Download and extract the Sakila sample database
    wget https://downloads.mysql.com/docs/sakila-db.tar.gz
    tar -xzf sakila-db.tar.gz
    cd sakila-db
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" < sakila-schema.sql
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" < sakila-data.sql

    # Configure replication from the manager node
    MANAGER_IP="{manager_ip}"
    REPLICATION_USER="replication_user"
    REPLICATION_PASSWORD="replication_password"
    MASTER_LOG_FILE="{bin_file}"
    MASTER_LOG_POS={position}

    # Set up replication on the slave
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CHANGE MASTER TO MASTER_HOST='$MANAGER_IP', MASTER_USER='$REPLICATION_USER', MASTER_PASSWORD='$REPLICATION_PASSWORD', MASTER_LOG_FILE='$MASTER_LOG_FILE', MASTER_LOG_POS=$MASTER_LOG_POS;"
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "START SLAVE;"

    # Optional: Log the replication status for verification
    REPLICATION_STATUS_FILE="/var/log/mysql-replication-status.log"
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "SHOW SLAVE STATUS\\G" | sudo tee "$REPLICATION_STATUS_FILE"

    # Flask and other packages installation
    apt-get install python3 python3-pip -y
    pip3 install flask torch transformers requests pymysql --break-system-packages

    # Creating db_app.py with no indentation issues
    cat <<EOF > /home/ubuntu/db_app.py
from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'hej'
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
    return jsonify({{"status": "ok"}}), 200

@app.route('/execute', methods=['POST'])
def execute_query():
    data = request.json
    if 'operation' not in data or 'query' not in data:
        return jsonify({{"status": "error", "error": "Invalid request format"}}), 400

    operation = data['operation'].upper()
    query = data['query']

    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(query)
            if operation == 'READ':
                result = cursor.fetchall()
                return jsonify({{"status": "success", "data": result}}), 200
            elif operation == 'WRITE':
                connection.commit()
                return jsonify({{"status": "success", "message": "Write operation completed"}}), 200
            else:
                return jsonify({{"status": "error", "error": "Unknown operation type"}}), 400

    except Exception as e:
        return jsonify({{"status": "error", "error": str(e)}}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
EOF

    echo "Flask app created for database instance."
    """
