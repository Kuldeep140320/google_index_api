import csv
import json
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin
from datetime import datetime

# Configurations
SEC_HEADERS = {
    "User-Agent": "PrismInfoways/1.0 (Contact: tarun@prisminfoways.com)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

# SEC_URLS = [
#     "https://www.sec.gov/Archives/edgar/data/1018724/000101872425000002/amzn-20250206.htm"
# ]
SEC_URLS = [
    "https://www.sec.gov/Archives/edgar/data/1018724/000110465924045915/tm246113d2_8k.htm",
    # "https://www.sec.gov/Archives/edgar/data/0001018724/000110465924065117/tm2414140d1_8k.htm",
    # "https://www.sec.gov/Archives/edgar/data/0001018724/000101872424000081/amzn-20240430.htm"
]

# Utility functions (same as previous message)

def get_base_url(main_url):
    return main_url.rsplit('/', 1)[0] + '/'

def split_into_chunks(text, chunk_size=2000, overlap=100):
    chunks = []
    start = 0
    end = chunk_size
    while start < len(text):
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        end = start + chunk_size
    return chunks

def fetch_and_parse_url(url, retries=3):
    while retries > 0:
        try:
            response = requests.get(url, headers=SEC_HEADERS)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.HTTPError as e:
            print(f"HTTP Error {e.response.status_code} for URL: {url}")
            if e.response.status_code == 403:
                print("❌ 403 Forbidden - SEC may have blocked the request.")
                break
            retries -= 1
            print(f"Retrying in 10 seconds... ({3 - retries}/3)")
            time.sleep(10)
    return None

# def extract_date_of_report(soup):
#     text = soup.get_text(separator=' ')
#     date_matches = re.findall(r'([A-Z][a-z]+ \d{1,2}, \d{4})', text)
#     if not date_matches:
#         return ""

#     report_date_index = text.find("Date of Report")
#     if report_date_index == -1:
#         closest_date = date_matches[0]
#     else:
#         closest_date = min(
#             date_matches,
#             key=lambda date: abs(report_date_index - text.find(date))
#         )

#     try:
#         parsed_date = datetime.strptime(closest_date, "%B %d, %Y")
#         return parsed_date.strftime("%d-%m-%Y")
#     except ValueError:
#         return closest_date

# def extract_filing_type(soup):
#     return "8-K" if "FORM 8-K" in soup.get_text() else "Unknown"

def extract_items_and_exhibits(soup, base_url):
    items = {}
    exhibit_data = []
    # lines = soup.get_text("\n").split("\n")

    item_pattern = re.compile(r'ITEM\s*(\d+\.\d+)\.*\s*(.*?)\.', re.IGNORECASE)
    # item_pattern =  re.compile(r'ITEM\s*(\d+\.\d+)', re.IGNORECASE)

    all_text = soup.get_text(separator=' ')
    print('\nitem_pattern',item_pattern)
    print('\nall_text',all_text)
    for match in item_pattern.finditer(all_text):
        item_id = match.group(1).strip()
        item_name = match.group(2).strip()
        items[item_id] = item_name

    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                exhibit_number = cells[0].get_text(strip=True)
                exhibit_description = cells[1].get_text(strip=True)

                link_tag = cells[1].find('a', href=True)
                exhibit_link = None
                if link_tag:
                    relative_url = link_tag['href'].strip()
                    if not relative_url.startswith('#'):
                        exhibit_link = urljoin(base_url, relative_url)

                exhibit_data.append({
                    'exhibit_number': exhibit_number,
                    'exhibit_title': exhibit_description,
                    'exhibit_link': exhibit_link
                })

    chunks = split_into_chunks(all_text)
    return {
        'items': items,
        'exhibit_data': exhibit_data,
        'chunks': chunks
    }

# Process each URL
def process_filing_url(filing_url,date,form_type ,cik ,company_name):
    print('\nkkkkk',filing_url,date,form_type ,cik ,company_name)
    soup = fetch_and_parse_url(filing_url)
    if not soup:
        print(f"Failed to fetch {filing_url}, skipping.")
        return []

    base_url = get_base_url(filing_url)
    filing_type = form_type
    date_of_report = date

    data = extract_items_and_exhibits(soup, base_url)
    document_rows = []

    for chunk in data['chunks']:
        document_rows.append({
            'url': filing_url,
            'cik':cik,
            'filing_type': filing_type,
            'date_of_report': date_of_report,
            'company_name': company_name,  # You can make this dynamic if needed
            'chunk_type': 'main file',
            'exhibit_number': None,
            'exhibit_link': None,
            'exhibit_title': None,
            'items': json.dumps(data['items'], ensure_ascii=False),
            'content': chunk
        })

    for exhibit in data['exhibit_data']:
        if not exhibit['exhibit_link']:
            continue

        exhibit_soup = fetch_and_parse_url(exhibit['exhibit_link'])
        if not exhibit_soup:
            continue

        exhibit_text = exhibit_soup.get_text(separator=' ')
        exhibit_chunks = split_into_chunks(exhibit_text)

        for chunk in exhibit_chunks:
            document_rows.append({
                'url': filing_url,
                'cik':cik,
                'filing_type': filing_type,
                'date_of_report': date_of_report,
                'company_name': company_name,
                'chunk_type': 'exhibit file',
                'exhibit_number': exhibit['exhibit_number'],
                'exhibit_link': exhibit['exhibit_link'],
                'exhibit_title': exhibit['exhibit_title'],
                'items': json.dumps(data['items'], ensure_ascii=False),
                'content': chunk
            })

    return document_rows

# Main Execution
def get_document(cik_data):
    all_documents = []

    for data in cik_data:
        url=data['url']
        print(f"Processing URL: {url}")
        date=data['date']
        form_type=data['form_type']
        cik=data['cik']
        accession_number=data['accession_number']
        company_name=data['company_name']
        document_rows = process_filing_url(url,date,form_type ,cik,company_name)
        all_documents.extend(document_rows)

    # CSV Write Section
    csv_columns = [
        'url',
        'cik',
        'filing_type',
        'date_of_report',
        'company_name',
        'chunk_type',
        'exhibit_number',
        'exhibit_link',
        'exhibit_title',
        'items',
        'content'
    ]

    with open('sec_8k_chunks_1.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerows(all_documents)

    print(f"✅ Data saved to 'sec_8k_chunks.csv'")

# if __name__ == "__main__":
#     main()
