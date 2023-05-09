from session import init_boto3_session
from cloudtrail_mfa import put_cloudtrail_mfa
from analyze_iam import get_user_policies
from iam_groups import dettach_policies, create_iam_groups
session = init_boto3_session()

search_term="andrew_koh"

# put_cloudtrail_mfa(session=session)
get_user_policies(session=session, search_term=search_term)
# create_iam_groups(session=session, search_term=search_term)
# dettach_policies(session=session, search_term=search_term)

