import boto3
import logging

# Configure logging
logging.basicConfig(filename='aws_encryption.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Get AWS credentials
aws_access_key_id = input("Enter your AWS access key ID: ")
aws_secret_access_key = input("Enter your AWS secret access key: ")
aws_region = input("Enter the AWS region: ")

# Connect to AWS
ec2 = boto3.client('ec2', region_name=aws_region,
                   aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Search for volumes and check encryption status
volumes = ec2.describe_volumes()
for vol in volumes['Volumes']:
    vol_id = vol['VolumeId']
    vol_encrypted = vol['Encrypted']
    if not vol_encrypted:
        logging.info(f"Volume {vol_id} is not encrypted.")
        # Create snapshot
        snapshot = ec2.create_snapshot(VolumeId=vol_id, Description='Snapshot of unencrypted volume')
        snapshot_id = snapshot['SnapshotId']
        logging.info(f"Snapshot {snapshot_id} created for volume {vol_id}.")
        # Copy and encrypt snapshot
        copy_snapshot = ec2.copy_snapshot(SourceSnapshotId=snapshot_id, Description='Encrypted copy of unencrypted snapshot', Encrypted=True, KmsKeyId='<your KMS key ID>')
        copy_snapshot_id = copy_snapshot['SnapshotId']
        logging.info(f"Encrypted snapshot {copy_snapshot_id} created from snapshot {snapshot_id}.")
        # Create encrypted volume from encrypted snapshot
        encrypted_vol = ec2.create_volume(SnapshotId=copy_snapshot_id, VolumeType='gp2', Encrypted=True, AvailabilityZone=vol['AvailabilityZone'])
        encrypted_vol_id = encrypted_vol['VolumeId']
        logging.info(f"Encrypted volume {encrypted_vol_id} created from snapshot {copy_snapshot_id}.")
        # Detach unencrypted volume
        ec2.detach_volume(VolumeId=vol_id)
        logging.info(f"Volume {vol_id} detached.")
        # Attach encrypted volume
        ec2.attach_volume(VolumeId=encrypted_vol_id, InstanceId='<your EC2 instance ID>', Device='/dev/sdf')
        logging.info(f"Encrypted volume {encrypted_vol_id} attached to instance.")
    else:
        logging.info(f"Volume {vol_id} is already encrypted.")

## unused script for EBS encryption ##