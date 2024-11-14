import requests
from bs4 import BeautifulSoup
import textstat
from urllib.parse import urljoin, urlparse
import re
from urllib.robotparser import RobotFileParser
import ssl
import socket
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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
    time.sleep(10) 
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
    time.sleep(5) 
    soup = BeautifulSoup(response.content, 'html.parser')
    time.sleep(5) 

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

def check_googlebot_factors(url):
    print("\nChecking Googlebot Crawling Factors:")
    
    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Load the page
        driver.get(url)
        
        # Wait for the page to load (adjust the time as needed)
        time.sleep(3)  # Wait for 10 seconds
        
        # Wait for a specific element to be present (e.g., body tag)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Get the page source after JavaScript execution
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # 1. Check robots.txt
        robots_url = urljoin(base_url, '/robots.txt')
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        print(f"1. Robots.txt allows Googlebot: {rp.can_fetch('Googlebot', url)}")
        
        # 2. Check for noindex meta tag
        noindex = soup.find('meta', attrs={'name': 'robots', 'content': lambda x: x and 'noindex' in x.lower()})
        print(f"2. Noindex directive: {'Present' if noindex else 'Not present'}")
        
        # 3. Check for rel="nofollow" on links
        nofollow_links = soup.find_all('a', attrs={'rel': 'nofollow'})
        print(f"3. Nofollow links: {len(nofollow_links)} found")
        
        # 4. Check HTTPS
        print(f"4. HTTPS: {'Used' if parsed_url.scheme == 'https' else 'Not used'}")
        
        # 5. Check mobile-friendliness (basic check)
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        print(f"5. Mobile viewport meta tag: {'Present' if viewport else 'Missing'}")
        
        # 6. Check page load speed
        navigation_start = driver.execute_script("return window.performance.timing.navigationStart")
        load_event_end = driver.execute_script("return window.performance.timing.loadEventEnd")
        load_time = (load_event_end - navigation_start) / 1000  # Convert to seconds
        print(f"6. Page load time: {load_time:.2f} seconds")
        
        # 7. Check for sitemap
        sitemap_url = urljoin(base_url, '/sitemap.xml')
        sitemap_response = driver.get(sitemap_url)
        print(f"7. Sitemap: {'Found' if 'xml' in driver.page_source.lower() else 'Not found'}")
        
        # 8. Check for hreflang tags
        hreflang = soup.find_all('link', attrs={'rel': 'alternate', 'hreflang': True})
        print(f"8. Hreflang tags: {len(hreflang)} found")
        
        # 9. Check SSL certificate
        hostname = parsed_url.netloc
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
                cert = secure_sock.getpeercert()
        print(f"9. Valid SSL certificate: {'Yes' if cert else 'No'}")
        
        # 10. Check for structured data
        structured_data = soup.find_all('script', type='application/ld+json')
        print(f"10. Structured data: {'Present' if structured_data else 'Not found'}")
        
    except Exception as e:
        print(f"Error during Googlebot factor check: {str(e)}")
    
    finally:
        driver.quit()

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
    
    # Add the new Googlebot factors check
    check_googlebot_factors(url)

# Example usage
url = "https://www.avathi.com/place/khurpa-taal/7821"
generate_seo_report(url)