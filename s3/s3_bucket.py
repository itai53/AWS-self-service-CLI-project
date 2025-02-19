import json
import os
import boto3

s3_client = boto3.client("s3")

def create_s3(bucket_name, access):
    try:
        # Create the bucket (us-east-1 by default)
        s3_client.create_bucket(Bucket=bucket_name)
        if access == "public":
            # Request confirmation for public buckets
            confirmation = input("Public access selected. Are you sure? (y/n): ")
            if confirmation.lower() != "y":
                print("Bucket creation aborted.")
                return
            # Disable block public access settings to allow a public bucket policy.
            s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            # Configure the bucket policy for public read access.
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            s3_client.put_bucket_policy(Bucket=bucket_name,
                                        Policy=json.dumps(bucket_policy))
        # Tag the bucket as CLI-managed along with its access type and name.
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={
                'TagSet': [
                    {'Key': 'cli-managed', 'Value': 'true'},
                    {'Key': 'access', 'Value': access},
                    {'Key': 'Name', 'Value': bucket_name},
                ]
            }
        )
        print(f"S3 bucket '{bucket_name}' created with {access} access.")
    except Exception as e:
        print(f"Error creating S3 bucket: {e}")

def list_s3():
    try:
        response = s3_client.list_buckets()
    except Exception as e:
        print(f"Error listing buckets: {e}")
        return

    cli_buckets = []
    for bucket in response.get("Buckets", []):
        bucket_name = bucket["Name"]
        try:
            tag_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
            tags = {tag["Key"]: tag["Value"] for tag in tag_response.get("TagSet", [])}
            if tags.get("cli-managed") == "true":
                access = tags.get("access", "private")
                cli_buckets.append((bucket_name, access))
        except s3_client.exceptions.ClientError:
            # Skip buckets without tagging or if an error occurs.
            continue

    if not cli_buckets:
        print("No CLI-managed S3 buckets found.")
    else:
        print("CLI-managed S3 buckets:")
        for bucket_name, access in cli_buckets:
            print(f" - Bucket Name: {bucket_name}.\n- Access: {access}.")

def upload_to_s3(bucket_name, file_path):
    try:
        tag_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        tags = {tag["Key"]: tag["Value"] for tag in tag_response.get("TagSet", [])}
        if tags.get("cli-managed") != "true":
            print(f"Error: Bucket '{bucket_name}' is not CLI-managed.")
            return
    except s3_client.exceptions.ClientError:
        print(f"Error: Bucket '{bucket_name}' does not have CLI-managed tagging.")
        return

    try:
        file_name = os.path.basename(file_path)
        s3_client.upload_file(file_path, bucket_name, file_name)
        print(f"File '{file_name}' uploaded to '{bucket_name}'.")
    except Exception as e:
        print(f"Error uploading file: {e}")

def delete_s3(bucket_name):
    try:
        # Check if the bucket is tagged as CLI-managed.
        tag_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        tags = {tag["Key"]: tag["Value"] for tag in tag_response.get("TagSet", [])}
        if tags.get("cli-managed") != "true":
            print(f"Error: Bucket '{bucket_name}' is not CLI-managed.")
            return
    except s3_client.exceptions.ClientError:
        print(f"Error: Could not retrieve tags for bucket '{bucket_name}'.")
        return

    confirmation = input(
        f"Are you sure you want to delete bucket '{bucket_name}' and all its contents? (y/n): ")
    if confirmation.lower() != 'y':
        print("Bucket deletion aborted.")
        return

    # Empty the bucket by deleting all objects inside.
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name):
            if 'Contents' in page:
                delete_keys = {'Objects': [{'Key': obj['Key']} for obj in page['Contents']]}
                s3_client.delete_objects(Bucket=bucket_name, Delete=delete_keys)
        print(f"Bucket '{bucket_name}' has been emptied.")
    except Exception as e:
        print(f"Error emptying bucket: {e}")
        return
    # Now delete the bucket.
    try:
        s3_client.delete_bucket(Bucket=bucket_name)
        print(f"S3 bucket '{bucket_name}' has been deleted.")
    except Exception as e:
        print(f"Error deleting S3 bucket: {e}")
