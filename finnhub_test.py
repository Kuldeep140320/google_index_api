import finnhub



import requests
import json

# url = "https://finnhub.io/api/v1/global-filings/search?token=csu5su1r01qour3sp3ggcsu5su1r01qour3sp3h0"

# payload = json.dumps({
#   "query": "artificial intelligence",
#   "symbols": "AAPL,GOOGL,TSLA",
#   "fromDate": "2010-01-01",
#   "toDate": "2022-09-30"
# })


# response = requests.request("POST", url, data=payload)

# print(response.json())

# Initialize client
finnhub_client = finnhub.Client(api_key="csu5su1r01qour3sp3ggcsu5su1r01qour3sp3h0")
print(finnhub_client.fda_calendar())
# # Fetch SEDAR filings for the given company symbol
# filings = finnhub_client.international_filings(symbol='AC.TO', country='CA')

# # Print the filings
# print(filings)
