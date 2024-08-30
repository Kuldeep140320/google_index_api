import requests
from bs4 import BeautifulSoup
import textstat

def validate_structured_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    structured_data = soup.find('script', type='application/ld+json')

    if structured_data:
        print(f"Structured Data Found: {structured_data.string}")
    else:
        print("No structured data found")

def check_canonical_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    canonical = soup.find('link', rel='canonical')
    print(f"Canonical URL: {canonical['href'] if canonical else 'Missing'}")

def check_broken_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            try:
                link_response = requests.head(href, timeout=5)
                if link_response.status_code == 404:
                    print(f"Broken link found: {href}")
            except requests.RequestException:
                print(f"Error checking link: {href}")

def check_seo_metadata(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('title')
    description = soup.find('meta', attrs={'name': 'description'})

    print(f"Title: {title.text if title else 'Missing'}")
    print(f"Description: {description['content'] if description else 'Missing'}")

def analyze_content_quality(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()  # Extract all text from the page

    readability_score = textstat.flesch_reading_ease(text)
    print(f"Readability Score: {readability_score}")

def generate_seo_report(url):
    print(f"Generating SEO report for: {url}\n")
    
    print("SEO Metadata:")
    check_seo_metadata(url)
    
    print("\nCanonical URL:")
    check_canonical_url(url)
    
    print("\nBroken Links:")
    check_broken_links(url)
    
    print("\nStructured Data Validation:")
    validate_structured_data(url)
    
    print("\nContent Quality Analysis:")
    analyze_content_quality(url)

# Example usage:
url = "https://www.avathi.com/experience/pondicherry-packages/1454"
generate_seo_report(url)
