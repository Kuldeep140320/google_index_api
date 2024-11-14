import pandas as pd
import re
from rapidfuzz import process, fuzz
from tqdm import tqdm
import multiprocessing as mp

def clean_company_names(names, keywords_to_remove=None):
    if keywords_to_remove is None:
        keywords_to_remove = ['Ltd', 'Ltd.', 'Inc', 'Inc.', 'Limited', 'Plc', 'Corporation', 'Corp', 'Co', 'Technologies']
    
    pattern = re.compile(r'\b(?:{})\b'.format('|'.join(map(re.escape, keywords_to_remove))))
    return [pattern.sub('', name).strip().lower() for name in names]

def process_chunk(args):
    chunk, all_cleaned_names, all_names, all_ids, threshold = args
    results = []
    for i, row in chunk.iterrows():
        if not row['grouped']:
            matches = process.extract(row['cleaned_name'], all_cleaned_names, 
                                      limit=None, scorer=fuzz.ratio, score_cutoff=threshold)
            group = [(row['name'], row['id'])]
            for match in matches:
                j = match[2]  # Index of the matched name
                if j != i:
                    group.append((all_names[j], all_ids[j]))
            results.append(group)
    return results

def group_similar_companies(df, threshold=96, chunk_size=1000):
    df['grouped'] = False
    all_cleaned_names = df['cleaned_name'].tolist()
    all_names = df['name'].tolist()
    all_ids = df['id'].tolist()

    chunks = [df[i:i+chunk_size] for i in range(0, len(df), chunk_size)]
    
    with mp.Pool(mp.cpu_count()) as pool:
        results = list(tqdm(pool.imap(process_chunk, 
                                      [(chunk, all_cleaned_names, all_names, all_ids, threshold) for chunk in chunks]), 
                            total=len(chunks)))
    
    grouped_companies = [item for sublist in results for item in sublist]
    
    final_results = []
    for group in grouped_companies:
        result_dict = {}
        for idx, (name, id_) in enumerate(group, 1):
            result_dict[f'Name_{idx}'] = name
            result_dict[f'ID_{idx}'] = id_
        final_results.append(result_dict)
    
    return final_results

def main():
    # Read the CSV file
    df = pd.read_csv(r"C:\Users\suppo\Downloads\data_guide_urls1.csv", encoding='cp1252', on_bad_lines='skip')

    # Clean company names
    df['cleaned_name'] = clean_company_names(df['name'])
    print("Company names are cleaned")

    # Group similar companies
    grouped_companies = group_similar_companies(df)

    # Convert the list of dictionaries into a DataFrame
    output_df = pd.DataFrame(grouped_companies)

    # Save the results to a CSV file
    output_df.to_csv('grouped_similar_companies_optimized.csv', index=False)

    print("The similar companies have been grouped and saved to 'grouped_similar_companies_optimized.csv'")

if __name__ == "__main__":
    main()