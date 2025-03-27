from google.cloud import bigquery
from config.settings import PROJECT_ID, DATASET_ID
from functools import lru_cache


bq_client = bigquery.Client(project=PROJECT_ID)
@lru_cache()

def extract_formatted_schema_for_prompt(project_id=PROJECT_ID, dataset_id=DATASET_ID):
    """
    Extrait le schéma des tables d'un dataset BigQuery et le formate pour l'injection dans un prompt LLM.
    """
    formatted_schema = []
    try:
        tables = bq_client.list_tables(dataset_id)
        for table in tables:
            full_table_id = f"{project_id}.{dataset_id}.{table.table_id}"
            table_obj = bq_client.get_table(full_table_id)
            fields = [f"{field.name} ({field.field_type})" for field in table_obj.schema]
            formatted_schema.append(f"- {full_table_id} :\n    " + "\n    ".join(fields))
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction du schéma : {e}")
    return "\n".join(formatted_schema)

if __name__ == "__main__":
    print(extract_formatted_schema_for_prompt())
