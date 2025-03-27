# src/inference/predict.py

import logging
from google import genai
from google.genai import types
from config.settings import PROJECT_NUMBER, ENDPOINT_ID, VERTEX_LOCATION
from src.security.safety_checks import sanitize_sql_output
from src.security.scope_filter import classify_scope
from src.prompts.utils import get_prompt


FT_PROMPT_PREFIX = get_prompt("v2")

# Logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def predict_sql(question: str, use_ft_model: bool = True) -> str:
    """
    Appelle le modèle (base ou fine-tuné) pour générer une requête SQL.

    Args:
        question (str): Question utilisateur en langage naturel.
        use_ft_model (bool): True pour utiliser le modèle fine-tuné, False pour Gemini base.

    Returns:
        str: Requête SQL générée ou 'INCOMPLETE_SCHEMA'
    """
    # 🔐 Refus immédiat des questions hors-scope
    if classify_scope(question) == "out_of_scope":
        logger.warning(f"🚫 Question hors-scope détectée : {question}")
        return "INCOMPLETE_SCHEMA"

    try:
        client = genai.Client(vertexai=True, project=PROJECT_NUMBER, location=VERTEX_LOCATION)

        # Choix du modèle
        model_name = (
            f"projects/{PROJECT_NUMBER}/locations/{VERTEX_LOCATION}/endpoints/{ENDPOINT_ID}"
            if use_ft_model else "gemini-2.0-flash-001"
        )

        # Construction du prompt
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

        logger.info(f"🔍 Génération SQL | Model: {'FT' if use_ft_model else 'Base'} | Question: {question}")

        # Génération du contenu
        stream = client.models.generate_content_stream(model=model_name, contents=content, config=config)
        response = "".join(chunk.text for chunk in stream if chunk.text).strip()

        logger.debug(f"🧠 Réponse brute du modèle : {response}")

        # Vérification
        if not response or not isinstance(response, str):
            logger.warning("⚠️ Réponse vide ou invalide")
            return "INCOMPLETE_SCHEMA"

        cleaned_sql = response.strip()
        is_safe, reason = sanitize_sql_output(cleaned_sql)

        if not is_safe:
            logger.warning(f"🚫 Requête refusée : {reason}")
            return "INCOMPLETE_SCHEMA"

        return cleaned_sql

    except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction : {e}")
        return "INCOMPLETE_SCHEMA"


def generate_base_sql(question: str) -> str:
    """
    Génère une requête SQL avec le modèle de base Gemini.
    """
    return predict_sql(question, use_ft_model=False)


def generate_ft_sql(question: str) -> str:
    """
    Génère une requête SQL avec le modèle fine-tuné sur Vertex AI.
    """
    return predict_sql(question, use_ft_model=True)
