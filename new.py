import pandas as pd
import sys

# -- 1. Read the data --
file_path = r"C:\Users\kulde\OneDrive\Desktop\google_index_api\google_index_api\December.xlsx"
df = pd.read_excel(file_path)

# Standardize column names if necessary
# Expect: 'date', 'menu_iteam', 'id'
df.columns = [col.strip().lower() for col in df.columns]

# Define your two dates (or months) to compare
date1 = '12/11/2024'
date2 = '11/13/2024'

# -- 2. Filter DataFrames by date --
df_date1 = df[df['date'] == date1].copy()
df_date2 = df[df['date'] == date2].copy()

# RENAME 'id' columns -> 'id_date1' / 'id_date2'
df_date1.rename(columns={'id': 'id_date1'}, inplace=True)
df_date2.rename(columns={'id': 'id_date2'}, inplace=True)

# -- 3. Identify unique items in each month --
menu_date1 = set(df_date1['menu_iteam'])
menu_date2 = set(df_date2['menu_iteam'])

unique_to_date1 = menu_date1 - menu_date2
unique_to_date2 = menu_date2 - menu_date1

# Create a DataFrame of unique items for date1
df_unique_date1 = df_date1[df_date1['menu_iteam'].isin(unique_to_date1)].copy()
# Create a DataFrame of unique items for date2
df_unique_date2 = df_date2[df_date2['menu_iteam'].isin(unique_to_date2)].copy()

# -- 4. Find items common to both dates and check if IDs differ --
common_items = menu_date1.intersection(menu_date2)

# Keep only relevant columns for merging
df_date1_merge = df_date1[['menu_iteam', 'id_date1']]
df_date2_merge = df_date2[['menu_iteam', 'id_date2']]

# Merge on 'menu_iteam' to compare IDs
df_merged = pd.merge(df_date1_merge, df_date2_merge, on='menu_iteam', how='inner')

# Filter where the IDs differ
df_id_mismatch = df_merged[df_merged['id_date1'] != df_merged['id_date2']].copy()

# -- 5. Prepare data for output (add date columns) --
# For unique date1 items, explicitly store the date
df_unique_date1['date'] = date1
# For unique date2 items, explicitly store the date
df_unique_date2['date'] = date2

# For the mismatched IDs, let's include both dates to be clear
df_id_mismatch['date1'] = date1
df_id_mismatch['date2'] = date2

# Optionally reorder columns for readability
df_unique_date1 = df_unique_date1[['date', 'menu_iteam', 'id_date1']]
df_unique_date1.rename(columns={'id_date1': 'id'}, inplace=True)

df_unique_date2 = df_unique_date2[['date', 'menu_iteam', 'id_date2']]
df_unique_date2.rename(columns={'id_date2': 'id'}, inplace=True)

df_id_mismatch = df_id_mismatch[['menu_iteam', 'id_date1', 'id_date2', 'date1', 'date2']]

# -- 6. Write results to Excel (3 sheets) --
output_file = r"C:\Users\kulde\OneDrive\Desktop\google_index_api\google_index_api\ComparisonOutput.xlsx"

with pd.ExcelWriter(output_file) as writer:
    df_unique_date1.to_excel(writer, sheet_name='Unique_to_Date1', index=False)
    df_unique_date2.to_excel(writer, sheet_name='Unique_to_Date2', index=False)
    df_id_mismatch.to_excel(writer, sheet_name='Mismatched_IDs', index=False)

print("Comparison complete. Results saved to:", output_file)
