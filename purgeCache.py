import requests
import xml.etree.ElementTree as ET
import pandas as pd
import sys
# Function to fetch and parse any sitemap or sitemap index
def fetch_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to fetch sitemap: {response.status_code}")

# Function to extract URLs from a sitemap (regular sitemap)
def extract_urls_from_sitemap(sitemap_xml):
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    tree = ET.ElementTree(ET.fromstring(sitemap_xml))
    urls = []
    for url in tree.findall('.//ns:url/ns:loc', namespaces):
        modified_url = url.text.replace("https://www.avathi.com/", "scrapped-data/")

        urls.append(modified_url+'/index.html')
    # print(urls)
    # sys.exit()
    return urls

# Function to extract sitemap URLs from a sitemap index
def extract_sitemaps_from_index(sitemap_xml):
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    tree = ET.ElementTree(ET.fromstring(sitemap_xml))
    sitemap_urls = []
    for sitemap in tree.findall('.//ns:sitemap/ns:loc', namespaces):
        sitemap_urls.append(sitemap.text)
    return sitemap_urls
def purge_cache(urls, api_token, base_url="https://api.gumlet.com/v1/purge/avathioutdoors"):

    headers = {
        'Authorization': f'Bearer {api_token}',
        'accept': 'application/json',
        'content-type': 'application/json'
    }

    payload = {
        "paths": urls
    }
    # print(payload)
    # sys.exit()
    
    response = requests.post(base_url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Cache successfully purged for URLs: {urls}")
    else:
        print(f"Failed to purge cache. Status code: {response.status_code}, Response: {response.text}")

# Main function to handle sitemap index and URLs
def main():
    sitemap_url = 'https://www.avathi.com/sitemap.xml'  # Main sitemap URL

    # Fetch the main sitemap (index)
    try:
        sitemap_xml = fetch_sitemap(sitemap_url)
        sitemaps = extract_sitemaps_from_index(sitemap_xml)  # Extract sitemaps from index
        # sitemaps=['https://www.avathi.com/stories/sitemap.xml']
        # print(sitemaps)
        # print("d")
        # print(storysitemaps)
        # sys.exit()
        all_urls = []
        
        # Fetch and extract URLs from each sitemap in the index
        for sitemap in sitemaps:
            # print(f"Fetching sitemap: {sitemap}")
            sitemap_content = fetch_sitemap(sitemap)
            urls = extract_urls_from_sitemap(sitemap_content)
            all_urls.extend(urls)

        print(f"Total URLs extracted: {len(all_urls)}")
        api_token='gumlet_0cb2ec7efddbd39dbe9836413faa9bde'
        chunk_size = 50  # Set a limit on how many URLs per request, adjust as needed
        for i in range(0, len(all_urls), chunk_size):
            purge_cache(all_urls[i:i+chunk_size], api_token)
        
        # print(all_urls)  # Print or process the URLs as needed

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
