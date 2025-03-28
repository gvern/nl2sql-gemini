# src/security/safety_checks.py

import re
from config.settings import PROJECT_ID, BQ_LOCATION
from google.cloud import bigquery
from google import genai

SQL_DANGEROUS_KEYWORDS = ["DROP", "DELETE", "ALTER", "TRUNCATE", "UPDATE", "INSERT"]

def validate_input(text):
    return bool(text and len(text.strip()) >= 3)

x

def execute_sql(query: str):
    """
    Exécute une requête SQL sur BigQuery pour vérifier sa validité.

    Returns:
        (bool, pd.DataFrame | None): True si la requête s'exécute sans erreur.
    """
    try:
        client = bigquery.Client(project=PROJECT_ID, location=BQ_LOCATION)
        result = client.query(query).result().to_dataframe()
        return True, result
    except Exception as e:
        return False, None

def evaluate_judge(question: str, reference_sql: str, predicted_sql: str) -> float:
    """
    Utilise Gemini (base) pour juger la similarité sémantique entre deux requêtes SQL pour une question donnée.

    Returns:
        float: score de similarité entre 0.0 et 2.0
    """
    try:
        client = genai.Client()
        content = [
            {"role": "user", "parts": [{
                "text": f"""Tu es un assistant qui évalue la similarité entre deux requêtes SQL.

Question : {question}

Référence SQL :
{reference_sql}

SQL générée :
{predicted_sql}

Donne une note entre 0 et 2 :
- 2 = mêmes résultats
- 1 = partiellement correct
- 0 = incorrect

Ta réponse :"""
            }]}
        ]
        response = client.generate_content(content)
        score = float(response.text.strip())
        return max(0.0, min(score, 2.0))
    except Exception:
        return 0.0
