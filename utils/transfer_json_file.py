from utils import util_functions as u

def transfer_json_file(pem_file_path):
    orchestrator_instance_id = u.get_orchestrator_instance_id()
    if orchestrator_instance_id:
        print(f"Orchestrator instance ID: {orchestrator_instance_id}")

    u.transfer_file_to_ec2(orchestrator_instance_id, "resources/test.json" , "/home/ubuntu/test.json", pem_file_path)


def transfer_json_file_to_all(pem_file_path, json_file_path):
    # List of instance names to transfer the file to
    instance_names = ["orchestrator", "db_manager", "db_worker1", "db_worker2", "proxy", "gatekeeper", "trusted-host"]

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

