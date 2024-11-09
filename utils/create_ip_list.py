import boto3
import json

def fetch_and_save_instance_ips(output_file="instance_ips.json", region='us-east-1'):
    # Initialize a session using Amazon EC2
    ec2 = boto3.client('ec2', region_name=region)
    
    # Function to get instance IPs based on Name tags
    def get_instance_ips(name, get_public_ip=False):
        response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': [name]},  # Filter by Name tag
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )
        instances = response['Reservations']
        if not instances:
            print(f"No running instances found with Name='{name}'")
            return None

        # Extract IPs
        private_ip = instances[0]['Instances'][0].get('PrivateIpAddress')
        public_ip = instances[0]['Instances'][0].get('PublicIpAddress') if get_public_ip else None

        return {
            'private_ip': private_ip,
            'public_ip': public_ip
        }

    # Fetch IPs for each instance by Name
    gateway_ips = get_instance_ips('gatekeeper', get_public_ip=True)
    trusted_host_ips = get_instance_ips('trusted-host')
    proxy_ips = get_instance_ips('proxy')
    db_manager_ips = get_instance_ips('db_manager')
    db_worker1_ips = get_instance_ips('db_worker1')  # Assuming distinct names for each worker
    db_worker2_ips = get_instance_ips('db_worker2')

    # Check that each required IP is available; if not, assign a default value or handle the error
    instance_ips = {
        "Gateway": {
            "public_ip": gateway_ips['public_ip'] if gateway_ips else None,
            "private_ip": gateway_ips['private_ip'] if gateway_ips else None
        },
        "Trusted_host": {
            "private_ip": trusted_host_ips['private_ip'] if trusted_host_ips else None
        },
        "Proxy": {
            "private_ip": proxy_ips['private_ip'] if proxy_ips else None
        },
        "db_manager": {
            "private_ip": db_manager_ips['private_ip'] if db_manager_ips else None
        },
        "db_worker1": {
            "private_ip": db_worker1_ips['private_ip'] if db_worker1_ips else None
        },
        "db_worker2": {
            "private_ip": db_worker2_ips['private_ip'] if db_worker2_ips else None
        }
    }

    # Save the data to a JSON file
    with open(output_file, 'w') as f:
        json.dump(instance_ips, f, indent=4)

    print(f"Instance IPs have been saved to {output_file}")
