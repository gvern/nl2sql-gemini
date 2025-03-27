import pandas as pd
from tqdm import tqdm
from src.inference.predict import generate_base_sql, generate_ft_sql
from src.security.safety_checks import execute_sql, sanitize_sql_output
from src.evaluation.plots import plot_results, plot_deltas, plot_scores_by_scope
from config.settings import PROJECT_ID, VERTEX_LOCATION
from google.cloud import bigquery
from vertexai import init as vertexai_init
from vertexai.generative_models import GenerativeModel, GenerationConfig, Content, Part
import re
import os

# Initialisation Vertex AI
vertexai_init(project=PROJECT_ID, location=VERTEX_LOCATION)

# Clients
bq_client = bigquery.Client(project=PROJECT_ID)
generation_config = GenerationConfig(temperature=0, max_output_tokens=512)
model_judge = GenerativeModel("gemini-pro")


def classify_scope(question: str) -> str:
    """Détermine si une question est en lien avec la base de données métier ou hors-scope."""
    prompt = f"""
    Tu dois dire si la question est liée à une base métier sur les ventes, clients, produits, tickets.

    Réponds uniquement par "in_scope" ou "out_of_scope".

    Exemples :
    Q: Quel est le chiffre d'affaires total ? → in_scope
    Q: Combien de tickets ont été émis en 2023 ? → in_scope
    Q: Quelle est la capitale de la France ? → out_of_scope
    Q: Que vaut π au carré ? → out_of_scope
    Q: Combien de clients fidèles en région PACA ? → in_scope

    Question : {question}
    """

    try:
        response = model_judge.generate_content(
            [Content(role="user", parts=[Part.from_text(prompt)])],
            generation_config=generation_config
        ).text.strip().lower()
        return "out_of_scope" if "out" in response else "in_scope"
    except:
        return "in_scope"


def evaluate_judge(question, expected_sql, predicted_sql):
    """Évalue la similarité sémantique entre la requête attendue et la prédite."""
    prompt = (
        "Évalue la similarité sémantique entre ces deux requêtes SQL pour la question donnée.\n"
        "Réponds uniquement par un chiffre : 0 (mauvais), 1 (acceptable) ou 2 (excellent).\n\n"
        f"Question: {question}\n"
        f"SQL attendu: {expected_sql}\n"
        f"SQL prédit: {predicted_sql}"
    )
    try:
        response = model_judge.generate_content(
            [Content(role="user", parts=[Part.from_text(prompt)])],
            generation_config=generation_config
        ).text.strip()
        match = re.search(r'\b([0-2])\b', response)
        print("🧪 Évaluation sémantique")
        print(f"Question : {question}")
        print(f"Référence SQL : {expected_sql}")
        print(f"SQL générée : {predicted_sql}")
        print(f"---")

        return int(match.group(1)) if match else 0
    except:
        return 0
    
# Calcul des refus corrects
def refusal_rate(df, model: str = "ft"):
    """
    Renvoie le pourcentage de refus corrects sur les out-of-scope.
    """
    out_df = df[df["scope"] == "out_of_scope"]
    refusals = (~out_df[f"{model}_safe"]).sum()
    total = len(out_df)
    return (refusals / total) * 100 if total > 0 else 0


def robust_evaluate():
    query = f"""
        SELECT DISTINCT original_question, query
        FROM `{PROJECT_ID}.working.logs`
        WHERE approved = TRUE AND scope = 'RDM'
    """
    df = bq_client.query(query).result().to_dataframe()

    results = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="🔐 Évaluation robuste"):
        question, expected_sql = row["original_question"], row["query"]
        scope = classify_scope(question)

        base_sql = generate_base_sql(question)
        ft_sql = generate_ft_sql(question)

        ft_is_safe, _ = sanitize_sql_output(ft_sql)
        base_is_safe, _ = sanitize_sql_output(base_sql)

        base_exec, _ = execute_sql(base_sql) if base_is_safe else (False, None)
        ft_exec, _ = execute_sql(ft_sql) if ft_is_safe else (False, None)

        results.append({
            "question": question,
            "expected_sql": expected_sql,
            "scope": scope,
            "base_sql": base_sql,
            "ft_sql": ft_sql,
            "base_safe": base_is_safe,
            "ft_safe": ft_is_safe,
            "base_exec": base_exec,
            "ft_exec": ft_exec,
            "base_semantic": evaluate_judge(question, expected_sql, base_sql or ""),
            "ft_semantic": evaluate_judge(question, expected_sql, ft_sql or ""),
        })

    df_result = pd.DataFrame(results)
    os.makedirs("evaluation", exist_ok=True)
    df_result.to_csv("evaluation/evaluation_robust.csv", index=False)
    print("✅ Fichier enregistré : evaluation/evaluation_robust.csv")

    in_scope = df_result[df_result["scope"] == "in_scope"]
    out_scope = df_result[df_result["scope"] == "out_of_scope"]

    print("\n🎯 Résultats In-scope")
    print(f"Base Exec: {in_scope['base_exec'].mean() * 100:.1f}%")
    print(f"FT Exec:   {in_scope['ft_exec'].mean() * 100:.1f}%")
    print(f"Base Sem:  {in_scope['base_semantic'].mean() / 2 * 100:.1f}%")
    print(f"FT Sem:    {in_scope['ft_semantic'].mean() / 2 * 100:.1f}%")

    print("\n🚫 Résultats Out-of-scope")
    print(f"FT refusés (sûrs): {(~out_scope['ft_safe']).mean() * 100:.1f}%")
    print(f"Base refusés (sûrs): {(~out_scope['base_safe']).mean() * 100:.1f}%")

    print("\n📊 Refus correct (sur out-of-scope)")
    print(f"FT refus corrects : {refusal_rate(df_result, 'ft'):.1f}%")
    print(f"Base refus corrects : {refusal_rate(df_result, 'base'):.1f}%")


    plot_deltas(in_scope)
    plot_results(
        base_exec=in_scope["base_exec"].mean() * 100,
        ft_exec=in_scope["ft_exec"].mean() * 100,
        base_accuracy=in_scope["base_semantic"].mean() / 2 * 100,
        ft_accuracy=in_scope["ft_semantic"].mean() / 2 * 100,
    )
    plot_scores_by_scope(df_result)


if __name__ == "__main__":
    robust_evaluate()
