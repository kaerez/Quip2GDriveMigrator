# Quip2GDriveMigrator

A script to migrate Quip documents to Google Drive.

## Prerequisites

1. Obtain your Personal Access Token for Quip API from https://salesforce.quip.com/dev/token
2. Install the `requests` Python library: `pip install requests`

## Usage

1. Identify the Quip folder ID from its URL. For example, if your Quip folder URL is `https://salesforce.quip.com/1kIQOuarQJBj`, then the folder ID is `1kIQOuarQJBj`.
2. Run `quip2gdrivemigrator.py` to recursively download Quip documents as Microsoft Word (.docs) files from a Quip folder to your local disk.

```bash
>python quip2gdrivemigrator.py -h
usage: quip2gdrivemigrator.py [-h] -t API_TOKEN -f FOLDER_ID -d DEST_FOLDER -m TITL_TO_URL_MAP_FILE [--throttle_threshold THROTTLE_THRESHOLD]

Quip doc to Google Drive Migrator

options:
  -h, --help            show this help message and exit
  -t, --api_token API_TOKEN
                        Access token for Quip API
  -f, --folder_id FOLDER_ID
                        ID of the Quip folder
  -d, --dest_folder DEST_FOLDER
                        Full path for the destination folder at your local disk
  -m, --titl_to_url_map_file TITL_TO_URL_MAP_FILE
                        Output file name in the destination folder that logs title to URL mappings
  --throttle_threshold THROTTLE_THRESHOLD
                        Interval in seconds between each Quip API call (default=2)
```

An example command is at below
```bash
python quip2gdrivemigrator.py -t <MY_ACCESS_TOKEN> -f 7aeFO13OHNPA -d "/Users/sam.he/Documents/Quip Docs" -m map.txt
```

3. (Optional) Go to https://drive.google.com/drive/settings and enable "Convert uploads to Google Docs editor format". By converting the .docx documents to Google Doc format, the documents will open much faster in Google Drive.
   ![Google Drive Setting](resources/Google%20Drive%20Setting.png)
4. Drag & Drop the Quip doc folder from your local disk to Google Drive

## ToDo

 - Automate step 4 above by using the Google Drive API.
