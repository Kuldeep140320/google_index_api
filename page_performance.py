import requests
from bs4 import BeautifulSoup
import textstat
from urllib.parse import urljoin
import re


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
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and split into paragraphs
        text = soup.get_text()
        paragraphs = re.split(r'\n\s*\n', text)
        
        overall_score = textstat.flesch_reading_ease(text)
        difficult_paragraphs = []
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.split()) > 20:  # Only analyze paragraphs with more than 20 words
                score = textstat.flesch_reading_ease(paragraph)
                if score < 60:
                    difficult_paragraphs.append({
                        'index': i,
                        'content': paragraph,
                        'score': score
                    })
        
        print(f"\nContent Quality Analysis:")
        print(f"Overall Readability Score: {overall_score:.2f}")
        print(f"Number of difficult paragraphs: {len(difficult_paragraphs)}")
        
        if difficult_paragraphs:
            print("\nDifficult paragraphs:")
            for para in difficult_paragraphs:
                print(f"\nParagraph {para['index']+1}:")
                print(f"Readability Score: {para['score']:.2f}")
                print(f"Content: {para['content'][:200]}...")  # Print first 200 characters
        
        return overall_score, difficult_paragraphs
        
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None, None
def analyze_image_seo(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        images = soup.find_all('img')
        
        print(f"\nAnalyzing Image SEO for: {url}")
        print(f"Total images found: {len(images)}")
        
        for idx, img in enumerate(images, 1):
            print(f"\nImage {idx}:")
            
            # Check for alt text
            alt_text = img.get('alt', '')
            print(f"Alt text: {'Present' if alt_text else 'Missing'}")
            if alt_text:
                print(f"Alt text content: {alt_text}")
            
            # Check for title attribute
            title = img.get('title', '')
            print(f"Title attribute: {'Present' if title else 'Missing'}")
            
            # Check image source
            src = img.get('src', '')
            if src:
                full_src = urljoin(url, src)
                print(f"Image source: {full_src}")
                
                # Check image file size
                try:
                    img_response = requests.head(full_src, allow_redirects=True)
                    img_size = int(img_response.headers.get('content-length', 0))
                    if img_size > 0:
                        print(f"Image size: {img_size / 1024:.2f} KB")
                        
                        if img_size > 200 * 1024:  # If larger than 200KB
                            print("Warning: Image size is large. Consider optimizing.")
                    else:
                        print("Image size: Unable to determine")
                except requests.RequestException:
                    print("Error: Couldn't fetch image size.")
            else:
                print("Error: Image source not found.")
            
            # Check for lazy loading
            loading = img.get('loading', '')
            print(f"Lazy loading: {'Implemented' if loading == 'lazy' else 'Not implemented'}")
            
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
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
    

    print("\nImage SEO Analysis:")
    analyze_image_seo(url) 
    
    print("\nContent Quality Analysis:")
    # analyze_content_quality(url)
    overall_score, difficult_paragraphs = analyze_content_quality(url)

    if overall_score is not None:
        print(f"\nOverall recommendations:")
        if overall_score < 60:
            print("- The overall readability of the content needs improvement.")
            print("- Try to simplify language, use shorter sentences, and break up long paragraphs.")
        elif overall_score < 70:
            print("- The overall readability is okay, but there's room for improvement.")
            print("- Focus on improving the identified difficult paragraphs.")
        else:
            print("- The overall readability is good. Keep up the good work!")
            print("- Consider reviewing any identified difficult paragraphs for further improvement.")
# Example usage:
url = "https://www.avathi.com/experience/pondicherry-packages/1454"
generate_seo_report(url)
