import requests
from bs4 import BeautifulSoup

# List of URLs to be processed
urls = [
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    
     "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    "https://www.avathi.com/activity/visit-kalapani-lake-in-chikhaldara/260",
    
 
 
]

# Define Googlebot Smartphone User-Agent
googlebot_smartphone_user_agent = (
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
)

# Function to fetch and analyze a single URL
def fetch_url(url):
    try:
        # Send HTTP GET request with Googlebot Smartphone User-Agent
        headers = {"User-Agent": googlebot_smartphone_user_agent}
        response = requests.get(url, headers=headers, timeout=10)

        # Check HTTP response status
        if response.status_code == 200:
            print(f"Fetched Successfully: {url}")
            
            # Parse the content with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Analyze the page (extract title, meta description, etc.)
            title = soup.title.string if soup.title else "No title found"
            meta_description = soup.find("meta", attrs={"name": "description"})
            meta_description_content = meta_description["content"] if meta_description else "No description found"

            print(f"Title: {title}")
            print(f"Meta Description: {meta_description_content}")
            return True  # Indicate success
        else:
            print(f"Failed to fetch {url} - Status Code: {response.status_code}")
            return False  # Indicate failure
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return False

# Process all URLs in the array
def process_urls(urls):
    for url in urls:
        print(f"Processing URL: {url}")
        success = fetch_url(url)
        if success:
            print(f"URL processed successfully: {url}\n")
        else:
            print(f"URL failed to process: {url}\n")

# Start processing
if __name__ == "__main__":
    process_urls(urls)
