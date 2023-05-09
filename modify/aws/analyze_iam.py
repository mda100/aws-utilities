import boto3

def get_user_policies(session: boto3.Session, search_term: str) -> None:
    iam_client = session.client('iam')

    response = iam_client.list_users()

    exceptions = [user for user in response['Users'] if search_term not in user['UserName']]
    # print(exceptions)
    users = [user for user in response['Users'] if search_term in user['UserName']]
    # print(users)
    # print(len(exceptions))

    for user in exceptions:
        attached_policies = iam_client.list_attached_user_policies(UserName=user['UserName'])
        policies = iam_client.list_user_policies(UserName=user['UserName'])
        if len(attached_policies['AttachedPolicies']) or len(policies['PolicyNames']): print(f"{user['UserName']}")


    # print(len(users))

    # num = 0
    # for user in users:
    #     attached_policies = iam_client.list_attached_user_policies(UserName=user['UserName'])
    #     num_attached_policies = len(attached_policies['AttachedPolicies'])

    #     policies = iam_client.list_user_policies(UserName=user['UserName'])
    #     num_inline_policies = len(policies['PolicyNames'])
    #     if num_inline_policies: num+=1
    # print(num)
            