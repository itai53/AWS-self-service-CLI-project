import argparse
from ec2 import ec2_instance as ec2_module
from s3 import s3_bucket as s3_module
from route53.route53_zones import list_route53_zones, delete_hosted_zone
from route53 import route53_records as record_module
from route53 import route53_zones as zone_module
from route53.route53_records import list_dns_records

def main():
    parser = argparse.ArgumentParser(description="CLI for provisioning AWS resources via Boto3", usage=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="resource", required=True)

    # --------------------------
    # EC2 Commands
    # --------------------------
    ec2_parser = subparsers.add_parser("ec2", help="Manage EC2 instances")
    ec2_subparsers = ec2_parser.add_subparsers(dest="action", required=True)

    create_ec2_parser = ec2_subparsers.add_parser("create", help="Create an EC2 instance")
    create_ec2_parser.add_argument("--name", "--N", required=True, help="Enter name of the EC2 instance")
    create_ec2_parser.add_argument("--instance-type", "--T", required=True, choices=["t3.nano", "t4g.nano"], help="Enter EC2 instance type")
    create_ec2_parser.add_argument("--ami", required=True, choices=["ubuntu", "amazon-linux"], help="AMI type to use")
    create_ec2_parser.add_argument("--pubkey-path", "--K", required=False, help="Enter Path to the SSH public key")

    ec2_subparsers.add_parser("list", help="List EC2 instances managed via CLI")

    stop_ec2_parser = ec2_subparsers.add_parser("stop", help="Stop an EC2 instance")
    stop_ec2_parser.add_argument("--instance-id", "--ID", help="Enter EC2 Instance ID to stop")
    stop_ec2_parser.add_argument("--name", "--N", help="Enter EC2 Instance name to stop")

    start_ec2_parser = ec2_subparsers.add_parser("start", help="Start an EC2 instance")
    start_ec2_parser.add_argument("--instance-id", "--ID", help="Enter EC2 Instance ID to start")
    start_ec2_parser.add_argument("--name", "--N", help="Enter EC2 Instance name to start")

    delete_ec2_parser = ec2_subparsers.add_parser("delete", help="Delete an EC2 instance")
    delete_ec2_parser.add_argument("--instance-id", "--ID", help="Enter EC2 Instance ID to delete")
    delete_ec2_parser.add_argument("--name", "--N", help="Enter EC2 Instance name to delete")

    # --------------------------
    # S3 Commands
    # --------------------------
    s3_parser = subparsers.add_parser("s3", help="Manage S3 buckets")
    s3_subparsers = s3_parser.add_subparsers(dest="action", required=True)

    create_s3_parser = s3_subparsers.add_parser("create", help="Create an S3 bucket")
    create_s3_parser.add_argument("--bucket-name", "--N", required=True, help="Name of the S3 bucket")
    create_s3_parser.add_argument("--access", required=True, choices=["private", "public"], help="Bucket access type")

    s3_subparsers.add_parser("list", help="List S3 buckets managed via CLI")

    upload_s3_parser = s3_subparsers.add_parser("upload", help="Upload a file to an S3 bucket")
    upload_s3_parser.add_argument("--bucket-name", "--N", required=True, help="Target S3 bucket name")
    upload_s3_parser.add_argument("--file", "--F", required=True, help="File path to upload")

    delete_s3_parser = s3_subparsers.add_parser("delete", help="Delete an S3 bucket")
    delete_s3_parser.add_argument("--bucket-name", "--N", required=True, help="Target S3 bucket name")

    # --------------------------
    # Route53 Commands
    # --------------------------
    route53_parser = subparsers.add_parser("route53", help="Manage Route53 resources")
    route53_subparsers = route53_parser.add_subparsers(dest="action", required=True)

    create_zone_parser = route53_subparsers.add_parser("create-zone", help="Create a Route53 hosted zone")
    create_zone_parser.add_argument("--zone-name", "--N", required=True, help="Domain name for the hosted zone")

    create_record_parser = route53_subparsers.add_parser("create-record", help="Create a DNS record in a hosted zone")
    create_record_parser.add_argument("--zone-id", "--ID", required=True, help="Hosted Zone ID")
    create_record_parser.add_argument("--record-name", "--N", required=True, help="DNS record name")
    create_record_parser.add_argument("--record-type", "--T", required=True, help="Record type (e.g., A, CNAME)")
    create_record_parser.add_argument("--record-value", "--V", required=True, help="Record value (e.g., IP address)")

    delete_record_parser = route53_subparsers.add_parser("delete-record", help="Delete a DNS record in a hosted zone")
    delete_record_parser.add_argument("--zone-id", "--ID", required=True, help="Hosted Zone ID")
    delete_record_parser.add_argument("--record-name", "--N", required=True, help="DNS record name")

    route53_subparsers.add_parser("list-zones", help="List Route53 zones managed via CLI")
    list_records_parser = route53_subparsers.add_parser("list-records", help="List DNS records in a hosted zone")
    list_records_parser.add_argument("--zone-id", "--ID", required=True, help="Hosted Zone ID")

    delete_zone_parser = route53_subparsers.add_parser("delete-zone", help="Delete a hosted zone")
    delete_zone_parser.add_argument("--zone-id", "--ID", required=True, help="Hosted Zone ID")

    # --------------------------
    # Parse and Dispatch
    # --------------------------
    args = parser.parse_args()

    if args.resource == "ec2":
        if args.action == "create":
            ec2_module.create_ec2(args.name, args.instance_type, args.ami,args.pubkey_path)
        elif args.action == "list":
            ec2_module.list_ec2()
        elif args.action == "start":
            ec2_module.start_ec2(args.name, args.instance_type)
        elif args.action == "stop":
            ec2_module.stop_ec2(args.instance_id,args.name)
        elif args.action == "delete":
            ec2_module.delete_ec2(args.instance_id, args.name)

    elif args.resource == "s3":
        if args.action == "create":
            s3_module.create_s3(args.bucket_name, args.access)
        elif args.action == "list":
            s3_module.list_s3()
        elif args.action == "upload":
            s3_module.upload_to_s3(args.bucket_name, args.file)
        elif args.action == "delete":
            s3_module.delete_s3(args.bucket_name)

    elif args.resource == "route53":
        if args.action == "create-zone":
            zone_module.create_route53_zone(args.zone_name)
        elif args.action == "list-zones":
            list_route53_zones()
        elif args.action == "delete-zone":
            delete_hosted_zone(args.zone_id)
        elif args.action == "create-record":
            record_module.create_route53_record(
                    args.zone_id, args.record_name, args.record_type,
                    args.record_value
            )
        elif args.action == "list-records":
            list_dns_records(args.zone_id)
        elif args.action == "delete-record":
            record_module.delete_route53_record(args.zone_id, args.record_name)
        elif args.action == "update-record":
            record_module.update_route53_record(
                args.zone_id, args.record_name, args.record_type,
                args.record_value
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
