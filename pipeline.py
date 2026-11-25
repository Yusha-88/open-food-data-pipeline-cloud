import pandas as pd
import pandas_gbq
from urllib.error import HTTPError
import urllib3
from tqdm import tqdm 
import sys 
import requests
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PROJECT_ID = "open-food-bgq"
DATASET_ID = "open_food"
TABLE_ID = "open_food_table"
TABLE_NAME = f"{DATASET_ID}.{TABLE_ID}"

SERVICE_ACCOUNT = "service_account.json"

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT)

url = 'https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz'

# Original CSV has 155 columns. Below are the most relevant. 
relevant_cols = [
    "product_name",
    "generic_name",
    "brands",
    "origins",
    "countries",
    "allergens",
    "nutriscore_score",
    "nutriscore_grade",
    "brand_owner",
    "environmental_score_score",
    "environmental_score_grade",
    "energy-kcal_100g",
    "energy_100g",
    "fat_100g",
    "saturated-fat_100g",
    "trans-fat_100g",
    "cholesterol_100g",
    "carbohydrates_100g",
    "sugars_100g",
    "added-sugars_100g",
    "fiber_100g",
    "proteins_100g",
    "salt_100g",
    "added-salt_100g"
] 

# Used to load_df function to coerce non-float values to NaN or null
numeric_cols = [
    "nutriscore_score",
    "environmental_score_score",
    "energy-kcal_100g",
    "energy_100g",
    "fat_100g",
    "saturated-fat_100g",
    "trans-fat_100g",
    "cholesterol_100g",
    "carbohydrates_100g",
    "sugars_100g",
    "added-sugars_100g",
    "fiber_100g",
    "proteins_100g",
    "salt_100g",
    "added-salt_100g"
]

# Ensure download url is working
def check_url_response(url):
    logging.info("Checking URL...")
    http = urllib3.PoolManager()
    url_working = True

    response = http.request("HEAD",url)

    if 400 <= response.status < 600:
        url_working = False
    else:
        logging.info(f"HTTP Status: {response.status}")

    return url_working

# Optional function to use to check if source CSV schema has changed. Useful when running this code after a long inactive use period. 
def check_headers(column_list, url):
    invalid_columns = False
    logging.info("Checking headers...")
    try:       
        df = pd.read_csv(url, sep='\t', nrows=1)
        header_list = df.columns.tolist()
    except HTTPError as err:
        print(f"HTTP Error: {err}. Please check URL link.")
        exit()
    for column in column_list:
        if column not in header_list:
            print(f"{column} not found in file's headers.")
            invalid_columns = True
        else:
            pass
    if invalid_columns:
        print("Please double-check the column names in the original CSV.")
        exit()
    return None

# Extraction and transformation
def extract_transform_csv(url, nrows=None):
    logging.info("Starting download...")     
    df_iter = pd.read_csv(
        url, 
        sep='\t',
        nrows=nrows,
        usecols=relevant_cols,
        iterator=True,
        low_memory=False,
        chunksize=500000
        )
    return df_iter

# Load open food df into Google BigQuery.
def load_df_to_database(Dataframe):
    total_rows = 0
    logging.info("Uploading to BigQuery...")
    for df_chunk in Dataframe:    
        total_rows += len(df_chunk)
        # Forces non-float values in float columns to NaN/null.
        for col in numeric_cols:
            df_chunk[col] = pd.to_numeric(df_chunk[col], errors = "coerce")
        pandas_gbq.to_gbq(
            df_chunk, 
            TABLE_NAME, 
            project_id=PROJECT_ID, 
            credentials=credentials, 
            progress_bar=True, 
            if_exists='append'
            )  
    logging.info(f"load_df finished. Number of rows uploaded: {total_rows}")

def main():
    # num_rows_to_extract = 1000000
    # check_headers(relevant_cols, url) 

    if check_url_response(url):
        logging.info("URL okay. Downloading CSV...")
    else:
        logging.critical("Open Food Facts URL not responding. Shutting down pipeline.")
        sys.exit()   

    open_food_df = extract_transform_csv(url)
    logging.info("Finished extract and transform")

    load_df_to_database(open_food_df)
    logging.info("Finished")

if __name__ == "__main__":
    main()

