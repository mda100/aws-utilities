#TODO: add filter by region option to avoid looping through all buckets

# requires python 3.10+
import boto3
from typing import Callable
import json
import logging


with open('config.json') as f:
    config = json.load(f)

TARGET_BUCKET = config.get("TARGET_BUCKET") # type : str
TARGET_PREFIX = config.get("TARGET_PREFIX") # type : str
LOG_PATH = config.get("LOG_PATH") # type : str
ALLOWED_MODIFICATIONS = config.get("ALLOWED_MODIFICATIONS") # type : List[str]
EXCLUDED_BUCKETS = config.get("EXCLUDED_BUCKETS") # type : List[str]


# assert(METHOD)
# assert(METHOD in ALLOWED_MODIFICATIONS)

## Modification Functions: (s3_client: any, bucket_name: str) -> dict##

def public_access_block (s3_client: any, bucket_name: str) -> dict:
  response = s3_client.put_public_access_block(
    Bucket=bucket_name,
    PublicAccessBlockConfiguration={
        "BlockPublicAcls": True,
        "IgnorePublicAcls": True,
        "BlockPublicPolicy": True,
        "RestrictPublicBuckets": True
    }
  )
  return response

def update_bucket (s3_client: any, bucket_name: str, method: Callable[[any, str],dict], automate: bool = False) -> None:

  logging.basicConfig(filename='s3_modification.log', level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
  
  proceed = automate or input(f"Reset bucket: {bucket_name}? (y/n): ").lower().strip() == 'y'

  if (proceed):   
    try:
      response = method(s3_client, bucket_name)
      if(response.get('ResponseMetadata').get('HTTPStatusCode') == 200):
        logging.info(f"bucket: {bucket_name} - Success")
      else:
        logging.info(f"bucket: {bucket_name} - Failure: Bad Response")
    except:
      logging.info(f"bucket: {bucket_name} - Failure: Can't Connect")
  else:
    print(f"cancelled reset of bucket {bucket_name}")

# def update_buckets_iter (method: Callable[[any, str],dict], s3_token: str = S3_TOKEN, automate: bool = False) -> None:
#   session = boto3.Session(
#     aws_access_key_id=ACCESS_KEY_ID,
#     aws_secret_access_key=ACCESS_KEY,
#     region_name=REGION
#   )
#   s3_client = session.client('s3')
#   buckets = s3_client.list_buckets().get('Buckets',[])
#   buckets_list = [bucket['Name'] for bucket in buckets if s3_token in bucket['Name']]
#   print (f"applying check logging to {len(buckets_list)} s3 buckets...")
#   for bucket_name in buckets_list:
#     print(f"bucket: {bucket_name}")
#     update_bucket(s3_client=s3_client, bucket_name=bucket_name, method=method, automate=automate)



def delete_bucket_contents (s3_client: any, bucket_name: str) -> None:

  def _log (success: bool, message: str) -> None:
    success_str = "success" if success else "failure"
    with open(f"{LOG_PATH}check-logging-{success_str}.csv", "a+") as f:
      f.write(f"{message},")

  proceed = input(f"Reset bucket: {bucket_name}? (y/n): ").lower().strip() == 'y'

  if (proceed):   
    try:
      objects = s3_client.list_objects_v2(Bucket=bucket_name).get('Contents',[])
      keys = [{'Key': obj['Key']} for obj in objects]
      response = s3_client.delete_objects(
        Bucket=bucket_name,
        Delete={
            'Objects': keys,
            'Quiet': True
        }
      )
      if(response.get('ResponseMetadata').get('HTTPStatusCode') == 200):
        _log(success=True, message=f"{bucket_name}")
      else:
        _log(success=False, message=f"{bucket_name}")
    except:
      _log(success=False, message=f"{bucket_name}")
  else:
    print(f"cancelled reset of bucket {bucket_name}")

def add_versioning (s3_client: any, bucket_name: str) -> dict:
  response = s3_client.put_bucket_versioning(
    Bucket=bucket_name,
    VersioningConfiguration={
      'Status': 'Enabled'
    }
  )
  return response

def check_logging (s3_client: any, bucket_name: str) -> None:
  try: 
    logging_config = s3_client.get_bucket_logging(Bucket=bucket_name)
    if 'LoggingEnabled' in logging_config:
        target_bucket = logging_config['LoggingEnabled']['TargetBucket']
        target_prefix = logging_config['LoggingEnabled']['TargetPrefix']
        if not target_prefix.endswith('/'):
          target_prefix += '/'
          logging_config = {
            'LoggingEnabled': {
                'TargetBucket': target_bucket,
                'TargetPrefix': target_prefix
            }
          }
          response = s3_client.put_bucket_logging(
              Bucket=bucket_name,
              BucketLoggingStatus=logging_config
          )
          if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
            with open(f"{LOG_PATH}check-logging-success.csv", "a+") as f:
              f.write(f"{bucket_name}: {target_bucket}/{target_prefix},")
          else:
            with open(f"{LOG_PATH}check-logging-failure.txt", "a+") as f:
              f.write(f"{bucket_name}-{response.get('ResponseMetadata').get('HTTPStatusCode')}")
        with open(f"{LOG_PATH}check-logging-success.csv", "a+") as f:
          f.write(f"{bucket_name}: {target_bucket}/{target_prefix},")
    else:
      with open(f"{LOG_PATH}check-logging-failure.txt", "a+") as f:
        f.write(f"{bucket_name}-logging-not-enabled")
  except:
    with open(f"{LOG_PATH}check-logging-failure.txt", "a+") as f:
      f.write(f"{bucket_name}-http-failure")
    

def add_logging (s3_client: any, bucket_name: str) -> dict:
  response = s3_client.put_bucket_logging(
    Bucket=bucket_name,
    BucketLoggingStatus={
        'LoggingEnabled': {
            'TargetBucket': TARGET_BUCKET,
            'TargetPrefix': f"{TARGET_PREFIX}{bucket_name}/"
        }
      }
    )
  return response

## Utilities ##
class Modification:
    def __init__(self, value: str, modifier: Callable[[any, str],dict]):
        if value not in ALLOWED_MODIFICATIONS:
            raise ValueError(f"Value '{value}' is not allowed. Allowed values are: {ALLOWED_MODIFICATIONS}")
        self.value = value
        self.modify = modifier

def modify_bucket(s3_client: any, bucket_name: str, modification: Modification) -> None:
    
    def _log(bucket_name: str, modification: str, success: bool) -> None:
      assert modification in ALLOWED_MODIFICATIONS
      status = "success" if success else "failure"
      with open(f"{LOG_PATH}{bucket_name}-{modification}-{status}.txt", "w") as f:
        f.write(f"{modification} {status} for bucket: {bucket_name}")
    
    try:
      response = modification.modify(s3_client, bucket_name)
      if response.get('ResponseMetadata').get('HTTPStatusCode') == 200:
        _log(bucket_name=bucket_name, modification=modification.value,success=True)
      else:
         _log(bucket_name=bucket_name, modification=modification.value,success=False)
    except:
      _log(bucket_name=bucket_name, modification=modification.value,success=False)

def choose_method(method: str) -> None:
   assert method in ALLOWED_MODIFICATIONS
   match method:
      case "versioning":
         return Modification(value="versioning", modifier=add_versioning)
      case "logging":
         return Modification(value="logging", modifier=add_logging)
      case other:
         raise ValueError((f"Allowed values are: {ALLOWED_MODIFICATIONS}"))


session = boto3.Session()
s3_client = session.client('s3')
buckets = s3_client.list_buckets().get('Buckets',[])

for bucket in buckets:
  bucket_name = bucket.get('Name')
  if bucket_name == 'aws-cloudtrail-logs-693656978031-35b9eeb6':
    continue
  try:
    response = add_versioning(s3_client=s3_client, bucket_name=bucket_name)
  except:
    raise BaseException(f"failed request bucket: {bucket_name}")
