#!/bin/bash

echo "Running pipeline for $1"
echo "Generating SMW Text..."
poetry run python wikidiary/scripts/generate_diary_smw_s3.py $1 > data.txt
sed -i '/^$/d' data.txt
echo "Done."

echo "Uploading SMW to S3"
poetry run python wikidiary/scripts/upload_smw_s3.py $1
echo "Done."


echo "Uploading SMW from S3 to Wiki"
poetry run python wikidiary/scripts/transfer_s3_to_wiki.py $1
echo "Done."

echo "Uploading Preview from Wiki"
poetry run python wikidiary/scripts/show_wiki_diary.py $1
echo "Done."
