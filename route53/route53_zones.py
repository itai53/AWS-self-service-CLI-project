import boto3

def create_route53_zone(zone_name):
    client = boto3.client('route53')
    response = client.create_hosted_zone(
            Name=zone_name,
            CallerReference=str(hash(zone_name)),
            HostedZoneConfig={"Comment": "CLI-managed zone",
                              "PrivateZone": False},
    )
    # Extract the zone ID and add tags
    zone_id = response['HostedZone']['Id'].split('/')[-1]
    client.change_tags_for_resource(
            ResourceType='hostedzone',
            ResourceId=zone_id,
            AddTags=[{"Key": "cli-managed", "Value": "true"}]
    )
    print("Host name Created:")
    print(
        f"Hosted zone {zone_name} created with ID {response['HostedZone']['Id']}")

def list_route53_zones():
    client = boto3.client('route53')
    zones = client.list_hosted_zones()['HostedZones']
    cli_managed_zones = [z for z in zones if any(
            tag['Key'] == 'cli-managed' and tag['Value'] == 'true' for tag in
            client.list_tags_for_resource(
                    ResourceType='hostedzone',
                    ResourceId=z['Id'].split('/')[-1])['ResourceTagSet'][
                'Tags'])]
    print("Host zones:")
    for zone in cli_managed_zones:
        print(f"-Zone ID: {zone['Id']} - Host Name: {zone['Name']}")

def delete_hosted_zone(zone_id):
    client = boto3.client('route53')
    # Check if the hosted zone is managed by the CLI
    try:
        tags_response = client.list_tags_for_resource(
                ResourceType='hostedzone',
                ResourceId=zone_id
        )
        tags = tags_response.get('ResourceTagSet', {}).get('Tags', [])
        cli_managed = any(
                tag.get('Key') == 'cli-managed' and tag.get('Value') == 'true'
                for tag in tags)

    except Exception as e:
        print(f"Error retrieving tags for hosted zone {zone_id}: {e}")
        return

    if not cli_managed:
        print(
            f"Error: Hosted zone {zone_id} is not managed by this CLI. Deletion aborted.")
        return

    # Confirm deletion with the user
    confirmation = input(
        f"Are you sure you want to delete hosted zone {zone_id} ?\nThis will delete all records permanently. (y/n):")
    if confirmation.lower() != "y":
        print("Deletion cancelled.")
        return
    # List all records in the zone
    try:
        response = client.list_resource_record_sets(HostedZoneId=zone_id)
        records = response.get('ResourceRecordSets', [])
    except Exception as e:
        print(f"Error listing records for hosted zone {zone_id}: {e}")
        return

    # Filter out the default NS and SOA records which AWS requires to remain
    records_to_delete = [record for record in records if
                         record.get('Type') not in ['NS', 'SOA']]

    # Delete each non-default record
    for record in records_to_delete:
        try:
            print(
                f"Deleting record {record.get('Name')} ({record.get('Type')})...")
            client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch={
                        "Changes": [{
                            "Action": "DELETE",
                            "ResourceRecordSet": record
                        }]
                    }
            )
        except Exception as e:
            print(
                f"Error deleting record {record.get('Name')} ({record.get('Type')}): {e}")

    # Now, delete the hosted zone itself
    try:
        client.delete_hosted_zone(Id=zone_id)
        print(f"Hosted zone {zone_id} deleted successfully.")
    except Exception as e:
        print(f"Error deleting hosted zone {zone_id}: {e}")

