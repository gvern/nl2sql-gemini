# src/inference/predict.py

from google import genai
from google.genai import types
from config.settings import PROJECT_NUMBER, ENDPOINT_ID, VERTEX_LOCATION
from src.schema.format_prompt import FT_PROMPT_PREFIX
from src.security.safety_checks import sanitize_sql_output

def predict_sql(question: str) -> str:
    """
    Appelle le modèle fine-tuné déployé sur un endpoint Vertex AI pour générer une requête SQL.

    Args:
        question (str): Question utilisateur en langage naturel.

    Returns:
        str: Requête SQL générée ou 'INCOMPLETE_SCHEMA'
    """
    try:
        client = genai.Client(vertexai=True, project=PROJECT_NUMBER, location=VERTEX_LOCATION)
        endpoint = f"projects/{PROJECT_NUMBER}/locations/{VERTEX_LOCATION}/endpoints/{ENDPOINT_ID}"

        content = [
            types.Content(role="user", parts=[
                types.Part(text=f"{FT_PROMPT_PREFIX}\n\nQuestion : {question}")
            ])
        ]

        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=2048,
            response_modalities=["TEXT"],
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
            ]
        )

        # Génération en streaming
        stream = client.models.generate_content_stream(model=endpoint, contents=content, config=config)
        response = "".join(chunk.text for chunk in stream if chunk.text).strip()

        # Vérification stricte du contenu généré
        if not response or not isinstance(response, str):
            print("⚠️ Réponse vide ou invalide.")
            return "INCOMPLETE_SCHEMA"

        # Nettoyage basique
        cleaned_sql = response.strip()

        # Sécurité : vérifie la validité de la requête générée
        is_safe, reason = sanitize_sql_output(cleaned_sql)
        if not is_safe:
            print(f"🚫 Requête refusée : {reason}")
            return "INCOMPLETE_SCHEMA"

        return cleaned_sql

    except Exception as e:
        print(f"❌ Erreur lors de la prédiction : {e}")
        return "INCOMPLETE_SCHEMA"
