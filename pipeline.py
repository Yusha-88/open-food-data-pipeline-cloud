import pandas as pd
import pandas_gbq 
from google.oauth2 import service_account

PROJECT_ID = "open-food-bgq"
DATASET_ID = "open_food"
TABLE_ID = "open_food_table"
TABLE_NAME = f"{DATASET_ID}.{TABLE_ID}"

SERVICE_ACCOUNT = "service_account.json"

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT)

url = 'https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz'

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

# Extraction and transformation
def extract_transform_csv(url, nrows=None):
    print("Starting...")       
    df_iter = pd.read_csv(
        url, 
        sep='\t',
        nrows=nrows,
        usecols=relevant_cols,
        iterator=True,
        low_memory=False,
        chunksize=100000
        )
    return df_iter
    

# Load open food df into Google BigQuery.
def load_df_to_database(Dataframe):
    print("load_df running...")
    for df_chunk in Dataframe:
        try:
            pandas_gbq.to_gbq(
                df_chunk, 
                TABLE_NAME, 
                project_id=PROJECT_ID, 
                credentials=credentials, 
                progress_bar=True, 
                if_exists='append'
                )  
        except pandas_gbq.exceptions.ConversionError:
            pass
    print("load_df finished")

def main():
    num_rows_to_extract = 1000000  
    open_food_df = extract_transform_csv(url)
    print("Finished extract and transform")
    load_df_to_database(open_food_df)
    print("Finished")

    # open_food_df.to_csv('output.csv', index=False)

if __name__ == "__main__":
    main()

