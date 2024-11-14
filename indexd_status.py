import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
def check_indexing(url):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(f"https://www.google.com/search?q=site:{url}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "result-stats"))
        )
        indexed = "No results found" not in driver.page_source
    except Exception as e:
        print(f"Error checking {url}: {str(e)}")
        indexed = False
    finally:
        driver.quit()
    
    return indexed
all_urls_s= pd.read_csv("sitemap_urls.csv")
# print(all_urls)
# sys.exit()
all_urls=all_urls_s.iloc[:100]
indexed_urls = []
not_indexed_urls = []
# Check each URL
for index, row in all_urls.iterrows():
    url = row['URL']  # Assuming the column name is 'URL'
    print(f"Checking {url}...")
    
    if check_indexing(url):
        indexed_urls.append(url)
    else:
        not_indexed_urls.append(url)
    
    # Add a delay to avoid overwhelming Google with requests
    time.sleep(2)

# Create DataFrames for indexed and not indexed URLs
indexed_df = pd.DataFrame({'URL': indexed_urls})
not_indexed_df = pd.DataFrame({'URL': not_indexed_urls})

# Save to CSV files
indexed_df.to_csv('indexed_urls.csv', index=False)
not_indexed_df.to_csv('not_indexed_urls.csv', index=False)

print(f"Indexed URLs: {len(indexed_urls)}")
print(f"Not Indexed URLs: {len(not_indexed_urls)}")
print("Results saved to 'indexed_urls.csv' and 'not_indexed_urls.csv'")