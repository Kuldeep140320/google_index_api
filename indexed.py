from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import json
import pandas as pd
from googleapiclient.discovery import build
import time
import sys

# File paths and scopes
JSON_KEY_FILE = r"avathi-327311-5e77d44d5b03.json"
SCOPES = ["https://www.googleapis.com/auth/webmasters"]

# Set up credentials and build service
credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
http = credentials.authorize(httplib2.Http())
service = build('searchconsole', 'v1', credentials=credentials)

def check_indexing_status(urls):
    not_indexed_urls = []
    for url in urls:
        try:
            response = service.urlInspection().index().inspect(
                body={
                    'inspectionUrl': url.strip(),
                    'siteUrl': 'https://www.avathi.com/'  # Replace with your actual site URL
                }
            ).execute()

            if 'inspectionResult' in response:
                index_status = response['inspectionResult'].get('indexStatusResult', {}).get('coverageState', '')
                if index_status == 'NEUTRAL' or index_status == 'URL_NOT_FOUND':
                    not_indexed_urls.append(url)
                    print(f"URL not indexed: {url}")
 
            else:
                print(f"Unable to determine index status for: {url}")

            # Respect rate limits
            time.sleep(1)  # Wait for 1 second between requests

        except Exception as e:
            print(f"Error checking {url}: {str(e)}")

    return not_indexed_urls

# Read CSV file
csv = pd.read_csv(r"Deduplicated_Table.csv")

# Select a subset of URLs to check (adjust as needed)
# csv_data = csv.iloc

# Get list of URLs
urls_to_check = csv["URL"].tolist()
# print(urls_to_check)
# sys.exit()
# Check indexing status
non_indexed_urls = check_indexing_status(urls_to_check)

# Print results
print("\nNon-indexed URLs:")
for url in non_indexed_urls:
    print(url)

# Optionally, save non-indexed URLs to a new CSV file
non_indexed_df = pd.DataFrame(non_indexed_urls, columns=["URL"])
non_indexed_df.to_csv("non_indexed_urls.csv", index=False)