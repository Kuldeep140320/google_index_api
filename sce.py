# from weasyprint import HTML
import csv ,sys
import json
from typing import List
from datetime import datetime
import requests
from pydantic import BaseModel
from pyppeteer import launch
from filing import get_document
data_to_csv = []


class FormIndex(BaseModel):
    form_type: str  # e.g. 10-K, 10-Q, 8-K, etc.
    index: int  # index of the form in the list


def fetch_company_submissions(cik: str):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        print(response.text)
        response.raise_for_status()

    try:
        print('dfdf:' ,url)
        return response.json()
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print("Response content:")
        print(response.text)
        raise


def parse_filings(submissions_json):
    # print('submissions_json',submissions_json)
    filings = submissions_json.get("filings", {})
    recent_filings = filings.get("recent", {})
    forms = recent_filings.get("form", [])
    accession_numbers = recent_filings.get("accessionNumber", [])
    report_dates = recent_filings.get("reportDate", [])
    primary_document_paths = recent_filings.get("primaryDocument", [])
    form_indices: List[FormIndex] = []
    for index, form in enumerate(forms):
        if form in ["8-K"]:
            form_indices.append(FormIndex(form_type=form, index=index))
    return form_indices, accession_numbers, report_dates, primary_document_paths


def create_filing_urls(cik, company_name, form_indices, accession_numbers, report_dates, primary_document_paths):
    data=[]
    cutoff_date = datetime(2024, 2, 1)  # January 1, 2023
    base_url = "https://www.sec.gov/Archives/edgar/data/"
    for form_index in form_indices:
        index = form_index.index
        form = form_index.form_type
        accession_number = accession_numbers[index]
        report_date = report_dates[index]
        primary_document_path = primary_document_paths[index]

        url = f"{base_url}{cik}/{accession_number.replace('-', '')}/{primary_document_path}"
        try:
            report_date_obj = datetime.strptime(report_date, "%Y-%m-%d")
        except ValueError:
            print(f"Skipping invalid date format: {report_date}")
            continue
        if url != "https://www.sec.gov/Archives/edgar/data/0001018724/000110465924061143/tm2414460d1_8k.htm":
            continue
        if report_date_obj <= cutoff_date:
            continue
        data.append({
                'url':url,
                'date':report_date,
                'form_type':form,
                'cik':cik,
                'accession_number':accession_number,
                'company_name':company_name

            })
    # print('data',data)
    # res=get_document(data)
    # print('res',res)
    return data

def import_to_csv(data_to_csv, output_file):
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data_to_csv)


async def main(url, output_file):
    browser = await launch({"headless": False})
    page = await browser.newPage()
    await page.goto(url)
    await page.screenshot({'path': output_file, 'fullPage': True})

    dimensions = await page.evaluate('''() => {
        return {
            width: document.documentElement.clientWidth,
            height: document.documentElement.clientHeight,
            deviceScaleFactor: window.devicePixelRatio,
        }
    }''')

    print(dimensions)
    # >>> {'width': 800, 'height': 600, 'deviceScaleFactor': 1}
    await browser.close()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Fetch and display SEC filings for a given CIK.')
    # parser.add_argument('cik', type=str, help='CIK of the company to fetch filings for')
    # parser.add_argument('cname', type=str, help='company name of the company to fetch filings for')
    # args = parser.parse_args()

    try:
        # submissions_json = fetch_company_submissions(args.cik)
        # form_indices, accession_numbers, report_dates, primary_document_paths = parse_filings(submissions_json)
        # create_filing_urls(args.cik, args.cname, form_indices, accession_numbers, report_dates, primary_document_paths)
        data_to_fetch = [
            {"cik": "0001018724", "cname": "amazon"},
            {"cik": "0001559720", "cname": "airbnb"},
            {"cik": "0000789019", "cname": "msft"},
            {"cik": "0001543151", "cname": "uber"},
            {"cik": "0000320193", "cname": "apple"},
            {"cik": "0001318605", "cname": "tesla"}
        ]
        res=[]
        for d in data_to_fetch:
            print(d)
            cik = d["cik"]
            cname = d["cname"]
            submissions_json = fetch_company_submissions(cik)
            print('hiii')
            form_indices, accession_numbers, report_dates, primary_document_paths = parse_filings(submissions_json)

            # print('form_indices, accession_numbers, report_dates, primary_document_paths',form_indices, accession_numbers, report_dates, primary_document_paths)
            res_data=create_filing_urls(cik, cname, form_indices, accession_numbers, report_dates,
                               primary_document_paths)
            res.extend(res_data)
        resss=get_document(res)
        print('\nres',resss)
    except Exception as e:
        print(f"An error occurred: {e}")
