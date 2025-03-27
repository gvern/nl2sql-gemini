# Informations GCP
PROJECT_ID = "avisia-self-service-analytics"
PROJECT_NUMBER = "491780955535"
DATASET_ID = "reine_des_maracas"
VERTEX_LOCATION = "europe-west1"
BQ_LOCATION = "EU"
ENDPOINT_ID = "4130025158670811136"

# Buckets
BUCKET_ID = "self-service-analytics-bucket"
GCS_BUCKET_URI = f"gs://{BUCKET_ID}/data/"

# Tables BigQuery
BQ_LOGS_TABLE = f"{PROJECT_ID}.working.logs"

# Fichiers pour fine-tuning
FINETUNE_PATH = "Finetuning_dataset/finetuning_data.jsonl"
VALIDATION_PATH = "Finetuning_dataset/validation_dataset.jsonl"
TRAINING_DATA_URI = GCS_BUCKET_URI + FINETUNE_PATH
VALIDATION_DATA_URI = GCS_BUCKET_URI + VALIDATION_PATH

# Modèle source
SOURCE_MODEL = "gemini-2.0-flash-001"

# Colonnes à ignorer ou enrichir
FIELDS_TO_IGNORE = ["_dlt_id", "_dlt_load_id"]
FIELDS_TO_ENHANCE = {
    "magasin": ["VILLE", "REGIONS", "CENTRE_VILLE"],
    "complement_individu": ["SOUSSEG", "SEGACT"],
    "typo_produit": ["LIGNE", "FAMILLE"]
}

