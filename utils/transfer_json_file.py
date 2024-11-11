from utils import util_functions as u

def transfer_json_file(pem_file_path):
    orchestrator_instance_id = u.get_orchestrator_instance_id()
    if orchestrator_instance_id:
        print(f"Orchestrator instance ID: {orchestrator_instance_id}")

    u.transfer_file_to_ec2(orchestrator_instance_id, "resources/test.json" , "/home/ubuntu/test.json", pem_file_path)


def transfer_json_file_to_all(pem_file_path, json_file_path):
    # List of instance names to transfer the file to
    instance_names = ["db_manager", "db_worker1", "db_worker2", "proxy", "gatekeeper", "trusted-host"]

    # Target path on the EC2 instances (assuming it’s always the same)
    target_path = "/home/ubuntu/instance_ips.json"

    # Loop through each instance name, retrieve its instance ID, and transfer the file
    for name in instance_names:
        instance_id = u.get_instance_id_by_name(name)
        
        if instance_id:
            print(f"Instance ID for {name}: {instance_id}")
            # Use json_file_path as the source file path
            u.transfer_file_to_ec2(instance_id, json_file_path, target_path, pem_file_path)
        else:
            print(f"No running instance found with name: {name}")

def transfer_file_to_instance(pem_file_path, source_file_path, target_file_name, instance_name):
    """
    Transfers a file to a specified EC2 instance by name.
    
    :param pem_file_path: Path to the PEM file for SSH authentication
    :param source_file_path: Local path of the file to transfer
    :param target_file_name: Target filename on the instance
    :param instance_name: The name of the EC2 instance to transfer the file to
    """
    # Get the instance ID based on the provided instance name
    instance_id = u.get_instance_id_by_name(instance_name)
    
    # Define the target path on the instance
    target_path = f"/home/ubuntu/{target_file_name}"

    if instance_id:
        print(f"Transferring file to instance '{instance_name}' (Instance ID: {instance_id})")
        # Use source_file_path as the source file path
        u.transfer_file_to_ec2(instance_id, source_file_path, target_path, pem_file_path)
        print(f"File transferred successfully to {instance_name}")
    else:
        print(f"No running instance found with name: {instance_name}")
