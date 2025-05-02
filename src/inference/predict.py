# src/inference/predict.py

import logging
from google import genai
from google.genai import types
from config.settings import PROJECT_NUMBER, ENDPOINT_ID, VERTEX_LOCATION
from src.security.safety_checks import sanitize_sql_output
from src.security.scope_filter import classify_scope
from src.prompts.utils import get_prompt
from src.logging_config import logger
from typing import Tuple, Optional, Any # Added Any


FT_PROMPT_PREFIX = get_prompt("v1")

# Logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Placeholder Pricing ---
# TODO: Replace with actual pricing per 1000 tokens for your models
# Example pricing (replace with actual values)
PRICING = {
    "gemini-2.0-flash-001": {"input": 0.00015, "output": 0.00060}, # Example price per 1k tokens
    "ft_endpoint": {"input": 0.00015, "output": 0.00060} # Example price for FT model per 1k tokens
}
# -------------------------

def _calculate_cost(model_key: str, usage_metadata: Optional[Any]) -> Optional[float]:
    """Calculates cost based on token usage and pricing."""
    if usage_metadata is None:
        logger.warning("Usage metadata not available, cannot calculate cost.")
        return None
    if model_key not in PRICING:
        logger.warning(f"Pricing not defined for model key '{model_key}', cannot calculate cost.")
        return None

    try:
        input_tokens = usage_metadata.prompt_token_count
        output_tokens = usage_metadata.candidates_token_count
        price = PRICING[model_key]

        cost = ((input_tokens / 1000) * price["input"]) + ((output_tokens / 1000) * price["output"])
        logger.info(f"Cost Calculation: Input Tokens={input_tokens}, Output Tokens={output_tokens}, Estimated Cost=${cost:.6f}")
        return round(cost, 6)
    except Exception as e:
        logger.error(f"Error calculating cost: {e}", exc_info=True)
        return None

def predict_sql(question: str, use_ft_model: bool = True) -> Tuple[str, Optional[float]]:
    """
    Appelle le modèle (base ou fine-tuné) pour générer une requête SQL et estime le coût.

    Args:
        question (str): Question utilisateur en langage naturel.
        use_ft_model (bool): True pour utiliser le modèle fine-tuné, False pour Gemini base.

    Returns:
        Tuple[str, Optional[float]]: Requête SQL générée (ou 'INCOMPLETE_SCHEMA') et coût estimé (ou None).
    """
    estimated_cost = None
    sql_result = "INCOMPLETE_SCHEMA" # Default result

    # 🔐 Refus immédiat des questions hors-scope
    if classify_scope(question) == "out_of_scope":
        logger.warning(f"🚫 Question hors-scope détectée : {question}")
        return sql_result, estimated_cost # Return default result and None cost

    try:
        client = genai.Client(vertexai=True, project=PROJECT_NUMBER, location=VERTEX_LOCATION)

        # Choix du modèle et pricing key
        if use_ft_model:
            model_name = f"projects/{PROJECT_NUMBER}/locations/{VERTEX_LOCATION}/endpoints/{ENDPOINT_ID}"
            model_key_for_pricing = "ft_endpoint" # Key for pricing dict
        else:
            model_name = "gemini-2.0-flash-001"
            model_key_for_pricing = "gemini-2.0-flash-001" # Key for pricing dict

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

        # Génération du contenu - Use non-streaming to easily get usage metadata
        # Note: If streaming is strictly required, extracting metadata might need adjustments
        # based on library specifics or might not be available until the full stream is processed.
        response_obj = client.models.generate_content(model=model_name, contents=content, config=config)

        # Extract text
        response_text = response_obj.text.strip()
        logger.debug(f"🧠 Réponse brute du modèle : {response_text}")

        # --- Cost Calculation ---
        try:
            # Attempt to get usage metadata (might be under response_obj.usage_metadata)
            usage_metadata = getattr(response_obj, 'usage_metadata', None)
            estimated_cost = _calculate_cost(model_key_for_pricing, usage_metadata)
        except Exception as cost_e:
            logger.error(f"Could not extract or calculate cost: {cost_e}", exc_info=True)
        # -----------------------


        # Vérification de la réponse SQL
        if not response_text or not isinstance(response_text, str):
            logger.warning("⚠️ Réponse vide ou invalide")
            sql_result = "INCOMPLETE_SCHEMA"
        elif response_text.lower().strip() == "incomplete_schema":
            logger.info("ℹ️ Modèle a détecté une question ambiguë ou hors schéma.")
            sql_result = "INCOMPLETE_SCHEMA"
        else:
            cleaned_sql = response_text.strip()
            is_safe, reason = sanitize_sql_output(cleaned_sql)

            if not is_safe:
                logger.warning(f"🚫 Requête refusée : {reason}")
                sql_result = "INCOMPLETE_SCHEMA"
            else:
                sql_result = cleaned_sql # Assign successful SQL

        return sql_result, estimated_cost

    except Exception as e:
        logger.error(f"❌ Erreur lors de la prédiction : {e}", exc_info=True)
        # Return default SQL and None cost in case of error
        return "INCOMPLETE_SCHEMA", None


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
