import base64
from datetime import datetime
from wikidiary import Wiki, DiaryBox, DiarySet
import sys
from pathlib import Path
import os
import boto3
import json

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# MinIO Configuration
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
BUCKET_NAME = os.getenv('BUCKET_NAME')


# Initialize MinIO S3 Client
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,  # Custom MinIO endpoint
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
)


sys.setrecursionlimit(1500)

def list_json_files(prefix=r"messages/raw/year=2025/month=03/day=03/"):
    """List all JSON files in the specified MinIO path."""
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

    if "Contents" in response:
        json_files = [obj["Key"] for obj in response["Contents"] if obj["Key"].endswith(".json")]
        # print(f"{len(json_files)} files found in bucket")
        return json_files
    return []



def fetch_json_from_minio(file_key):
    """Download and load a JSON file from MinIO."""
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
    json_data = json.loads(response["Body"].read().decode("utf-8"))
    return json_data

def file_to_base64(file_path):
    """Convert a file to a base64-encoded string."""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def base64_to_image(base64_string, output_filename):
    """Converts a Base64 string to an image file."""
    image_data = base64.b64decode(base64_string)  # Decode Base64 to binary
    with open(output_filename, "wb") as file:
        file.write(image_data)


class TelegramMessageJSON:
	date = None
	media = None
	photo = None
      
	def __init__(self,json_content):
		message = json_content["message"]
		
		self.date = message["date"]
		self.date = datetime.strptime(self.date,'%Y-%m-%dT%H:%M:%S')
		self.id = message["id"]
		self.text = message["message"]
		self.message = message
		self.media = message["media"]
		self.chat_id = message["chat_id"]
		self.sender_id = message["sender_id"]

	def download_media(self,path):
		base64_to_image(self.media["base64"], path)
		return(path)



# Check if an argument is provided
if len(sys.argv) < 2:
    date_choice = "2025-03-01"
else:
    # Get the input argument
    date_choice  = sys.argv[1]

year, month, day = date_choice.split("-")

prefix = f"messages/raw/year={year}/month={month}/day={day}/"
print(f"Searching messages for: {year}-{month}-{day} in {prefix}")

# Example usage
json_files = list_json_files(prefix)  # Get all JSON files in "messages/" folder
#print(json_files)


# Example usage
messages = []
for file_key in json_files:
	json_content = fetch_json_from_minio(file_key)
	msg = TelegramMessageJSON(json_content)
	messages.append(msg)
	#print(f"Content of {file_key} ({type(msg)}):\n {msg.id}: {msg.date}\n{msg.text}")



###
# Filtering messages by Date
#
message_array = []
for message in messages:
	message_date = message.date.strftime("%Y-%m-%d")
	if str(message_date) == str(date_choice):
		#message_array.append(message)
		message_array.append(message)

print(f"Message Array: {len(message_array)}")

###
# Creating Box objects from Telegram message array
#
box_array = []
for message in message_array:
	if message.text is None:
		continue
	box = DiaryBox()
	box.setFromTelegramMessage(message)
	if box.isarray:
		#print("add array")
		box_array += box.array
	else:
		box_array.append(box)

def findInside(box,boxes):
	if box.ID != "":
		for box_inside in boxes:
			if box.ID == box_inside.inside and not box.ID == box_inside.ID:
				#print("Recurse - " + "Box " + box.title + " Box_Inside " + box_inside.title)
				if box_inside.ID != "":
					box_inside = findInside(box_inside,boxes)
				box.addBox(box_inside)
	return(box)


date_list = [box.date.strftime("%Y-%m-%d") for box in box_array]
date_list = list(set(date_list))
date_list.sort()

for date in date_list:
#for date in (str(date_choice),):
	subset = []
	subset = [a for a in box_array if a.date.strftime("%Y-%m-%d")==date]
	subset.sort(key=lambda x: x.time)
	subset = sorted(subset, key=lambda x: x.time)

	box_array_processed = []
	for box in subset:
		#print("Outer: " + box.title)
		if box.inside == "" and box.listed==False and box.ID =="":
			#print("Inner: " + box.title)
			box_array_processed.append(box)
			#print(box.ID)
		elif box.ID != "" and box.inside =="":
			box = findInside(box,box_array)
			box_array_processed.append(box)
	subset = box_array_processed


	final_output = ""
	ds = ""
	ds = DiarySet()
	ds.create_from_array(subset)
	ds.tags_from_array(subset)
	# sys.setdefaultencoding('utf-8')
	sys.stdout.reconfigure(encoding='utf-8')
	final_output = final_output + Path('./templates/DiaryBox_header').read_text().replace("${Date}",date).replace("${Tags}",ds.tags_toString())+"\n"
	#print(ds.tags_toString())
	for box in ds.boxes:
		box.upload_photo()
		box_text = box.toString().encode("utf-8").decode("utf-8")
		final_output = final_output + box_text +"\n"
	final_output = final_output + "}}\n"
	final_output = "\n".join([line for line in final_output.split("\n") if line.strip()])
	print(final_output)
