from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import json
import sys
import pandas as pd

# https://developers.google.com/search/apis/indexing-api/v3/prereqs#header_2
JSON_KEY_FILE = r"avathi-327311-5e77d44d5b03.json"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
http = credentials.authorize(httplib2.Http())

def indexURL(urls, http):
    # print(type(url)); print("URL: {}".format(url));return;

    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    
    for u in urls:
        # print("U: {} type: {}".format(u, type(u)))
    
        content = {}
        content['url'] = u.strip()
        content['type'] = "URL_UPDATED"
        json_ctn = json.dumps(content)    
        # print(json_ctn);return
    
        response, content = http.request(ENDPOINT, method="POST", body=json_ctn)

        result = json.loads(content.decode())

        # For debug purpose only
        if("error" in result):
            print("Error({} - {}): {}".format(result["error"]["code"], result["error"]["status"], result["error"]["message"]))
        else:
            if 'urlNotificationMetadata' in result:
                print("Success: URL successfully submitted for indexing.")
                print(f"Submitted URL: {result['urlNotificationMetadata'].get('url', 'N/A')}")
                if 'latestUpdate' in result['urlNotificationMetadata']:
                    latest_update = result['urlNotificationMetadata']['latestUpdate']
                    print(f"Update type: {latest_update.get('type', 'N/A')}")
                    print(f"Notification time: {latest_update.get('notifyTime', 'N/A')}")
                else:
                    print("Note: No 'latestUpdate' information available in the response.")
            else:
                print("Warning: URL submitted, but no metadata received in the response.")
            
        print(f"Full API response: {json.dumps(result, indent=2)}")
"""
data.csv has 2 columns: URL and date.
I just need the URL column.
"""
# csv = pd.read_csv(r"data.csv")

# original_csv = pd.read_csv(r"data.csv")
# new_csv = pd.read_csv(r"Table 1.csv")
# # new row=new_csv-csv
# deduplicated_csv = new_csv[~new_csv['URL'].isin(original_csv['URL'])]
# deduplicated_csv.to_csv("Deduplicated_Table.csv", index=False)
csv = pd.read_csv(r"url_list.csv")  
# csv = pd.read_csv(r"Deduplicated_Table.csv")


csv_data=csv.iloc[1300:1500]

 
# print(csv_data)
# sys.exit()
 
csv_data[["URL"]].apply(lambda x: indexURL(x, http))