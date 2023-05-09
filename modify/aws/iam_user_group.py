import boto3
import json

iam_client = boto3.client('iam')

def get_user_policies(user_name):
    attached_policies = []
    inline_policies = []
    user_policies = iam_client.list_attached_user_policies(UserName=user_name)['AttachedPolicies']
    for policy in user_policies:
        attached_policies.append(policy['PolicyArn'])
    user_policy_names = iam_client.list_user_policies(UserName=user_name)['PolicyNames']
    for policy_name in user_policy_names:
        inline_policies.append(json.loads(iam_client.get_user_policy(UserName=user_name, PolicyName=policy_name)['PolicyDocument']))
    return attached_policies, inline_policies

def get_group_policies(group_name):
    group_policies = []
    policies = iam_client.list_attached_group_policies(GroupName=group_name)['AttachedPolicies']
    for policy in policies:
        group_policies.append(policy['PolicyArn'])
    group_policy_names = iam_client.list_group_policies(GroupName=group_name)['PolicyNames']
    for policy_name in group_policy_names:
        group_policies.append(json.loads(iam_client.get_group_policy(GroupName=group_name, PolicyName=policy_name)['PolicyDocument']))
    return group_policies

def main():
    users = iam_client.list_users()['Users']
    for user in users:
        user_name = user['UserName']
        user_attached_policies, user_inline_policies = get_user_policies(user_name)
        assigned_group_name = None
        for group_name in iam_client.list_groups()['Groups']:
            group_policies = get_group_policies(group_name['GroupName'])
            if set(user_attached_policies).issubset(set(group_policies)):
                iam_client.add_user_to_group(UserName=user_name, GroupName=group_name['GroupName'])
                assigned_group_name = group_name['GroupName']
                break
        if assigned_group_name is None:
            new_group_name = user_name + "-group"
            iam_client.create_group(GroupName=new_group_name)
            iam_client.attach_group_policy(GroupName=new_group_name, PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess")
            iam_client.add_user_to_group(UserName=user_name, GroupName=new_group_name)
            assigned_group_name = new_group_name
        assigned_group_policies = get_group_policies(assigned_group_name)
        for policy in user_attached_policies:
            if policy not in assigned_group_policies:
                print("Error: User " + user_name + " has attached policy " + policy + " that is not assigned to the assigned group " + assigned_group_name + ". Please assign this policy to the group before removing it.")
            else:
                iam_client.detach_user_policy(UserName=user_name, PolicyArn=policy)
        for policy in user_inline_policies:
            print("Removing inline policy " + json.dumps(policy))
            iam_client.delete_user_policy(UserName=user_name, PolicyName=policy['Name'])

if __name__ == "__main__":
    main()
