import boto3
import sys
from datetime import datetime
from botocore.client import Config
from wikidiary import Wiki
import os

# MinIO Configuration
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
BUCKET_NAME = "wikidiary"
PREFIX = "diary/"  # If files are stored with a date-based prefix
LATEST_FILES_COUNT = 1  # Number of latest files to process
WIKI_PAGE_TITLE = "S3_Diary_Upload"

# Initialize MinIO client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

def get_latest_file():
    """List objects in MinIO and get the latest file."""
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
    if "Contents" not in response:
        return None
    
    # Sort by last modified date (latest first)
    files = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)
    return files[0]["Key"] if files else None

def download_file(file_key):
    """Download file content from MinIO."""
    obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
    text = obj["Body"].read().decode("utf-8",errors="ignore")
    return text

def main():
    #latest_file = get_latest_file()
    date_string = sys.argv[1]
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    # Extract individual components
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day
    KEY_PATH = f"{PREFIX}year={year}/month={month}/day={day}/smw_{date_string}.txt"
    latest_file = KEY_PATH
    print(latest_file)
    if not latest_file:
        print("No files found in MinIO bucket.")
        return
    wiki = Wiki()

    new_content = download_file(latest_file)
    result = wiki.update_wiki_page(WIKI_PAGE_TITLE,new_content)
    sys.stdout.reconfigure(encoding='utf-8')
    print("Wiki update response:", result)

if __name__ == "__main__":
    main()