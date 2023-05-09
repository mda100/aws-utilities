from boto3 import Session

def init_boto3_session (config_path: str = 'config.json') -> Session:

  import json
  import boto3

  with open(config_path) as f:
      config = json.load(f)
  SECRETS = config.get("SECRETS")
  with open(SECRETS) as f:
    aws_access_key_id, aws_secret_access_key = f.readline().strip().split(',')
  session = boto3.Session(
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key,
  )

  return session