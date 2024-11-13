
import time
import os
import globals as g
import boto3
import stat

from utils import instance_setup as i
from utils import transfer_json_file as tj
from utils import util_functions as u
from utils import create_ip_list as cip
from userdata_scripts import generate_user_data as ud

if __name__ == "__main__":

    pem_file_path = g.pem_file_path

    # Create EC2 Client
    session = boto3.Session()
    ec2 = session.resource('ec2')

    # Read VPC and Subnet IDs from files
    with open(f'{g.aws_folder_path}/vpc_id.txt', 'r') as file:
        vpc_id = file.read().strip()
    with open(f'{g.aws_folder_path}/subnet_id.txt', 'r') as file:
        subnet_id = file.read().strip()


    # Delete keypair with same name, USED IN TESTING
    ec2.KeyPair(g.key_pair_name).delete()

    # Create a new key pair and save the .pem file
    key_pair = ec2.create_key_pair(KeyName=g.key_pair_name)

    # Change file permissions to 600 to protect the private key
    os.chmod(pem_file_path, stat.S_IWUSR) # Change security to be able to read
    # Save the private key to a .pem file
    with open(pem_file_path, 'w') as pem_file:
        pem_file.write(key_pair.key_material)
    os.chmod(pem_file_path, stat.S_IRUSR) # Change file permissions to 400 to protect the private key

    # Create public security group - used for all instances in the beginning for the setup
    public_sg_id = i.createPublicSecurityGroup(vpc_id, g.public_security_group_name)

    with open('userdata_scripts/manager_data.sh', 'r') as file:
        manager_userdata = file.read()

    with open('userdata_scripts/gateway_userdata.sh', 'r') as file:
        gateway_userdata = file.read()

    with open('userdata_scripts/proxy_userdata.sh', 'r') as file:
        proxy_userdata = file.read()

    with open('userdata_scripts/trusted_host_userdata.sh', 'r') as file:
        th_userdata = file.read()


    # Manager Instance (internal)
    i.createInternalInstance('t2.large', 1, 1, key_pair, public_sg_id, subnet_id, manager_userdata, 'db_manager')

    time.sleep(180) # Wait for manager to be ready

    # Transfer the master config to this machine
    u.transfer_file_from_ec2(u.get_manager_instance_id(), "/home/ubuntu/MASTER_INFO.txt","resources/MASTER_STATUS.txt", g.pem_file_path)
    # Parse the txt output and save it as a json file
    u.parse_master_status("resources/MASTER_STATUS.txt", "resources/MASTER_CONFIG.json")
    master_config = u.load_config("resources/MASTER_CONFIG.json")


    MANAGER_PRIVATE_IP = u.get_manager_private_ip()

    # Configure the database workers userdata
    # worker_userdata = ud.generate_worker_userdata(MANAGER_PRIVATE_IP, master_config["File"], master_config["Position"])
    # print(worker_userdata)

    worker_userdata = f"""#!/bin/bash

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
    MANAGER_IP="{MANAGER_PRIVATE_IP}"  # Replace with the actual private IP of the manager instance
    REPLICATION_USER="replication_user"
    REPLICATION_PASSWORD="replication_password"

    # Get the master's log file and position
    MASTER_LOG_FILE="{master_config["File"]}"  # Replace with the actual log file from master
    MASTER_LOG_POS={master_config["Position"]}              # Replace with the actual log position from master

    # Set up replication on the slave
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CHANGE MASTER TO MASTER_HOST='$MANAGER_IP', MASTER_USER='$REPLICATION_USER', MASTER_PASSWORD='$REPLICATION_PASSWORD', MASTER_LOG_FILE='$MASTER_LOG_FILE', MASTER_LOG_POS=$MASTER_LOG_POS;"
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "START SLAVE;"

    # Optional: Log the replication status for verification
    REPLICATION_STATUS_FILE="/var/log/mysql-replication-status.log"
    sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "SHOW SLAVE STATUS\\G" | sudo tee "$REPLICATION_STATUS_FILE"

    echo "MySQL slave instance setup completed with Sakila database for replication."

    apt-get install python3 python3-pip -y;
    pip3 install flask requests pymysql --break-system-packages;

    sudo apt-get install sysbench -y;
    """


    # 2x MySQL Worker Instances (internal)
    # ANVÄNDER PUBLIC SECURITY GROUP I BÖRJAN
    print("Creating workers")
    i.createInternalInstance('t2.micro', 1,1, key_pair, public_sg_id, subnet_id, worker_userdata, 'db_worker1')
    i.createInternalInstance('t2.micro', 1,1, key_pair, public_sg_id, subnet_id, worker_userdata, 'db_worker2')

    # Proxy Instance (internal)
    i.createInstance('t2.large', 1, 1, key_pair, public_sg_id, subnet_id, proxy_userdata, 'proxy')

    # Gatekeeper Instance (public)
    i.createInstance('t2.large', 1, 1, key_pair, public_sg_id, subnet_id, gateway_userdata, 'gatekeeper')

    # Trusted Host Instance (internal)
    i.createInternalInstance('t2.large', 1, 1, key_pair, public_sg_id, subnet_id, th_userdata, 'trusted-host')

    cip.fetch_and_save_instance_ips("resources/instance_ips.json")
    
    # Transfer instance_ips.json to every instance
    tj.transfer_json_file_to_all(pem_file_path, "resources/instance_ips.json")

    # Transfer the database.py file to the db_worker instances
    tj.transfer_file_to_instance(pem_file_path, "apis/database.py", "db_app.py", "db_worker1")
    tj.transfer_file_to_instance(pem_file_path, "apis/database.py", "db_app.py", "db_worker2")

    time.sleep(270)

    print("Running sysbench on the db_manager and db_worker instances...")
    # Run sysbench on the db_manager and db_worker instances
    u.ssh_and_run_command(u.get_instance_ip_by_name("db_manager"), g.pem_file_path, 'sudo sysbench /usr/share/sysbench/oltp_read_only.lua --mysql-db=sakila --mysql-user="root" --mysql-password="hej" run > sysbench_results.txt')
    u.ssh_and_run_command(u.get_instance_ip_by_name("db_worker1"), g.pem_file_path, 'sudo sysbench /usr/share/sysbench/oltp_read_only.lua --mysql-db=sakila --mysql-user="root" --mysql-password="hej" run > sysbench_results.txt')
    u.ssh_and_run_command(u.get_instance_ip_by_name("db_worker2"), g.pem_file_path, 'sudo sysbench /usr/share/sysbench/oltp_read_only.lua --mysql-db=sakila --mysql-user="root" --mysql-password="hej" run > sysbench_results.txt')
    
    time.sleep(10)

    # Collect results from sysbench
    u.transfer_file_from_ec2(u.get_instance_id_by_name("db_manager"), "/home/ubuntu/sysbench_results.txt", "test_results/sysbench_results_manager.txt", g.pem_file_path)
    u.transfer_file_from_ec2(u.get_instance_id_by_name("db_worker1"), "/home/ubuntu/sysbench_results.txt", "test_results/sysbench_results_worker1.txt", g.pem_file_path)
    u.transfer_file_from_ec2(u.get_instance_id_by_name("db_worker2"), "/home/ubuntu/sysbench_results.txt", "test_results/sysbench_results_worker2.txt", g.pem_file_path)

    print("starting all flask apps...")
    # Start the flask apps
    u.ssh_and_run_command(u.get_instance_ip_by_name("gatekeeper"), g.pem_file_path, "nohup python3 gateway_app.py > app.log 2>&1 &")
    u.ssh_and_run_command(u.get_instance_ip_by_name("trusted-host"), g.pem_file_path, "nohup python3 trusted_host_app.py > app.log 2>&1 &")
    u.ssh_and_run_command(u.get_instance_ip_by_name("proxy"), g.pem_file_path, "nohup python3 proxy_app.py  > app.log 2>&1 &")
   
    u.ssh_and_run_command(u.get_instance_ip_by_name("db_manager"), g.pem_file_path, "nohup python3 db_app.py  > app.log 2>&1 &")
    u.ssh_and_run_command(u.get_instance_ip_by_name("db_worker1"), g.pem_file_path, "nohup python3 db_app.py  > app.log 2>&1 &")
    u.ssh_and_run_command(u.get_instance_ip_by_name("db_worker2"), g.pem_file_path, "nohup python3 db_app.py  > app.log 2>&1 &")

    print("SET UP COMPLETE")

    print("Making instances private...")
    time.sleep(10)

    # Create internal security group
    private_sg_id = i.createInternalSecurityGroup(vpc_id, g.internal_security_group_name, public_sg_id)

    # Update security groups
    i.update_sec_group(u.get_instance_id_by_name("trusted-host"), private_sg_id)
    i.update_sec_group(u.get_instance_id_by_name("proxy"), private_sg_id)
    i.update_sec_group(u.get_instance_id_by_name("db_manager"), private_sg_id)
    i.update_sec_group(u.get_instance_id_by_name("db_worker1"), private_sg_id)
    i.update_sec_group(u.get_instance_id_by_name("db_worker2"), private_sg_id)
    