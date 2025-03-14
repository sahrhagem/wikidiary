import boto3
import os
from botocore.exceptions import NoCredentialsError
import sys
from datetime import datetime

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# MinIO Configuration
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
BUCKET_NAME = "wikidiary"

# Initialize MinIO S3 Client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,  # Custom MinIO endpoint
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)

# Upload the file
FILE_PATH = "data.txt"
date_string = sys.argv[1]
date_obj = datetime.strptime(date_string, "%Y-%m-%d")
print(date_string)
# Extract individual components
year = date_obj.year
month = date_obj.month
day = date_obj.day
KEY_PATH = f"diary/year={year}/month={month}/day={day}/smw_{date_string}.txt"

try:
    s3_client.upload_file(FILE_PATH, BUCKET_NAME, KEY_PATH)
    print(f"File '{FILE_PATH}' uploaded as '{KEY_PATH}' in bucket '{BUCKET_NAME}'.")
except NoCredentialsError:
    print("Credentials not available.")
except Exception as e:
    print(f"Error: {e}")