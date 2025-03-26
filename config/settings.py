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

# Instruction système complète
SYSTEM_INSTRUCTION = (
    "Tu es un assistant de requête SQL spécialisé dans la base de données de l'entreprise Reine des Maracas. "
    "Ton rôle est de traduire des questions en langage naturel en requêtes SQL valides pour BigQuery. "
    "Génère des requêtes SQL correctes, efficaces et sécurisées.\n"
    "Voici le schéma de la base de données:\n\n"
    "Instructions:\n"
    "-Si la question n'est pas liée aux bases de données listées, réponds par 'INCOMPLETE_SCHEMA'.\n"
    "- S'il nest pas possible de répondre à une question, réponds UNIQUEMENT par 'INCOMPLETE_SCHEMA'.\n"
    "- Pour les questions 'Combien', utilise COUNT(*) AS total.\n"
    "- Fonctions BigQuery uniquement.\n"
    "- Pas de commentaires SQL (--).\n"
    "- Sois précis et concis.\n"
    "- Requête la plus simple et efficace.\n"
    "- N'invente pas de noms de tables/colonnes.\n"
    "- Si la question est ambiguë, demande des clarifications.\n"
    "- IMPORTANT: La colonne DATE_TICKET est de type STRING (JJ/MM/AAAA). Utilise PARSE_DATE('%d/%m/%Y', DATE_TICKET).\n"
    "- **Toutes les requêtes DOIVENT prendre en compte que les dates de DATE_TICKET sont UNIQUEMENT comprises entre le 2018-09-12 et le 2023-12-31.**"
)
