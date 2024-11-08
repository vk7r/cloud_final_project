#!/bin/bash

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

# Allow remote root login (for testing; restrict in production)
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE USER 'root'@'%' IDENTIFIED BY '$MYSQL_ROOT_PASSWORD';"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;"

# Configure MySQL for replication
REPLICATION_USER="replication_user"
REPLICATION_PASSWORD="replication_password"

# Create a replication user with mysql_native_password plugin to avoid SSL issues
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE USER '$REPLICATION_USER'@'%' IDENTIFIED WITH 'mysql_native_password' BY '$REPLICATION_PASSWORD';"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "GRANT REPLICATION SLAVE ON *.* TO '$REPLICATION_USER'@'%';"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;"

# Configure MySQL settings for replication
sudo sed -i "/\[mysqld\]/a server-id=1" /etc/mysql/mysql.conf.d/mysqld.cnf  # Sets a unique server ID for the master (required for replication)
sudo sed -i "/\[mysqld\]/a log_bin=mysql-bin" /etc/mysql/mysql.conf.d/mysqld.cnf  # Enables binary logging, necessary for capturing changes for replication
sudo sed -i "/\[mysqld\]/a binlog_do_db=sakila" /etc/mysql/mysql.conf.d/mysqld.cnf  # Restricts replication to the 'sakila' database only
sudo sed -i "s/bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.cnf  # Allows MySQL to accept connections from any IP address

# Restart MySQL to apply changes
sudo systemctl restart mysql

# Download the Sakila sample database files
wget https://downloads.mysql.com/docs/sakila-db.tar.gz

# Extract the downloaded file
tar -xzf sakila-db.tar.gz

# Change to the Sakila directory
cd sakila-db

# Load the Sakila database structure and data into MySQL
mysql -u root -p"$MYSQL_ROOT_PASSWORD" < sakila-schema.sql
mysql -u root -p"$MYSQL_ROOT_PASSWORD" < sakila-data.sql

# Log the master status for reference
MASTER_INFO_FILE="/home/ubuntu/MASTER_INFO.txt"
sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "SHOW MASTER STATUS\G" > "$MASTER_INFO_FILE"


echo "MySQL master instance setup completed with Sakila database for replication."
