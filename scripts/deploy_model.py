from google.cloud import aiplatform
from config.settings import PROJECT_ID, VERTEX_LOCATION
from src.logging_config import logger


def deploy_model(model_name: str, endpoint_display_name: str):
    """
    Déploie un modèle fine-tuné sur un endpoint Vertex AI.

    Args:
        model_name (str): Nom du modèle fine-tuné (Vertex AI model resource name).
        endpoint_display_name (str): Nom de l'endpoint à créer.
    """
    aiplatform.init(project=PROJECT_ID, location=VERTEX_LOCATION)

    model = aiplatform.Model(model_name=model_name)

    endpoint = model.deploy(
        deployed_model_display_name=endpoint_display_name,
        machine_type="n1-standard-4",
        traffic_split={"0": 100}
    )

    print(f"✅ Modèle déployé sur l'endpoint : {endpoint.resource_name}")

if __name__ == "__main__":
    
    deploy_model(
        model_name="projects/491780955535/locations/europe-west1/models/YOUR_FINE_TUNED_MODEL_ID",
        endpoint_display_name="nl2sql-ft-endpoint"
    )
