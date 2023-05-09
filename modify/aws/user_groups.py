import boto3
import boto3
import logging
import json 

with open('config.json') as f:
    config = json.load(f)
SECRETS = config.get("SECRETS")
with open(SECRETS) as f:
  aws_access_key_id, aws_secret_access_key = f.readline().strip().split(',')
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)
iam = boto3.client('iam')

def get_attached_policies(user):
    attached_policies = []
    response = iam.list_attached_user_policies(UserName=user['UserName'])
    for policy in response.get('AttachedPolicies'):
        attached_policies.append(policy['PolicyArn'])
    return attached_policies

def get_inline_policies(user):
    inline_policies = []
    response = iam.list_user_policies(UserName=user['UserName'])
    for policy_name in response.get('PolicyNames'):
        response = iam.get_user_policy(UserName=user['UserName'], PolicyName=policy_name)
        inline_policies.append(response)
    return inline_policies

def create_group_and_attach_policies(user, attached_policies, inline_policies):
    group_name = user['UserName'] + '-group'
    response = iam.create_group(GroupName=group_name)
    print(f"Creating group {group_name}")
    for policy in attached_policies:
        response = iam.attach_group_policy(GroupName=group_name, PolicyArn=policy)
        print(f"Attaching policy {policy} to group {group_name}")
    for policy in inline_policies:
        response = iam.put_group_policy(GroupName=group_name, PolicyName=policy.split(':')[-1], PolicyDocument=iam.get_user_policy(UserName=user['UserName'], PolicyName=policy.split(':')[-1])['PolicyDocument'])
        print(f"Attaching inline policy {policy} to group {group_name}")
    return group_name

def add_user_to_group(user, group_name):
    response = iam.add_user_to_group(UserName=user['UserName'], GroupName=group_name)
    print(f"Adding user {user['UserName']} to group {group_name}")

def remove_directly_attached_policies(user, attached_policies):
    for policy in attached_policies:
        response = iam.detach_user_policy(UserName=user['UserName'], PolicyArn=policy)
        print(f"Detaching policy {policy} from user {user['UserName']}")

def remove_inline_policies(user, inline_policies):
    for policy in inline_policies:
        response = iam.delete_user_policy(UserName=user['UserName'], PolicyName=policy.split(':')[-1])
        print(f"Removing inline policy {policy} from user {user['UserName']}")

def process_user(user, dry_run=False):
    attached_policies = get_attached_policies(user)
    inline_policies = get_inline_policies(user)

    if attached_policies or inline_policies:
        if dry_run:
            print(f"Processing user {user['UserName']}...")
            print(f"Attached Policies: {attached_policies}")
            print(f"Inline Policies: {inline_policies}")
        else:
            group_name = create_group_and_attach_policies(user, attached_policies, inline_policies)
            add_user_to_group(user, group_name)
            remove_directly_attached_policies(user, attached_policies)
            remove_inline_policies(user, inline_policies)

def main(dry_run=False):
    users = iam.list_users()['Users']
    # print(users)
    for user in users:
        process_user(user, dry_run)

if __name__ == '__main__':
    dry_run = True
    main(dry_run=dry_run)

# error handling for responses?
# check that this assigns policies correctly