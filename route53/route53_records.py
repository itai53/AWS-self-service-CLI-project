import boto3

def create_route53_record(zone_id, record_name, record_type, record_value, ttl=300):
    client = boto3.client('route53')
    response = client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            "Changes": [{
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": record_name,
                    "Type": record_type,
                    "TTL": ttl,  # Set default TTL to 300
                    "ResourceRecords": [{"Value": record_value}]
                }
            }]
        }
    )
    change_info = response.get("ChangeInfo", {})
    change_id = change_info.get("Id")
    status = change_info.get("Status")
    print(f"Record {record_name} ({record_type}) created in zone {zone_id}")
    print(f"Change ID: {change_id}, Status: {status}")

def list_dns_records(zone_id):
    client = boto3.client('route53')
    try:
        response = client.list_resource_record_sets(HostedZoneId=zone_id)
        records = response.get('ResourceRecordSets', [])

        if not records:
            print(f"No DNS records found in zone {zone_id}.")
            return

        print(f"DNS records in zone {zone_id}:")
        for record in records:
            name = record.get('Name')
            record_type = record.get('Type')
            ttl = record.get('TTL', 'N/A')
            values = ', '.join([r.get('Value') for r in
                                record.get('ResourceRecords', [])])
            print(f" -NAME: {name} -TYPE: {record_type}: TTL={ttl}, Value(s): {values}")
    except Exception as e:
        print(f"Error listing DNS records for hosted zone {zone_id}: {e}")

def update_route53_record(zone_id, record_name, record_type, record_value, ttl=300):
    client = boto3.client('route53')

    # Fetch existing records in the hosted zone
    response = client.list_resource_record_sets(HostedZoneId=zone_id)
    records = response.get("ResourceRecordSets", [])

    # Normalize the record name for comparison (remove trailing dot)
    normalized_target = record_name.rstrip(".")

    target_record = None
    for record in records:
        # Normalize the existing record name
        existing_name = record.get("Name", "").rstrip(".")
        if existing_name == normalized_target and record.get("Type") == record_type:
            target_record = record
            break

    if not target_record:
        print(f"Error: Record {record_name} of type {record_type} does not exist in zone {zone_id}.")
        return

    # Perform update using UPSERT (update the record with new value/TTL)
    response = client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            "Changes": [{
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": record_name,
                    "Type": record_type,
                    "TTL": ttl,
                    "ResourceRecords": [{"Value": record_value}]
                }
            }]
        }
    )
    change_info = response.get("ChangeInfo", {})
    change_id = change_info.get("Id")
    status = change_info.get("Status")

    print(f"Record {record_name} ({record_type}) updated in zone {zone_id}")
    print(f"Change ID: {change_id}, Status: {status}")

def delete_route53_record(zone_id, record_name):
    client = boto3.client('route53')

    # Fetch existing records in the hosted zone
    response = client.list_resource_record_sets(HostedZoneId=zone_id)
    records = response.get('ResourceRecordSets', [])

    # Find the record to delete
    for record in records:
        if record['Name'] == f"{record_name}":
            record_type = record['Type']
            record_value = record['ResourceRecords'][0]['Value']

            # Proceed with deletion
            del_response = client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch={
                    "Changes": [{
                        "Action": "DELETE",
                        "ResourceRecordSet": {
                            "Name": record_name,
                            "Type": record_type,
                            "TTL": record['TTL'],
                            "ResourceRecords": [{"Value": record_value}]
                        }
                    }]
                }
            )
            print(f"Record {record_name} ({record_type}) deleted from zone {zone_id}")
            return
    print(f"Error: Record {record_name} not found in zone {zone_id}")