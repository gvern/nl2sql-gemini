import pandas as pd
from tqdm import tqdm
from src.inference.predict import generate_ft_sql, generate_base_sql
from src.security.safety_checks import execute_sql, evaluate_judge
from google.cloud import bigquery
from config.settings import PROJECT_ID

bq_client = bigquery.Client(project=PROJECT_ID)

def evaluate_model():
    query = f"""
        SELECT DISTINCT original_question, query 
        FROM `{PROJECT_ID}.working.logs` 
        WHERE approved = TRUE AND scope = 'RDM'
    """
    validation_data = bq_client.query(query).result().to_dataframe()
    
    results = []
    for _, row in tqdm(validation_data.iterrows(), total=len(validation_data), desc="📐 Évaluation des modèles"):
        question = row['original_question']
        expected_sql = row['query']

        base_sql = generate_base_sql(question)
        ft_sql = generate_ft_sql(question)

        base_exec, _ = execute_sql(base_sql) if base_sql else (False, None)
        ft_exec, _ = execute_sql(ft_sql) if ft_sql else (False, None)

        results.append({
            "question": question,
            "expected_sql": expected_sql,
            "base_sql": base_sql,
            "ft_sql": ft_sql,
            "base_semantic": evaluate_judge(question, expected_sql, base_sql or ""),
            "ft_semantic": evaluate_judge(question, expected_sql, ft_sql or ""),
            "base_exec": base_exec,
            "ft_exec": ft_exec,
        })
    
    return pd.DataFrame(results)
