import boto3
import sys
from datetime import datetime
from botocore.client import Config
from wikidiary import Wiki
import os
import re

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

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

def extract_diary_date(content):
    """Extract the diary date from the content (assuming it's in ISO format)."""
    match = re.search(r"\d{4}-\d{2}-\d{2}", content)  # Look for YYYY-MM-DD format
    return match.group(0) if match else None


def update_wiki_page_content(new_content, existing_content, diary_date):
    """Update the wiki page by replacing an existing section or prepending a new one."""
    # Generate new section header
    upload_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_section_header = f"== Diary Entry for {diary_date} (Uploaded: {upload_timestamp}) ==\n"

    # Define a regex to find existing sections for this diary date
    diary_section_pattern = rf"== Diary Entry for {diary_date} \(Uploaded: .*?\) ==\n(.*?)(?=\n== |\Z)"

    # Check if this diary date already exists
    match = re.search(diary_section_pattern, existing_content, re.DOTALL)

    if match:
        # Replace existing entry
        updated_content = re.sub(diary_section_pattern, new_section_header + new_content, existing_content, flags=re.DOTALL)
        print(f"Replacing existing diary entry for {diary_date}.")
    else:
        # Prepend new entry
        updated_content = f"{new_section_header}{new_content}\n\n{existing_content}"
        print(f"Adding new diary entry for {diary_date}.")

    return updated_content

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



    wiki_page_title = f"{WIKI_PAGE_TITLE}_{year}_{month}"

    existing_content = wiki.get_wiki_page_content(wiki_page_title)
    new_content = download_file(latest_file)
    content = update_wiki_page_content(new_content,existing_content,date_string)
    if not existing_content:
        print(f"existing_content:  {existing_content}")
        content = content + f"\n\n== Metadata == \n[[Category:Wikicontent]]"

    result = wiki.upload_wiki_page(wiki_page_title,content)
    sys.stdout.reconfigure(encoding='utf-8')
    print("Wiki update response:", result)

if __name__ == "__main__":
    main()