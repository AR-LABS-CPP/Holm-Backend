import os
import pymongo
from dotenv import load_dotenv
from . import data_preparation
from . import utils

load_dotenv()

parquet_files = []
hf_read_token = os.environ["HUGGING_FACE_API_KEY"]
  
def ingest_data(mongo_uri):
  db_name = "medical_data"
  collection_name = "medical_data_collection"

  mongo_client = utils.get_mongo_client(mongo_uri)
  
  db = mongo_client[db_name]
  collection = db[collection_name]

  # Delete any previous data so that we start fresh
  collection.delete_many({})

  # Data Ingestion (In Batches)
  batch_size = 1000
  
  combined_dataset = data_preparation.download_and_combine_parquet_files(parquet_files, hf_read_token)

  # Remove the id column from the initial dataset
  combined_dataset = combined_dataset.drop(columns=["id"])

  combined_df_json = combined_dataset.to_dict(orient="records")

  # Data Ingestion (In Batches)
  batch_size = 1000
  combined_df_json = combined_dataset.to_dict(orient="records")

  batches = [combined_df_json[idx:idx+batch_size] for idx in range(0, len(combined_df_json), batch_size)]

  import time

  # Insert batches with delay (to avoid getting our connection overload or closed)
  for batch in batches:
    collection.insert_many(batch)
    print("Sleeping for 2 seconds before inserting another batch")
    time.sleep(2)