import boto3

def create_iam_groups (session: boto3.Session, search_term: str) -> None:

  iam_client = session.client('iam')
  response = iam_client.list_users()
  users = [user for user in response['Users'] if search_term in user['UserName']]

  for user in users:
      user_name = user['UserName']
      group_name = f'{user_name}-group'
      iam_client.create_group(GroupName=group_name)
      attached_policies = iam_client.list_attached_user_policies(UserName=user_name)['AttachedPolicies']
      inline_policies = iam_client.list_user_policies(UserName=user['UserName'])['PolicyNames']
      print(f"{user_name} has {len(attached_policies)} attached policies and {len(inline_policies)} inline policies")
      for policy in attached_policies:
          policy_arn = policy['PolicyArn']
          print(f"attaching {policy_arn} to {group_name}")
          iam_client.attach_group_policy(GroupName=group_name, PolicyArn=policy_arn)
      print(f"adding {user_name} to {group_name}")
      iam_client.add_user_to_group(UserName=user_name, GroupName=group_name)


def dettach_policies (session: boto3.Session, search_term: str) -> None:
    
  iam_client = session.client('iam')
  response = iam_client.list_users()
  users = [user for user in response['Users'] if search_term in user['UserName']]

  for user in users:
      user_name = user['UserName']
      attached_policies = iam_client.list_attached_user_policies(UserName=user_name)['AttachedPolicies']

      groups = iam_client.list_groups_for_user(UserName=user_name)["Groups"]
      assert(len(groups) == 1)

      group = groups[0]
      group_name = group['GroupName']
      group_policies = iam_client.list_attached_group_policies(GroupName=group_name)['AttachedPolicies']
      assert(len(group_policies) == len(attached_policies))

      for policy in attached_policies:
        assert(policy['PolicyName'] in [policy['PolicyName'] for policy in group_policies])
        iam_client.detach_user_policy(UserName=user_name, PolicyArn=policy['PolicyArn'])