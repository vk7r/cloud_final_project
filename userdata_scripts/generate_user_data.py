
def generate_worker_userdata(manager_ip, bin_file, position):
    return """#!/bin/bash

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
    SERVER_ID=$(shuf -i 2-10000 -n 1)  # Generates a unique server ID for each worker
    sudo sed -i "/\\[mysqld\\]/a server-id=$SERVER_ID" /etc/mysql/mysql.conf.d/mysqld.cnf

    # Allow connections from any IP address
    sudo sed -i "s/bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.cnf

    # Restart MySQL to apply changes
    sudo systemctl restart mysql

    # Download the Sakila sample database files
    wget https://downloads.mysql.com/docs/sakila-db.tar.gz

    # Extract the downloaded file
    tar -xzf sakila-db.tar.gz
    cd sakila-db

    # Load the Sakila database structure and data into MySQL on the worker
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" < sakila-schema.sql
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" < sakila-data.sql

    # Configure replication from the manager node
    MANAGER_IP="{manager_ip}"  # Replace with the actual private IP of the manager instance
    REPLICATION_USER="replication_user"
    REPLICATION_PASSWORD="replication_password"

    # Get the master's log file and position
    MASTER_LOG_FILE="{bin_file}"  # Replace with the actual log file from master
    MASTER_LOG_POS={position}   # Replace with the actual log position from master

    # Set up replication on the slave
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CHANGE MASTER TO MASTER_HOST='$MANAGER_IP', MASTER_USER='$REPLICATION_USER', MASTER_PASSWORD='$REPLICATION_PASSWORD', MASTER_LOG_FILE='$MASTER_LOG_FILE', MASTER_LOG_POS=$MASTER_LOG_POS;"
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "START SLAVE;"

    # Optional: Log the replication status for verification
    REPLICATION_STATUS_FILE="/var/log/mysql-replication-status.log"
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "SHOW SLAVE STATUS\\G" | sudo tee "$REPLICATION_STATUS_FILE"

    echo "MySQL slave instance setup completed with Sakila database for replication."
    """ 