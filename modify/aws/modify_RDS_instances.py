import boto3

# get user input for AWS credentials and region
access_key = input("Enter AWS access key ID: ")
secret_key = input("Enter AWS secret access key: ")
region = input("Enter AWS region name: ")
kms_key_id = input("Enter KMS key id: ")

# create session and RDS client
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region
)
rds = session.client('rds')

# get all RDS snapshots
response = rds.describe_db_snapshots()

# iterate through snapshots
for snapshot in response['DBSnapshots']:
    # check if snapshot is not encrypted
    if not snapshot['Encrypted']:
        # copy snapshot with encryption
        copy_response = rds.copy_db_snapshot(
            SourceDBSnapshotIdentifier=snapshot['DBSnapshotArn'],
            TargetDBSnapshotIdentifier=f"{snapshot['DBSnapshotIdentifier']}-encrypted",
            KmsKeyId=kms_key_id,
            CopyTags=True
        )
        # wait for copy to complete
        waiter = rds.get_waiter('db_snapshot_completed')
        waiter.wait(
            DBSnapshotIdentifier=copy_response['DBSnapshot']['DBSnapshotIdentifier']
        )
        # delete unencrypted snapshot

        # enter check before deletion
        # 1. can you get the ID for copy (will it be available immediately?)
        # 2. proceed = input(f"Reset bucket: {bucket_name}? (y/n): ").lower().strip() == 'y'
        rds.delete_db_snapshot(
            DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier']
        )


## this file wasn't need - but rough script for RDS instances ##