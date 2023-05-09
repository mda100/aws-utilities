import boto3
import logging
import json 

with open('config.json') as f:
    config = json.load(f)

SECRETS = config.get("SECRETS")
LOGS = config.get("LOGS")
REGIONS = config.get("REGIONS")

with open(SECRETS) as f:
  aws_access_key_id, aws_secret_access_key = f.readline().strip().split(',')

logging.basicConfig(filename=LOGS, level=logging.INFO)

session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

logging.basicConfig(filename=LOGS, level=logging.INFO)

policy_arn = 'arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
instance_role_arn = 'arn:aws:iam::693656978031:instance-profile/SSMManagedEC2Instance'

iam_client = boto3.client('iam')


def ec2_loop(ec2_client: any) -> None:
  instances = ec2_client.describe_instances()
  for reservation in instances['Reservations']:
      for instance in reservation['Instances']:
          instance_id = instance['InstanceId']
          instance_state = instance['State']['Name']
          logging.info(f'Processing instance {instance_id} with state {instance_state}')
          if instance_state != 'terminated':
              instance_profile = instance.get('IamInstanceProfile', None)
              if instance_profile:
                  instance_profile_arn = instance_profile['Arn']
                  instance_role_name = instance_profile_arn.split('/')[-1]
                  instance_policy_arns = [
                      p['PolicyArn'] for p in iam_client.list_attached_role_policies(RoleName=instance_role_name)['AttachedPolicies']
                  ]
                  if policy_arn not in instance_policy_arns:
                      iam_client.attach_role_policy(RoleName=instance_role_name, PolicyArn=policy_arn)
                      logging.info(f'Attached policy {policy_arn} to role {instance_role_name}')
                  else:
                      logging.info(f'Role {instance_role_name} already has policy {policy_arn}')
              else:
                  ec2_client.associate_iam_instance_profile(
                      IamInstanceProfile={
                          'Arn': instance_role_arn
                      },
                      InstanceId=instance_id
                  )
                  logging.info(f'Associated role {instance_role_arn} with instance {instance_id}')

def ec2_loop_iter () -> None:
    for region in REGIONS:
        print(f"running loop in region: {region}")
        ec2_client = boto3.client('ec2', region_name=region)
        ec2_loop(ec2_client=ec2_client)

ec2_loop_iter()
print('Done')
