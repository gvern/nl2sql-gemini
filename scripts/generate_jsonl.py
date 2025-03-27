import os
import json
import pandas as pd
import argparse
from typing import List, Dict, Any
from google.cloud import bigquery, storage
from langchain_core.globals import set_verbose, set_debug
from src.prompts.utils import get_prompt
from config.settings import (
    PROJECT_ID,
    DATASET_ID,
    BQ_LOGS_TABLE,
    GCS_BUCKET_URI,
    FINETUNE_PATH,
    FIELDS_TO_IGNORE,
    FIELDS_TO_ENHANCE
)

# === Désactive logs LangChain ===
set_verbose(False)
set_debug(False)

# === Fonctions utilitaires ===

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
                    desc += " (Format: JJ/MM/AAAA. Utilisez PARSE_DATE('%d/%m/%Y', DATE_TICKET))."
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

def score_sql_complexity(sql: str) -> int:
    """
    Attribue un score de complexité à une requête SQL.
    """
    if not sql or not isinstance(sql, str):
        return 0
    sql_lower = sql.lower()
    score = 0
    score += sql_lower.count("join") * 3
    score += sql_lower.count("with") * 2
    score += sql_lower.count("group by") * 2
    score += sql_lower.count("order by")
    score += sql_lower.count("union") * 2
    score += sql_lower.count("case when") * 2
    score += sql_lower.count("having")
    score += sql_lower.count("select") * 0.5
    score += len(set(sql_lower.split())) / 50
    return int(score)

def create_finetuning_jsonl(top_n: int = None, filter_complexity: str = None, append: bool = False):
    schemas = get_table_schemas(PROJECT_ID, DATASET_ID, FIELDS_TO_IGNORE)
    enhanced = enhance_schema_with_values(PROJECT_ID, DATASET_ID, schemas, FIELDS_TO_ENHANCE)
    schema_str = format_schema_for_prompt(enhanced)
    logs_df = get_logs_dataframe(BQ_LOGS_TABLE)

    # Ajout du score de complexité
    logs_df["complexity_score"] = logs_df["query"].apply(score_sql_complexity)

    if filter_complexity:
        if filter_complexity == "simple":
            logs_df = logs_df[logs_df["complexity_score"] < 5]
        elif filter_complexity == "medium":
            logs_df = logs_df[(logs_df["complexity_score"] >= 5) & (logs_df["complexity_score"] < 10)]
        elif filter_complexity == "advanced":
            logs_df = logs_df[logs_df["complexity_score"] >= 10]
        print(f"🎯 Filtrage par complexité : {filter_complexity} ({len(logs_df)} exemples)")

    logs_df = logs_df.sort_values(by="complexity_score", ascending=False)

    if top_n:
        logs_df = logs_df.head(top_n)
        print(f"⚙️ Sélection des {top_n} requêtes les plus complexes")

    os.makedirs(os.path.dirname(FINETUNE_PATH), exist_ok=True)

    existing = []
    if append and os.path.exists(args.output):
        with open(args.output, "r", encoding="utf-8") as f:
            existing = f.readlines()
        print(f"➕ Mode append : {len(existing)} exemples existants chargés")

    with open(args.output, "w", encoding="utf-8") as f:
        for line in existing:
            f.write(line)
        for _, row in logs_df.iterrows():
            question, query = row["original_question"], row["query"]
            instruction = f"{get_prompt('v2').strip()}\n\n📚 Schéma de la base de données :\n{schema_str}"
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

    print(f"✅ JSONL généré : {FINETUNE_PATH}")

    if GCS_BUCKET_URI:
        bucket_name = GCS_BUCKET_URI.split("//")[1].split("/")[0]
        rel_path = FINETUNE_PATH if not GCS_BUCKET_URI.endswith("/") else FINETUNE_PATH[len("Finetuning_dataset/"):]
        blob_path = f"{GCS_BUCKET_URI.split(bucket_name+'/')[1]}{rel_path}"
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(FINETUNE_PATH)
        print(f"✅ Fichier uploadé vers GCS : gs://{bucket_name}/{blob_path}")

# === Script d’exécution CLI ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default=FINETUNE_PATH)
    parser.add_argument("--top_n", type=int, default=None, help="Nombre d'exemples complexes à inclure")
    parser.add_argument("--filter_complexity", type=str, choices=["simple", "medium", "advanced"], help="Filtrer par complexité SQL")
    parser.add_argument("--append", action="store_true", help="Ajouter les exemples sans écraser le fichier existant")
    args = parser.parse_args()

    create_finetuning_jsonl(
        top_n=args.top_n,
        filter_complexity=args.filter_complexity,
        append=args.append
    )
