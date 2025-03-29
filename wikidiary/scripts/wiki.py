import requests
import yaml
import os
from datetime import datetime
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


URL = os.getenv('WIKI_API_URL')
WIKI_BASIC_AUTH_USER = os.getenv('WIKI_BASIC_AUTH_USER')
WIKI_BASIC_AUTH_PW = os.getenv('WIKI_BASIC_AUTH_PW')
WIKI_USER = os.getenv('WIKI_USER')
WIKI_PW = os.getenv('WIKI_PW')

a = (WIKI_BASIC_AUTH_USER, WIKI_BASIC_AUTH_PW)


def replaceumlaut(txt):
    txt = txt.replace("Ä","AE")
    txt = txt.replace("Ö","OE")
    txt = txt.replace("Ü","UE")
    txt = txt.replace("ä","ae")
    txt = txt.replace("ö","oe")
    txt = txt.replace("ü","ue")
    txt = txt.replace("ß","ss")
    txt = txt.replace(":_","_dp_")
    return(txt)



class Wiki:
    S = requests.Session()
    CSRF_TOKEN = ""
    LOGIN_TOKEN = ""

    def __init__(self):
        self.LOGIN_TOKEN = self.get_login_token()
        self.login()
        self.CSRF_TOKEN = self.get_csrf_token()
    def get_login_token(self):
        PARAMS_1 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }

        R = self.S.get(url=URL, params=PARAMS_1,auth=a)
        DATA = R.json()

        LOGIN_TOKEN = DATA["query"]["tokens"]["logintoken"]
        #print("LOGIN_TOKEN: " + LOGIN_TOKEN)
        return(LOGIN_TOKEN)
    def get_csrf_token(self):
        PARAMS_3 = {
            "action": "query",
            "meta":"tokens",
            "format":"json"
        }

        R = self.S.get(url=URL, params=PARAMS_3,auth=a)
        DATA = R.json()

        CSRF_TOKEN = DATA["query"]["tokens"]["csrftoken"]
        #print("CSRF_TOKEN: " + CSRF_TOKEN)
        return(CSRF_TOKEN)

    def login(self):
        PARAMS_2 = {
            "action": "login",
            "lgname": WIKI_USER,
            "lgpassword": WIKI_PW,
            "format": "json",
            "lgtoken": self.LOGIN_TOKEN
        }

        R = self.S.post(URL, data=PARAMS_2,auth=a)
    def upload_file(self,file_path,wikiname):
        #wikiname = wikiname.encode(encoding="ascii",errors="xmlcharrefreplace").decode("utf-8")
        wikiname = replaceumlaut(wikiname)
        PARAMS_4 = {
            "action": "upload",
            "filename": wikiname,
            "format": "json",
            "token": self.CSRF_TOKEN,
            "ignorewarnings": 1
        }
        #print(wikiname)

        FILE = {'file':(wikiname, open(file_path, 'rb'), 'multipart/form-data')}
        R = self.S.post(URL, files=FILE, data=PARAMS_4,auth=a)
        DATA = R.json()
        #print("Upload")
        #print(DATA)
        #print(DATA)
    def download_data(self):
        with open("meta/urls.yaml", "r") as stream:
            try:
                urls = yaml.safe_load(stream)
                os.makedirs("./download")
                for key in urls:
                    r = requests.get(urls[key], allow_redirects=True,auth = a)
                    open('download/'+key+".csv", 'wb').write(r.content)

            except yaml.YAMLError as exc:
                print(exc)

    def download_data_s3(self):
        with open("meta/urls.yaml", "r") as stream:
            try:
                urls = yaml.safe_load(stream)

                # MinIO Configuration
                MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
                ACCESS_KEY = os.getenv('ACCESS_KEY')
                SECRET_KEY = os.getenv('SECRET_KEY')
                BUCKET_NAME = os.getenv('BUCKET_NAME_WIKIDIARY')


                # Initialize MinIO S3 Client
                s3_client = boto3.client(
                    "s3",
                    endpoint_url=MINIO_ENDPOINT,  # Custom MinIO endpoint
                    aws_access_key_id=ACCESS_KEY,
                    aws_secret_access_key=SECRET_KEY,
                )


                for key in urls:
                    r = requests.get(urls[key], allow_redirects=True,auth = a)
                    KEY_PATH = f"data/download/{key}.csv"

                    try:
                        s3_client.put_object(
                            Bucket=BUCKET_NAME,
                            Key=KEY_PATH,
                            Body=r.content,  # Directly upload raw content
                            ContentType="text/csv"
                        )

                        print(f"File '{key}' uploaded as '{KEY_PATH}' in bucket '{BUCKET_NAME}'.")
                    except Exception as e:
                        print(f"Error: {e}")

            except yaml.YAMLError as exc:
                print(exc)


    def backup(self,dir):
        ### Create directory structure
        root_dir = os.path.join(dir,"backup")
        os.makedirs(root_dir)

        media_dir = os.path.join(dir,"media")
        os.makedirs(media_dir)

        articles_dir = os.path.join(dir,"articles")
        os.makedirs(articles_dir)

    def post(self,data):
        data["token"] = self.CSRF_TOKEN
        response = requests.post(URL, data=data,auth=a)
        return response

    def get_wiki_page_content(self,page_name):
        """Fetch current content of the MediaWiki page."""
        response = requests.get(URL, params={
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "titles": page_name,
            "rvprop": "content"
        },allow_redirects=True,auth = a)
        data = response.json()
        pages = data["query"]["pages"]
        page_id = next(iter(pages))
        return pages[page_id].get("revisions", [{}])[0].get("*", "")

    def update_wiki_page(self,page_name,new_content):
        """Prepend new content to the existing wiki page."""
        # Get the current page content
        existing_content = self.get_wiki_page_content(page_name)

        # Prepend new content
        updated_content = f"== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==\n{new_content}\n\n{existing_content}"

        # Edit the page
        response = self.S.post(URL, data={
            "action": "edit",
            "format": "json",
            "title": page_name,
            "text": updated_content,
            "token": self.CSRF_TOKEN
        },allow_redirects=True,auth = a)

        return response.json()

    def upload_wiki_page(self,page_name,new_content):
        """Prepend new content to the existing wiki page."""
        # Edit the page
        response = self.S.post(URL, data={
            "action": "edit",
            "format": "json",
            "title": page_name,
            "text": new_content,
            "token": self.CSRF_TOKEN
        },allow_redirects=True,auth = a)

        return response.json()
