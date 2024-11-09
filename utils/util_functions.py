import boto3
import paramiko
import time
import json

'''
Description: Connects to an EC2 instance via SSH and runs a specified Python script.
Inputs: 
    instance_ip (str) - The public IP address of the EC2 instance.
    pem_file_path (str) - The file path to the PEM file used for SSH authentication.
    file_name (str) - The name of the Python script to run on the instance.
Outputs: None (prints connection status and script execution results).
'''
def ssh_and_run_py_script(instance_ip: str, pem_file_path: str, file_name :str):
    try:
        print(f"Connecting to {instance_ip} using SSH...")
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the instance
        ssh.connect(instance_ip, username='ubuntu', key_filename=pem_file_path)
        
        print(f"Connected, now running {file_name}...")

        # Run the command to execute the Python script
        stdin, stdout, stderr = ssh.exec_command(f'python3 {file_name}.py')
        
        # Close the SSH connection
        ssh.close()
        print("SSH connection closed.")

    except Exception as e:
        print(f"An error occurred during SSH: {str(e)}")

def ssh_and_run_command(instance_ip:str, pem_file_path:str, command_str:str):
    try:
        print(f"Connecting to {instance_ip} using SSH...")
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the instance
        ssh.connect(instance_ip, username='ubuntu', key_filename=pem_file_path)
        
        print(f"Connected, now running command: {command_str}")

        # Run the command to execute the Python script
        stdin, stdout, stderr = ssh.exec_command(f'{command_str}')
        
        # Close the SSH connection
        time.sleep(5)
        ssh.close()
        print("SSH connection closed.")

    except Exception as e:
        print(f"An error occurred during SSH: {str(e)}")

# Attaches terminal to the script
def ssh_and_run_command_tmux(instance_ip: str, pem_file_path: str, command_str: str):
    try:
        print(f"Connecting to {instance_ip} using SSH...")
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the instance
        ssh.connect(instance_ip, username='ubuntu', key_filename=pem_file_path)
        
        print(f"Connected, now running command inside tmux: {command_str}")

        # Use tmux to ensure the process has a persistent TTY
        tmux_command = f"tmux new-session -d -s mysession '{command_str}'"
        
        # Run the command inside a tmux session
        ssh.exec_command(tmux_command)
        
        # Allow the command to start and then close the SSH connection
        time.sleep(5)
        ssh.close()
        print("SSH connection closed. The process is running inside a tmux session.")

    except Exception as e:
        print(f"An error occurred during SSH: {str(e)}")



def transfer_file_to_ec2(instance_id, file_path, destination_path, key_path, username='ubuntu'):
    """
    Transfer a file to an EC2 instance via SFTP.

    :param instance_id: EC2 instance ID
    :param file_path: Local path of the file to be transferred
    :param destination_path: Destination path on the EC2 instance
    :param key_path: Path to the private key file (e.g., .pem file) for SSH authentication
    :param username: Username for the EC2 instance (default: 'ubuntu')
    """
    try:
        # Initialize EC2 resource
        ec2 = boto3.client('ec2')
        
        # Get the public DNS or IP address of the EC2 instance
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance_info = response['Reservations'][0]['Instances'][0]
        public_ip = instance_info.get('PublicIpAddress') or instance_info.get('PublicDnsName')

        print(f"Public IP: {public_ip}")

        if not public_ip:
            raise ValueError("Instance does not have a public IP or DNS")

        # Initialize the SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(key_path)

        # Connect to the EC2 instance
        print(f"Connecting to EC2 instance {instance_id} at {public_ip}...")
        ssh.connect(hostname=public_ip, username=username, pkey=private_key)

        # Open SFTP session
        sftp = ssh.open_sftp()

        # Transfer the file
        print(f"Transferring {file_path} to {destination_path} on EC2 instance...")
        sftp.put(file_path, destination_path)

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

        print("File transfer successful!")

    except Exception as e:
        print(f"Error occurred during file transfer: {str(e)}")

import boto3
import paramiko

def transfer_file_from_ec2(instance_id, remote_file_path, local_destination_path, key_path, username='ubuntu'):
    """
    Transfer a file from an EC2 instance to the local machine via SFTP.

    :param instance_id: EC2 instance ID
    :param remote_file_path: Path of the file on the EC2 instance to be transferred
    :param local_destination_path: Local path where the file will be saved
    :param key_path: Path to the private key file (e.g., .pem file) for SSH authentication
    :param username: Username for the EC2 instance (default: 'ubuntu')
    """
    try:
        # Initialize EC2 client
        ec2 = boto3.client('ec2')
        
        # Get the public IP or DNS of the EC2 instance
        response = ec2.describe_instances(InstanceIds=[instance_id])
        instance_info = response['Reservations'][0]['Instances'][0]
        public_ip = instance_info.get('PublicIpAddress') or instance_info.get('PublicDnsName')

        print(f"Public IP: {public_ip}")

        if not public_ip:
            raise ValueError("Instance does not have a public IP or DNS")

        # Initialize the SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(key_path)

        # Connect to the EC2 instance
        print(f"Connecting to EC2 instance {instance_id} at {public_ip}...")
        ssh.connect(hostname=public_ip, username=username, pkey=private_key)

        # Open SFTP session
        sftp = ssh.open_sftp()

        # Download the file
        print(f"Transferring {remote_file_path} from EC2 instance to {local_destination_path} on local machine...")
        sftp.get(remote_file_path, local_destination_path)

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

        print("File transfer successful!")

    except Exception as e:
        print(f"Error occurred during file transfer: {str(e)}")



def get_manager_instance_id():
    # Initialize the EC2 client
    ec2_client = boto3.client('ec2')

    # Describe all running EC2 instances with the 'orchestrator-instance' tag
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',  # Filter by the 'Name' tag
                'Values': ['db_manager']  # Only instances with the 'orchestrator-instance' tag
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']  # Only running instances
            }
        ]
    )

    # Extract the details of the orchestrator instance
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            # print(f"Orchestrator Instance Found: Instance ID: {instance_id}")
            
            # Return the Instance ID
            return instance_id
    
    print("No running orchestrator-instance found.")
    return None

def get_instance_id_by_name(instance_name):
    # Initialize the EC2 client
    ec2_client = boto3.client('ec2')

    # Describe all running EC2 instances with the 'orchestrator-instance' tag
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',  # Filter by the 'Name' tag
                'Values': [instance_name]  # Only instances with the 'orchestrator-instance' tag
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']  # Only running instances
            }
        ]
    )

    # Extract the details of the orchestrator instance
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            # print(f"Orchestrator Instance Found: Instance ID: {instance_id}")
            
            # Return the Instance ID
            return instance_id
    
    print("No running orchestrator-instance found.")
    return None




def get_instance_ip_by_name(instance_name):
    # Initialize the EC2 client
    ec2_client = boto3.client('ec2')

    # Describe all running EC2 instances with the 'orchestrator-instance' tag
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',  # Filter by the 'Name' tag
                'Values': [instance_name]  # Only instances with the 'orchestrator-instance' tag
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']  # Only running instances
            }
        ]
    )

    # Extract the details of the orchestrator instance
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            public_ip = instance.get('PublicIpAddress')
            if public_ip:
                # Return the Public IP address
                return public_ip
    
    print("No running instance found or the instance does not have a public IP address.")
    return None


"""
Retrieves the private IP address of an EC2 instance with the tag Name='manager'.

Returns:
- str: The private IP address of the instance if found, otherwise None.
"""
def get_manager_private_ip():
    # Initialize the Boto3 session and EC2 client
    session = boto3.Session(region_name='us-east-1')
    ec2_client = session.client('ec2')

    # Filter instances by tag Name='db_manager'
    try:
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': ['db_manager']},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        # Extract the private IP from the response
        reservations = response.get('Reservations')
        if reservations:
            private_ip = reservations[0]['Instances'][0].get('PrivateIpAddress')
            return private_ip
        else:
            print("No running instance found with Name='manager'")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None    


def fetch_master_status(db_manager_ip, mysql_user, mysql_password, output_file="master_status.json"):
    """
    Connects to the db_manager instance over SSH, retrieves the output of SHOW MASTER STATUS,
    and saves the 'File' and 'Position' values to a JSON file.
    
    Parameters:
    - db_manager_ip (str): IP address of the db_manager instance.
    - db_manager_user (str): SSH username for the db_manager instance.
    - mysql_user (str): MySQL username with permission to run SHOW MASTER STATUS.
    - mysql_password (str): MySQL password for the specified user.
    - output_file (str): Filename for the output JSON file (default: "master_status.json").
    """
    
    # SSH command to get the master status
    mysql_command = f"mysql -u {mysql_user} -p{mysql_password} -e 'SHOW MASTER STATUS\\G'"
    
    # Initialize SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the db_manager instance
        ssh.connect(db_manager_ip, username="ubuntu")

        # Execute the MySQL command
        stdin, stdout, stderr = ssh.exec_command(mysql_command)
        output = stdout.read().decode('utf-8')

        # Parse the output to find the File and Position values
        file_value = None
        position_value = None
        for line in output.splitlines():
            if line.strip().startswith("File:"):
                file_value = line.split(":", 1)[1].strip()
            elif line.strip().startswith("Position:"):
                position_value = line.split(":", 1)[1].strip()

        # Check if both values were found
        if file_value is None or position_value is None:
            print("Error: Could not retrieve File and Position values from the master status output.")
            return None
        else:
            # Prepare JSON data
            master_status = {
                "File": file_value,
                "Position": position_value
            }

            # Write to a JSON file
            with open(output_file, 'w') as f:
                json.dump(master_status, f, indent=4)
            
            print(f"Master status saved to {output_file}")
            return master_status

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        # Close the SSH connection
        ssh.close()


def parse_master_status(input_file, output_file="MASTER_CONFIG.json"):
    """
    Parses the File and Position from the MySQL SHOW MASTER STATUS output file
    and saves them in a JSON file.

    :param input_file: Path to the input text file with the SHOW MASTER STATUS output.
    :param output_file: Path to the JSON file to save the parsed data (default: "MASTER_CONFIG.json").
    """
    file_value = None
    position_value = None

    # Read and parse the input file
    with open(input_file, 'r') as f:
        for line in f:
            # Check for the "File" and "Position" lines and extract values
            if line.strip().startswith("File:"):
                file_value = line.split(":", 1)[1].strip()
            elif line.strip().startswith("Position:"):
                position_value = line.split(":", 1)[1].strip()

    # Ensure both values were found
    if file_value is None or position_value is None:
        print("Error: Could not find File and Position values in the input file.")
        return

    # Create the dictionary to save as JSON
    master_config = {
        "File": file_value,
        "Position": position_value
    }

    # Save the extracted values to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(master_config, json_file, indent=4)
    
    print(f"Parsed data saved to {output_file}")


def load_config(file_path):
    """
    Loads configuration from a JSON file.

    :param file_path: Path to the JSON config file.
    :return: Dictionary containing configuration data.
    """
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config