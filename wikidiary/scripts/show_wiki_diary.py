import boto3
from botocore.exceptions import NoCredentialsError
import sys
from wikidiary import Wiki
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import base64
from botocore.client import Config
import traceback
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

base_url = os.getenv('WIKI_BASE_URL')
USERNAME = os.getenv('WIKI_BASIC_AUTH_USER')
PASSWORD = os.getenv('WIKI_BASIC_AUTH_PW')


# MinIO Configuration
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
BUCKET_NAME = "wikidiary"
PREFIX = "preview"  # If files are stored with a date-based prefix

# Initialize MinIO client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
)



def display_click_data(date):

    wiki = Wiki()

    request_text = """
    {{{{#ask:
    [[Has log::Tagebuch]][[Has date::{date}]]
    |?Has date#ISO =Date
    |?Has agenda =Agenda
    |?Has tag =Tag
    |?Has book =Book
    |?Has sport
    |?Has location
    |?Has essen
    |?Has spiel
    |?Has laden
    |?Has film
    |?Has serie
    |?Has podcast
    |?Has musik
    |?Has person
    |?Has situation
    |?Has event
    |?Has haushalt
    |?Has place
    |?Has krankheit
    |?Has pflanze
    |format=template
    |introtemplate=Diary Table Header
    |template=Diary Table Body
    |outrotemplate=Diary Table Footer
    |sort=Has date
    |order=desc
    |mainlabel=-
    |limit=1
    }}}}"""
    
    #request_text ="{{#ask:[[Has log::Tagebuch]][[Has date::{clicked_day}]]|?Has date#ISO =Date|?Has agenda =Agenda|?Has tag =Tag|?Has book =Book|?Has sport|?Has location|?Has essen|?Has spiel|?Has laden|?Has film|?Has serie|?Has podcast|?Has musik|?Has person|?Has situation|?Has event|?Has haushalt|?Has place|?Has krankheit|?Has pflanze|format=template|introtemplate=Diary Table Header|template=Diary Table Body|outrotemplate=Diary Table Footer}}"


    request_text= request_text.format(date=date)

    # Define the POST data
    data = {
        "action": "parse",
        "text": request_text,
        "prop": "text|images",
        "format": "json"
    }


    # Make the POST request
    try:
        response = wiki.post(data)
        response = response.json()['parse']['text']['*']

    except Exception:
        response = traceback.format_exc()
    #response.raise_for_status()
    #print(response)
    
    # response = """
    # Hallo<br>Hallo Hallo
    # """
    # response = """
    # <div class="mw-parser-output"> <table class="sortable wikitable smwtable"><tbody><tr><th>&#160;</th><th class="Date"><a href="/mediawiki/index.php/Property:Has_date" title="Property:Has date">Date</a></th></tr><tr data-row-number="1" class="row-odd"><td class="smwtype_wpg"><span class="smw-subobject-entity"><a href="/mediawiki/index.php/Tagebuch_2024_09#_0fd1f5cb21c525aa4c9b8158ac43570e" title="Tagebuch 2024 09">Tagebuch 2024 09</a></span></td><td class="Date smwtype_dat" data-sort-value="2460571.5">2024-09-18</td></tr></tbody></table></div>
    # """
    #return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(request_text)
    #response = response.replace("/mediawiki/","/assets/")

    return response
    #return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(response)



# Credentials and URL

def replace_images_with_base64(html, base_url, username, password, max_size=(200, 200), quality=20):
    """
    Replaces <a> tags containing images with <img> tags containing base64-encoded images.

    Parameters:
        html (str): The HTML content.
        base_url (str): Base URL of the MediaWiki instance.
        username (str): Username for Basic Auth.
        password (str): Password for Basic Auth.
        max_size (tuple): Max width/height for resizing.
        quality (int): Compression quality (JPEG 1-100).

    Returns:
        str: The modified HTML with base64 images.
    """
    
    soup = BeautifulSoup(html, "html.parser")

    for a_tag in soup.find_all("a", class_="image"):
        img_tag = a_tag.find("img")
        if img_tag and "src" in img_tag.attrs:
            img_url = img_tag["src"]

            # Convert relative URL to absolute
            if img_url.startswith("/"):
                img_url = base_url + img_url

            # Download the image
            response = requests.get(img_url, auth=(username, password))
            if response.status_code != 200:
                print(f"❌ Failed to download {img_url}")
                continue

            # Open and process the image
            image = Image.open(BytesIO(response.content))
            image = image.convert("RGB")  # Ensure it's RGB
            image.thumbnail(max_size)  # Resize while keeping aspect ratio

            # Save compressed image to memory
            output_buffer = BytesIO()
            image.save(output_buffer, format="JPEG", quality=quality)

            # Encode in Base64
            base64_encoded = base64.b64encode(output_buffer.getvalue()).decode()
            base64_src = f"data:image/jpeg;base64,{base64_encoded}"

            # Create new img tag
            new_img_tag = soup.new_tag("img", src=base64_src)

            # Replace the <a> tag with the new <img> tag
            a_tag.replace_with(new_img_tag)

    return str(soup)

# Convert images to base64
date_string = sys.argv[1]
html_data = display_click_data(date_string)
new_html = replace_images_with_base64(html_data, base_url, USERNAME, PASSWORD)

# Save to file (optional)
with open("output.html", "w", encoding="utf-8") as f:
    f.write(new_html.encode("utf-8").decode("utf-8"))

# Print output
#print(new_html)




# Upload the file
FILE_PATH = "output.html"
date_obj = datetime.strptime(date_string, "%Y-%m-%d")
print(date_string)
# Extract individual components
year = date_obj.year
month = date_obj.month
day = date_obj.day
KEY_PATH = f"{PREFIX}/year={year}/month={month}/day={day}/preview_{date_string}.html"

try:
    s3_client.upload_file(FILE_PATH, BUCKET_NAME, KEY_PATH)
    print(f"File '{FILE_PATH}' uploaded as '{KEY_PATH}' in bucket '{BUCKET_NAME}'.")
except NoCredentialsError:
    print("Credentials not available.")
except Exception as e:
    print(f"Error: {e}")
