from wikidiary import Wiki

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

wiki = Wiki()
wiki.download_data_s3()