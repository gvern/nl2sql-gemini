# src/security/scope_filter.py
from vertexai import init as vertexai_init
from vertexai.generative_models import GenerativeModel, GenerationConfig, Content, Part
from config.settings import PROJECT_ID, VERTEX_LOCATION


vertexai_init(project=PROJECT_ID, location=VERTEX_LOCATION)
generation_config = GenerationConfig(temperature=0, max_output_tokens=512)
model_judge = GenerativeModel("gemini-pro")

def classify_scope(question: str) -> str:
    """
    Détermine si une question est en lien avec la base métier.

    Returns: "in_scope" ou "out_of_scope"
    """
    prompt = f"""
    Cette question est-elle liée à une base de données métier sur la vente, les clients, les produits ou les tickets ?
    Réponds uniquement par "in_scope" ou "out_of_scope".

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
