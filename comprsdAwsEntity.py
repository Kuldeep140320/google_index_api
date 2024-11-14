import boto3
import requests
import time
import pandas as pd
import re ,sys


session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

# Initialize the Comprehend client from the session
comprehend = session.client('comprehend')
def extract_entities_single(description):
    try:
        response = comprehend.detect_entities(Text=description, LanguageCode='en')
        companies_in_text = [entity['Text'] for entity in response['Entities'] if entity['Type'] == 'ORGANIZATION']
        return clean_company_names(companies_in_text)
    except Exception as e:
        print(f"Error during entity extraction: {e}")
        return []

# Function to clean and filter out invalid company names
def clean_company_names(companies):
    companies = list(set(companies))
    valid_companies = [company for company in companies if len(company) > 3 and not re.search(r'[^\w\s]', company)]
    return valid_companies

# Function to clean the DataFrame by removing unnecessary columns and extracting URLs
def clean_csv(input_csv):
    # Load the CSV file
    df = pd.read_csv(input_csv)
    
    # Drop unnecessary 'Unnamed' columns (they are likely empty or redundant)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Drop rows with all NaN values
    df.dropna(how='all', inplace=True)
    
    return df

# Function to process the cleaned CSV and add company names
def add_companies_to_csv(input_csv, output_csv):
    # Clean the CSV and get relevant columns
    df = clean_csv(input_csv)
    df=df.loc[0:100]
    # Create an empty list to store extracted companies
    company_list = []

    # Iterate over each row
    for index, row in df.iterrows():
        description = row['content']  # Assuming the relevant text is in the 'source' column
        
        # Extract company names from the description (URL in this case)
        companies = extract_entities_single(description)
        # print(companies)
        # sys.exit()
        # Add the companies to the list (semicolon-separated)
        company_list.append('; '.join(companies))

        # Log progress every 10 rows
        if (index + 1) % 10 == 0:
            print(f"Processed row {index+1}/{len(df)}")

        # Avoid hitting API rate limits
        time.sleep(0.5)

    # Add the company names to a new column in the DataFrame
    df['companies'] = company_list

    # Save the updated DataFrame to the output CSV
    df.to_csv(output_csv, index=False)

# Example usage
input_csv = r"C:\Users\suppo\Downloads\On_demand_report.csv"  # Replace with your input CSV file path
output_csv = r"C:\Users\suppo\Downloads\On_demand_report_output.csv"  # Replace with your output CSV file path

# Add companies to CSV
add_companies_to_csv(input_csv, output_csv)

print(f"Updated CSV saved as {output_csv}")