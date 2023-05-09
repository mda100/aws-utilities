import boto3

# Create CloudWatch client
cloudwatch = boto3.client('cloudwatch')

# Enable metric filters for CloudTrail logs
def enable_metric_filters():
    
    # Open CloudWatch dashboard
    cloudwatch_url = 'https://console.aws.amazon.com/cloudwatch/home?region='
    regions = ['us-east-1', 'us-west-1', 'us-west-2', 'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1', 'sa-east-1']
    for region in regions:
        print('Region:', region)
        region_cloudwatch = boto3.client('cloudwatch', region_name=region)
        print(cloudwatch_url+region+'#metricsV2:')

        # Enable metric filter for CloudTrail event count
        metric_filters = region_cloudwatch.describe_metric_filters(
            logGroupName='/aws/cloudtrail/AWSLogs/<account-id>/CloudTrail',  # replace <account-id> with your AWS account ID
            metricName='CloudTrailEventCount'
        )
        if not metric_filters['metricFilters']:
            print('No metric filter found for CloudTrailEventCount')
            response = region_cloudwatch.put_metric_filter(
                logGroupName='/aws/cloudtrail/AWSLogs/<account-id>/CloudTrail',  # replace <account-id> with your AWS account ID
                filterName='CloudTrailEventCount',
                filterPattern='{ $.eventType != "AwsServiceEvent" }',
                metricTransformations=[
                    {
                        'metricNamespace': 'CloudTrailMetrics',
                        'metricName': 'CloudTrailEventCount',
                        'metricValue': '1'
                    }
                ]
            )
            print('Enabled metric filter for CloudTrailEventCount')
        else:
            print('Metric filter already enabled for CloudTrailEventCount')

        # Enable metric filters for security threats
        metric_filters = [
            {
                'filterName': 'UnauthorizedApiCalls',
                'filterPattern': '{ ($.errorCode = *UnauthorizedOperation) || ($.errorCode = AccessDenied*) }'
            },
            {
                'filterName': 'SignInWithoutMfa',
                'filterPattern': '{ ($.eventName = ConsoleLogin) && ($.additionalEventData.MFAUsed != Yes) }'
            },
            {
                'filterName': 'RootAccountUsage',
                'filterPattern': '{ $.userIdentity.type = "Root" && $.userIdentity.invokedBy NOT EXISTS && $.eventType != "AwsServiceEvent" }'
            },
            {
                'filterName': 'IamPolicyChanges',
                'filterPattern': '{($.eventName=DeleteGroupPolicy)||($.eventName=DeleteRolePolicy)||($.eventName=DeleteUserPolicy)||($.eventName=PutGroupPolicy)||($.eventName=PutRolePolicy)||($.eventName=PutUserPolicy)||($.eventName=CreatePolicy)||($.eventName=DeletePolicy)||($.eventName=CreatePolicyVersion)||($.eventName=DeletePolicyVersion)||($.eventName=AttachRolePolicy)||($.eventName=DetachRolePolicy)||($.eventName=AttachUserPolicy)||($.eventName=DetachUserPolicy)||($.eventName=AttachGroupPolicy)||($.eventName=DetachGroupPolicy)}'
            },
            {
                'filterName': 'CloudTrailConfigurationChanges',
                'filterPattern': '{ ($.eventName = CreateTrail) || ($.eventName = UpdateTrail) || ($.eventName = DeleteTrail) || ($.eventName = StartLogging) || ($.eventName = StopLogging) }'
            },
            {
                'filterName': 'SignInFailures',
                'filterPattern': '{ ($.eventName = ConsoleLogin) && ($.errorMessage = "Failed authentication") }'
            },
            {
                'filter
