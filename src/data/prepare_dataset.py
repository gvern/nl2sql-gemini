# src/data/prepare_dataset.py

import pandas as pd
import json
from src.schema.extract_schema import extract_formatted_schema_for_prompt
from src.config import PROJECT_ID, DATASET_ID
from google.cloud import bigquery

def prepare_jsonl_dataset(output_path):
    bq_client = bigquery.Client(project=PROJECT_ID)
    logs_query = f"""
        SELECT DISTINCT original_question, query 
        FROM `{PROJECT_ID}.working.logs`
        WHERE approved = TRUE AND scope = 'RDM'
    """
    df = bq_client.query(logs_query).result().to_dataframe()
    schema = extract_formatted_schema_for_prompt()

    with open(output_path, "w") as f:
        for _, row in df.iterrows():
            prompt = f"""\
Tu es un assistant de requête SQL spécialisé. Voici le schéma :

{schema}

Question : {row['original_question']}"""

            json.dump({
                "messages": [
                    {"role": "user", "content": prompt},
                    {"role": "model", "content": row["query"]}
                ]
            }, f)
            f.write("\n")
