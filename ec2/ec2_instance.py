from datetime import datetime
import os
import boto3

data = {}
with open("ec2/configuration.txt", "r") as file:
    for line in file:
        key, value = line.strip().split(":", 1)
        data[key.strip()] = value.strip()
subnet_id = data.get("subnet-id")
security_group = data.get("security-group")

def get_or_create_key_pair_boto(pubkey_path: str) -> str:
    basename = os.path.basename(pubkey_path)
    # Ensure that we correctly strip ".pub" from the key name
    if basename.endswith(".pem.pub"):
        key_name = basename[:-8]  # Remove ".pem.pub"
    elif basename.endswith(".pub"):
        key_name = basename[:-4]  # Remove ".pub"
    else:
        key_name = basename  # Leave as is
    ec2_client = boto3.client("ec2")
    try:
        ec2_client.describe_key_pairs(KeyNames=[key_name])
        print(f"Key pair '{key_name}' exists.")
    except ec2_client.exceptions.ClientError:
        print(f"Key pair '{key_name}' not found. Importing your public key.")
        with open(pubkey_path, 'r', encoding='utf-8') as f:
            public_key = f.read().strip()
        ec2_client.import_key_pair(KeyName=key_name,
                                   PublicKeyMaterial=public_key)

    return key_name

def delete_ec2(instance_id=None, instance_name=None):
    ec2_client = boto3.client("ec2")
    if not instance_id:
        if instance_name:
            response = ec2_client.describe_instances(
                    Filters=[
                        {"Name": "tag:Name", "Values": [instance_name]},
                        {"Name": "tag:cli-managed", "Values": ["true"]}
                    ]
            )
            instances = [
                instance for reservation in response.get("Reservations", [])
                for instance in reservation.get("Instances", [])
            ]
            if not instances:
                print(f"No instance found with name {instance_name}.")
                return
            instance_id = instances[0]["InstanceId"]
        else:
            print("Error: Must specify either instance_id or instance_name.")
            return

    try:
        ec2_client.terminate_instances(InstanceIds=[instance_id])
        print(f"Terminating instance {instance_id}")
    except Exception as e:
        print(f"Error terminating instance: {e}")

def start_ec2(instance_id=None, instance_name=None):
    ec2_client = boto3.client("ec2")
    if not instance_id:
        if instance_name:
            response = ec2_client.describe_instances(
                    Filters=[
                        {"Name": "tag:Name", "Values": [instance_name]},
                        {"Name": "tag:cli-managed", "Values": ["true"]},
                        {"Name": "instance-state-name", "Values": ["stopped"]}
                    ]
            )
            instances = [
                instance for reservation in response.get("Reservations", [])
                for instance in reservation.get("Instances", [])
            ]
            if not instances:
                print(f"No stopped instance found with name {instance_name}.")
                return
            instance_id = instances[0]["InstanceId"]
        else:
            print("Error: Must specify either instance_id or instance_name.")
            return

    try:
        ec2_client.start_instances(InstanceIds=[instance_id])
        print(f"Starting instance {instance_id}")
    except Exception as e:
        print(f"Error starting instance: {e}")

def create_ec2(cli_name, cli_instance_type, cli_ami, cli_pubkey_path):
    # Ensure the public key file exists before proceeding
    if not os.path.isfile(cli_pubkey_path):
        print(f"Error: Public key file '{cli_pubkey_path}' does not exist.")
        return
    # Get or create the key pair
    final_key_name = get_or_create_key_pair_boto(cli_pubkey_path)

    # Determine the AMI and user data file based on instance type and AMI selection
    if cli_instance_type == "t4g.nano":
        if cli_ami == "ubuntu":
            resolved_ami = "ami-0a7a4e87939439934"  # ARM Ubuntu
            user_data_file = "./ec2/user_data_ubuntu.sh"
        elif cli_ami == "amazon-linux":
            resolved_ami = "ami-0c518311db5640eff"  # ARM Amazon Linux
            user_data_file = "./ec2/user_data_amazon-linux.sh"
        else:
            print("Invalid AMI selection.")
            return
    elif cli_instance_type == "t3.nano":  # Assume t3.nano is x86_64
        if cli_ami == "ubuntu":
            resolved_ami = "ami-04b4f1a9cf54c11d0"  # x86_64 Ubuntu
            user_data_file = "./ec2/user_data_ubuntu.sh"
        elif cli_ami == "amazon-linux":
            resolved_ami = "ami-085ad6ae776d8f09c"  # x86_64 Amazon Linux
            user_data_file = "./ec2/user_data_amazon-linux.sh"
        else:
            print("Invalid AMI selection.")
            return
    else:
        print("Invalid instance type selection.")
        return

    # Read and encode the user data script
    with open(user_data_file, 'r') as f:
        user_data_script = f.read()

    max_instances = 2
    ec2_client = boto3.client("ec2")
    response = ec2_client.describe_instances(
            Filters=[
                {"Name": "tag:cli-managed", "Values": ["true"]},
                {"Name": "instance-state-name", "Values": ["running"]}
            ]
    )
    running_instances = sum(
            1 for reservation in response.get("Reservations", [])
            for _ in reservation.get("Instances", [])
    )
    if running_instances >= max_instances:
        print(
            "Maximum running instances is 2.\n"
            "Cannot create a new instance if current running instances is 2 .")
        return

    # Create the new EC2 instance
    resource_ec2 = boto3.resource("ec2")
    date_created = datetime.now().strftime("%Y-%m-%d")
    instance_name = f"{cli_name}"

    print(f"Creating EC2 instance:")
    try:
        instances = resource_ec2.create_instances(
                ImageId=resolved_ami,
                MinCount=1,
                MaxCount=1,
                InstanceType=cli_instance_type,
                KeyName=final_key_name,
                NetworkInterfaces=[
                    {
                        "AssociatePublicIpAddress": True,
                        "DeviceIndex": 0,
                        "SubnetId": subnet_id,
                        "Groups": [security_group],
                    }
                ],
                TagSpecifications=[
                    {
                        "ResourceType": "instance",
                        "Tags": [
                            {"Key": "Name", "Value": instance_name},
                            {"Key": "creation_date", "Value": date_created},
                            {"Key": "cli-managed", "Value": "true"},
                            {"Key": "owner", "Value": "itaimoshe"},
                        ]
                    }
                ],
                UserData=user_data_script,
        )
    except Exception as e:
        print(f"Error creating instance: {e}")
        return

    # Wait until the instance is running and then display its details
    instance = instances[0]
    instance.wait_until_running()
    instance.reload()
    public_ip = instance.public_ip_address

    print("EC2 Instance Created:")
    print(f"  - Instance ID: {instance.id}")
    print(f"  - Name: {instance_name}")
    print(f"  - Public IP: {public_ip}")

    return instance.id, instance_name, public_ip

def list_ec2():
    ec2_client = boto3.client("ec2")
    try:
        response = ec2_client.describe_instances(
            Filters=[{"Name": "tag:cli-managed", "Values": ["true"]}]
        )
        print("EC2 Instances:")
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                name_tag = tags.get("Name", "Unknown")
                print(
                    f" - Instance ID: {instance['InstanceId']} - Instance Name: {name_tag} - Instance State: {instance['State']['Name']}"
                )
    except ec2_client.exceptions.ClientError as e:
        print("No EC2 instances found", e)
        return

def stop_ec2(instance_id=None, instance_name=None):
    ec2_client = boto3.client("ec2")
    if not instance_id:
        if instance_name:
            response = ec2_client.describe_instances(
                    Filters=[
                        {"Name": "tag:Name", "Values": [instance_name]},
                        {"Name": "tag:cli-managed", "Values": ["true"]},
                        {"Name": "instance-state-name", "Values": ["running"]}
                    ]
            )
            instances = [
                instance for reservation in response.get("Reservations", [])
                for instance in reservation.get("Instances", [])
            ]
            if not instances:
                print(f"No running instance found with name {instance_name}.")
                return
            instance_id = instances[0]["InstanceId"]
        else:
            print("Error: Must specify either instance_id or instance_name.")
            return

    try:
        ec2_client.stop_instances(InstanceIds=[instance_id])
        print(f"Stopping instance {instance_id}")
    except Exception as e:
        print(f"Error stopping instance: {e}")

