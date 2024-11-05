
import time
import os
import globals as g
import boto3
import stat

from utils import instance_setup as i
from utils import transfer_json_file as tj
from utils import util_functions as u


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

    # Create the required security groups
    gatekeeper_security_id = i.createPublicSecurityGroup(vpc_id, g.public_security_group_name)
    private_security_id = i.createInternalSecurityGroup(vpc_id, g.internal_security_group_name, gatekeeper_security_id)

    with open('userdata_scripts/blank_data.sh', 'r') as file:
        blank_userdata = file.read()


    # Create instances with the correct security groups and configurations

    # MySQL Manager Instance (internal)
    # ANVÄNDER PUBLIC SECURITY GROUP I BÖRJAN
    i.createInternalInstance('t2.large', 1, 1, key_pair, gatekeeper_security_id, subnet_id, blank_userdata, 'manager')

    # 2x MySQL Worker Instances (internal)
    # ANVÄNDER PUBLIC SECURITY GROUP I BÖRJAN
    i.createInternalInstance('t2.micro', 2, 2, key_pair, gatekeeper_security_id, subnet_id, blank_userdata, 'worker-instance')

    # Proxy Instance (internal)
    # i.createInstance('t2.large', 1, 1, key_pair, private_security_id, subnet_id, blank_userdata, 'proxy')

    # Gatekeeper Instance (public)
    # i.createInstance('t2.large', 1, 1, key_pair, gatekeeper_security_id, subnet_id, blank_userdata, 'gatekeeper')

    # Trusted Host Instance (internal)
    # i.createInternalInstance('t2.large', 1, 1, key_pair, private_security_id, subnet_id, blank_userdata, 'trusted-host')


    # time.sleep(240)

    