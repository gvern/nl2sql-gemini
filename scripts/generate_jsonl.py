import os
import json
import time
import pandas as pd
from typing import List, Dict, Any
from google.cloud import bigquery, storage
from langchain_core.globals import set_verbose, set_debug
from config.settings import (
    PROJECT_ID,
    DATASET_ID,
    BQ_LOGS_TABLE,
    GCS_BUCKET_URI,
    FINETUNE_PATH,
    TRAINING_DATA_URI,
    VALIDATION_DATA_URI,
    FIELDS_TO_IGNORE,
    FIELDS_TO_ENHANCE,
    SYSTEM_INSTRUCTION
)


# Désactive logs LangChain
set_verbose(False)
set_debug(False)


# === Fonctions ===

def get_table_schemas(project_id, dataset_id, fields_to_ignore) -> Dict[str, Dict[str, Any]]:
    client = bigquery.Client(project=project_id)
    schemas = {}
    for table in client.list_tables(dataset_id):
        table_obj = client.get_table(table)
        fields = []
        for field in table_obj.schema:
            if field.name not in fields_to_ignore:
                desc = field.description or ""
                if field.name == "DATE_TICKET":
                    desc += " (Format: JJ/MM/AAAA. Utilisez PARSE_DATE('%d/%m/%Y', DATE_TICKET) pour les opérations de date)."
                fields.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": desc
                })
        schemas[table.table_id] = {
            "fields": fields,
            "description": table_obj.description or ""
        }
    return schemas

def get_distinct_values(client, project_id, dataset_id, table, column) -> list:
    query = f"""
        SELECT DISTINCT {column}
        FROM `{project_id}.{dataset_id}.{table}`
        ORDER BY {column}
        LIMIT 150
    """
    return [row[column] for row in client.query(query).result()]

def enhance_schema_with_values(project_id, dataset_id, schemas, fields_to_enhance):
    client = bigquery.Client(project=project_id)
    for table, columns in fields_to_enhance.items():
        for col in columns:
            values = get_distinct_values(client, project_id, dataset_id, table, col)
            for field in schemas[table]["fields"]:
                if field["name"] == col:
                    val_str = ', '.join(f'"{v}"' for v in values)
                    field["description"] += f" Available values: {val_str}"
    return schemas

def format_schema_for_prompt(schemas: Dict[str, Any]) -> str:
    formatted = []
    for table_name, info in schemas.items():
        table_data = {
            "table": table_name,
            "columns": info["fields"]
        }
        if info.get("description"):
            table_data["description"] = info["description"]
        formatted.append(table_data)
    return json.dumps(formatted, ensure_ascii=False, indent=2)

def get_logs_dataframe(bq_logs_table_name: str) -> pd.DataFrame:
    client = bigquery.Client()
    query = f"""
        SELECT DISTINCT original_question, query
        FROM `{bq_logs_table_name}`
        WHERE approved = TRUE AND scope = 'RDM'
    """
    return client.query(query).result().to_dataframe()

def create_finetuning_jsonl():
    schemas = get_table_schemas(project_id, dataset_id, fields_to_ignore)
    enhanced = enhance_schema_with_values(project_id, dataset_id, schemas, fields_to_enhance)
    schema_str = format_schema_for_prompt(enhanced)
    logs_df = get_logs_dataframe(bq_logs_table_name)

    os.makedirs(os.path.dirname(output_jsonl_path), exist_ok=True)
    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        for _, row in logs_df.iterrows():
            question, query = row["original_question"], row["query"]
            instruction = f"{system_instruction.strip()}\n\nSchéma de la base de données :\n{schema_str}"
            example = {
                "systemInstruction": {
                    "role": "user",
                    "parts": [{"text": instruction}]
                },
                "contents": [
                    {"role": "user", "parts": [{"text": question}]},
                    {"role": "model", "parts": [{"text": query}]}
                ]
            }
            json.dump(example, f, ensure_ascii=False)
            f.write("\n")
    print(f"✅ JSONL généré : {output_jsonl_path}")

    if gcs_bucket_uri:
        bucket_name = gcs_bucket_uri.split("//")[1].split("/")[0]
        rel_path = output_jsonl_path if not gcs_bucket_uri.endswith("/") else output_jsonl_path[len("Finetuning_dataset/"):]
        blob_path = f"{gcs_bucket_uri.split(bucket_name+'/')[1]}{rel_path}"
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(output_jsonl_path)
        print(f"✅ Fichier uploadé vers GCS : gs://{bucket_name}/{blob_path}")

# === Lancement ===
if __name__ == "__main__":
    create_finetuning_jsonl()
