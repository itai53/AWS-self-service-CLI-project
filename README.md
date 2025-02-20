# AWS DevOps Self-Service CLI project 🚀

## Overview 📄

This project is a Python-based CLI tool for developers to create, update, and manage AWS resources.

This CLI tool streamlines AWS resource management by allowing developers to:

- Provision EC2 instances with specific instance types and AMIs.
- Manage S3 buckets with control over access policies and file uploads.
- Create and manage DNS zones and records via Route53.

## Prerequisites ⚙️

### Python 3.6+

Ensure you have Python installed on your system.

### AWS CLI

Ensure AWS CLI Is Installed 
check the link on -  

[How to install AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

Configure your AWS credentials by running:

```sh
aws configure
```

### Boto3

Installed automatically via `pip install` (see below).

## Installation 📦

### Clone the Repository

First, clone the repository and navigate to the project directory:

```sh
git clone <repository-url>
cd <project-directory>
```

### Install Packages

Install the package locally:

```sh
pip install .
```

This command registers the `awscli` command which you'll use to interact with the terminal.

## Configuration 🛠️

Before using the CLI, ensure you set up your security-group and subnet id in the file below:

```
ec2/configuration.txt
```

Example content:

```sh
security-group:sg-<your_sg_id>
subnet-id:subne-<your_subnet_id>
```

This configuration file ensures the correct security group and subnet are used when launching EC2 instances.

### SSH Keys (optional) 🔑

To connect to EC2 instances via SSH, generate an SSH key pair in PEM format:

```sh
ssh-keygen -t rsa -b 4096 -m PEM -f mykey.pem
```

This will generate `mykey.pem` (private key) and `mykey.pem.pub` (public key).

## Usage 💻

Invoke the CLI with the `awscli` command followed by a resource type, an action, and any required options.

### General Syntax

```sh
awscli <resource> <action> [options]
```

## Help Command 🆘

The `-h` or `--help` flag can be used with any resource type to display help information about available commands. Example:

```sh
awscli ec2 -h
```
Example output:
```
usage:  ec2 [-h] {create,list,stop,start,delete} ...

positional arguments:
  {create,list,stop,start,delete}
    create              Create an EC2 instance
    list                List EC2 instances managed via CLI
    stop                Stop an EC2 instance
    start               Start an EC2 instance
    delete              Delete an EC2 instance

options:
  -h, --help            show this help message and exit
```

## Flag Naming Conventions 🚩

Some commands support both full and short versions of flags. For example:

- `--record-type` and `--instance-type` can also be used as `--T`.
- `--instance-id` and `--zone-id` can also be used as `--ID`.
- `--pubkey-path` can also be used as `--K`.
- `--name` can also be used as `--N`.
- `--file` can also be used as `--F`.


## Available Commands ✨

### ☁️ EC2 Commands  

| Command      | Action                                                                      | Example                                                                                      |
|-------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| `ec2 create` | Create a new EC2 instance using `t3.nano` or `t4g.nano` and a selected AMI. | `awscli ec2 create --N my-ec2 --type t3.nano --ami ubuntu --K /path/to/mykey.pem` |
| `ec2 list`   | List all EC2 instances created via the CLI.                                 | `awscli ec2 list`                                                                           |
| `ec2 start`  | Start a stopped EC2 instance.                                              | `awscli ec2 start --N my-ec2`                                                               |
| `ec2 stop`   | Stop a running EC2 instance.                                               | `awscli ec2 stop --id i-0123456789abcdef`                                                   |
| `ec2 delete` | Delete an EC2 instance.                                                    | `awscli ec2 delete --N my-ec2`                                                              |


### 📂 S3 Commands

| Command     | Action                                                                                           | Example                                                             |
| ----------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| `s3 create` | Create a new S3 bucket with public or private access.                                           | `awscli s3 create --N my-bucket --access public`                   |
| `s3 list`   | List all S3 buckets created via the CLI.                                                         | `awscli s3 list`                                                    |
| `s3 upload` | Upload a file to an S3 bucket.                                                                   | `awscli s3 upload --N my-bucket --F /path/to/file.txt`             |
| `s3 delete` | Delete an S3 bucket.                                                                             | `awscli s3 delete --N my-bucket`                                    |

### 🌐 Route53 Commands

| Command                 | Action                                           | Example                                                                                       |
| ----------------------- |--------------------------------------------------| --------------------------------------------------------------------------------------------- |
| `route53 create-zone`   | Create a new hosted zone (DNS zone).             | `awscli route53 create-zone --N example.com`                                                 |
| `route53 list-zones`    | List all hosted zones created via the CLI.       | `awscli route53 list-zones`                                                                  |
| `route53 delete-zone`   | Delete a hosted zone.                            | `awscli route53 delete-zone --ID Z3XXXXXXXXXXXXXX`                                          |
| `route53 create-record` | Create a new DNS record.                         | `awscli route53 create-record --ID Z3XXXXXXXXXXXXXX --N www.example.com --T A --V 192.0.2.1` |
| `route53 list-records`  | List DNS records in a specified hosted zone.     | `awscli route53 list-records --ID Z3XXXXXXXXXXXXXX`                                         |
| `route53 delete-record` | Delete a DNS record from a hosted zone.          | `awscli route53 delete-record --ID Z3XXXXXXXXXXXXXX --N www.example.com`                    |

## Summary 📚

By following the installation and configuration steps above, you can quickly set up and use the tool to self-provision AWS resources.
- PRs are welcome! Fork, commit, and create a Pull Request.
- 🔥 If this project helps you, give it a ⭐ on GitHub!



**Happy provisioning! 🎉**
