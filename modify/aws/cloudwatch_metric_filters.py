import boto3

session = boto3.Session()
cloudwatch = session.client('cloudwatch')
logs = session.client('logs')
sns = session.client('sns')

LOG_GROUP_NAME = 'cloudwatch-metric-alarms'
TOPIC_ARN = 'arn:aws:sns:us-west-2:693656978031:cloudwatch-metric-alarms'

# List of metric filters
metric_filters = [
    {
        'filterName': 'UnauthorizedAPICalls',
        'filterPattern': '{ ($.errorCode = *UnauthorizedOperation) || ($.errorCode = AccessDenied*) }'
    },
    {
        'filterName': 'SignInWithoutMFA',
        'filterPattern': '{ ($.eventName = ConsoleLogin) && ($.additionalEventData.MFAUsed != Yes) }'
    },
    {
        'filterName': 'RootAccountUsage',
        'filterPattern': '{ $.userIdentity.type = Root && $.userIdentity.invokedBy NOT EXISTS && $.eventType != AwsServiceEvent }'
    },
    {
        'filterName': 'IAMPolicyChanges',
        'filterPattern': '{($.eventName=DeleteGroupPolicy)||($.eventName=DeleteRolePolicy)||($.eventName=DeleteUserPolicy)||($.eventName=PutGroupPolicy)||($.eventName=PutRolePolicy)||($.eventName=PutUserPolicy)||($.eventName=CreatePolicy)||($.eventName=DeletePolicy)||($.eventName=CreatePolicyVersion)||($.eventName=DeletePolicyVersion)||($.eventName=AttachRolePolicy)||($.eventName=DetachRolePolicy)||($.eventName=AttachUserPolicy)||($.eventName=DetachUserPolicy)||($.eventName=AttachGroupPolicy)||($.eventName=DetachGroupPolicy)}'
    },
    {
        'filterName': 'CloudTrailConfigChanges',
        'filterPattern': '{ ($.eventName = CreateTrail) || ($.eventName = UpdateTrail) || ($.eventName = DeleteTrail) || ($.eventName = StartLogging) || ($.eventName = StopLogging) }'
    },
    {
        'filterName': 'SignInFailures',
        'filterPattern': '{ ($.eventName = ConsoleLogin) && ($.errorMessage = "Failed authentication") }'
    },
    {
        'filterName': 'DisabledCMKs',
        'filterPattern': '{($.eventSource = kms.amazonaws.com) && (($.eventName=DisableKey)||($.eventName=ScheduleKeyDeletion)) }'
    },
    {
        'filterName': 'S3PolicyChanges',
        'filterPattern': '{ ($.eventSource = s3.amazonaws.com) && (($.eventName = PutBucketAcl) || ($.eventName = PutBucketPolicy) || ($.eventName = PutBucketCors) || ($.eventName = PutBucketLifecycle) || ($.eventName = PutBucketReplication) || ($.eventName = DeleteBucketPolicy) || ($.eventName = DeleteBucketCors) || ($.eventName = DeleteBucketLifecycle) || ($.eventName = DeleteBucketReplication)) }'
    },
    {
        'filterName': 'ConfigServiceChanges',
        'filterPattern': '{($.eventSource = config.amazonaws.com) && (($.eventName=StopConfigurationRecorder)||($.eventName=DeleteDeliveryChannel)||($.eventName=PutDeliveryChannel)||($.eventName=PutConfigurationRecorder))}'
    },
        {
        'filterName': 'SecurityGroupChanges',
        'filterPattern': '{ ($.eventName = AuthorizeSecurityGroupIngress) || ($.eventName = AuthorizeSecurityGroupEgress) || ($.eventName = RevokeSecurityGroupIngress) || ($.eventName = RevokeSecurityGroupEgress) || ($.eventName = CreateSecurityGroup) || ($.eventName = DeleteSecurityGroup) }'
    },
    {
        'filterName': 'NetworkACLChanges',
        'filterPattern': '{ ($.eventName = CreateNetworkAcl) || ($.eventName = CreateNetworkAclEntry) || ($.eventName = DeleteNetworkAcl) || ($.eventName = DeleteNetworkAclEntry) || ($.eventName = ReplaceNetworkAclEntry) || ($.eventName = ReplaceNetworkAclAssociation) }'
    },
    {
        'filterName': 'NetworkGatewayChanges',
        'filterPattern': '{ ($.eventName = CreateCustomerGateway) || ($.eventName = DeleteCustomerGateway) || ($.eventName = AttachInternetGateway) || ($.eventName = CreateInternetGateway) || ($.eventName = DeleteInternetGateway) || ($.eventName = DetachInternetGateway) }'
    },
    {
        'filterName': 'RouteTableChanges',
        'filterPattern': '{ ($.eventName = CreateRoute) || ($.eventName = CreateRouteTable) || ($.eventName = ReplaceRoute) || ($.eventName = ReplaceRouteTableAssociation) || ($.eventName = DeleteRouteTable) || ($.eventName = DeleteRoute) || ($.eventName = DisassociateRouteTable) }'
    },
    {
        'filterName': 'VPCChanges',
        'filterPattern': '{ ($.eventName = CreateVpc) || ($.eventName = DeleteVpc) || ($.eventName = ModifyVpcAttribute) || ($.eventName = AcceptVpcPeeringConnection) || ($.eventName = CreateVpcPeeringConnection) || ($.eventName = DeleteVpcPeeringConnection) || ($.eventName = RejectVpcPeeringConnection) || ($.eventName = AttachClassicLinkVpc) || ($.eventName = DetachClassicLinkVpc) || ($.eventName = DisableVpcClassicLink) || ($.eventName = EnableVpcClassicLink) }'
    },
    {
        'filterName': 'OrganizationsChanges',
        'filterPattern': '{ ($.eventSource = organizations.amazonaws.com) && (($.eventName = AcceptHandshake) || ($.eventName = AttachPolicy) || ($.eventName = CreateAccount) || ($.eventName = CreateOrganizationalUnit) || ($.eventName = CreatePolicy) || ($.eventName = DeclineHandshake) || ($.eventName = DeleteOrganization) || ($.eventName = DeleteOrganizationalUnit) || ($.eventName = DeletePolicy) || ($.eventName = DetachPolicy) || ($.eventName = DisablePolicyType) || ($.eventName = EnablePolicyType) || ($.eventName = InviteAccountToOrganization) || ($.eventName = LeaveOrganization) || ($.eventName = MoveAccount) || ($.eventName = RemoveAccountFromOrganization) || ($.eventName = UpdatePolicy) || ($.eventName = UpdateOrganizationalUnit)) }'
    }
]

for metric_filter in metric_filters:
  try:
    response = logs.put_metric_filter(
    logGroupName=LOG_GROUP_NAME,
    filterName=metric_filter['filterName'],
    filterPattern=metric_filter['filterPattern'],
    metricTransformations=[
        {
            'metricName': metric_filter['filterName'],
            'metricNamespace': 'CloudTrail/Metrics',
            'metricValue': '1'
        }
      ]
    )
    cloudwatch.put_metric_alarm(
        AlarmName=metric_filter['filterName'],
        MetricName=metric_filter['filterName'],
        Namespace='CloudTrail/Metrics',
        Statistic='SampleCount',
        ComparisonOperator='GreaterThanOrEqualToThreshold',
        Threshold=1,
        Period=300,
        EvaluationPeriods=1,
        AlarmActions=[
            TOPIC_ARN
        ]
      )
  except:
    raise BaseException(f"failed request metric filter: {metric_filter}")

