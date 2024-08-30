from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import json

# Initialize credentials and HTTP object
JSON_KEY_FILE = r"avathi-327311-5e77d44d5b03.json"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
http = credentials.authorize(httplib2.Http())

def check_url_status(url, http):
    ENDPOINT = f"https://indexing.googleapis.com/v3/urlNotifications/metadata?url={url}"
    
    try:
        response, content = http.request(ENDPOINT, method="GET")
        result = json.loads(content.decode())

        if "urlNotificationMetadata" in result:
            metadata = result["urlNotificationMetadata"]
            print(f"URL: {metadata.get('url')}")
            if "latestUpdate" in metadata:
                latest_update = metadata["latestUpdate"]
                print(f"Latest Update Type: {latest_update.get('type')}")
                print(f"Latest Update Time: {latest_update.get('notifyTime')}")
            else:
                print("No updates found for this URL.")
        else:
            print(f"No metadata found for URL: {url}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# List of URLs to check (replace with your actual list)
urls_to_check = [
    "https://www.avathi.com/guide/munnar/15",
    "https://www.avathi.com/guide/gaya/18",
    "https://www.avathi.com/guide/patna/19",
    
    # Add more URLs here
]

# Check status for each URL
for url in urls_to_check:
    check_url_status(url, http)
