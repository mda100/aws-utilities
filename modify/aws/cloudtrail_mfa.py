from boto3 import Session

def put_cloudtrail_mfa(
      session: Session,
      trail_name: str = 'management-events',
      mfa_serial: str = 'arn:aws:iam::693656978031:mfa/Andrews_phone'
      ) ->  None:
  
  mfa_code = input("Enter MFA Code: ")
  print(f'MFA Code: {mfa_code}')
  cloudtrail = session.client('cloudtrail')
  response = cloudtrail.describe_trails()
  trail = response.get('trailList', [])[0]
  if (trail.get('Name') == trail_name):
    bucket_name = trail.get('S3BucketName', None)
  else:
    bucket_name = None

  s3 = session.client('s3')
  response = s3.list_buckets()
  print(response)
  response = s3.put_bucket_versioning(
      Bucket=bucket_name,
      VersioningConfiguration={
          'Status': 'Enabled',
          'MFADelete': 'Enabled'
      },
      MFA=f"{mfa_serial} {mfa_code}"
  )
  print(response)

  response = s3.get_bucket_versioning(Bucket=bucket_name)
  versioning_status = response.get('Status')
  mfa_delete_status = response.get('MFADelete')
  if versioning_status == 'Enabled' and mfa_delete_status == 'Enabled':
      print(f"MFA delete and versioning are enabled on {bucket_name}")
  else:
      print(f"MFA delete and versioning are not enabled on {bucket_name}")
#this works, need correct MFA
# oops need credentials


# aws s3api put-bucket-versioning --bucket "aws-cloudtrail-logs-693656978031-35b9eeb6" --versioning-configuration Status=Enabled,MFADelete=Enabled --mfa "arn:aws:iam::693656978031:mfa/Andrews_phone 509064"