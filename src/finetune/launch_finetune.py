from vertexai.preview.generative_models import FineTuningJob, FineTuningConfig
from vertexai import init
import os

from config.settings import PROJECT_ID, VERTEX_LOCATION

def launch_finetune(
    display_name: str,
    source_model: str,
    training_file_uri: str,
    validation_file_uri: str,
    output_dir: str
) -> str:
    """
    Lance un job de fine-tuning sur Vertex AI avec un modèle Gemini.
    
    Args:
        display_name (str): Nom du job affiché sur Vertex.
        source_model (str): Nom du modèle de base (ex: gemini-1.5-pro-preview).
        training_file_uri (str): URI GCS du fichier JSONL d'entraînement.
        validation_file_uri (str): URI GCS du fichier JSONL de validation.
        output_dir (str): URI du dossier GCS pour la sortie du modèle fine-tuné.
    
    Returns:
        str: Nom complet du modèle fine-tuné déployé.
    """
    init(project=PROJECT_ID, location=VERTEX_LOCATION)

    job = FineTuningJob(
        display_name=display_name,
        model_name=source_model,
        tuning_config=FineTuningConfig(
            train_data=training_file_uri,
            validation_data=validation_file_uri,
            output_dir=output_dir,
            epochs=3,
            learning_rate=3e-5
        ),
    )
    model = job.run(sync=True)
    print(f"✅ Modèle fine-tuné disponible à : {model.resource_name}")
    return model.resource_name

if __name__ == "__main__":
    # Exemple d'appel
    launch_finetune(
        display_name="nl2sql-gemini-rdm",
        source_model="gemini-1.5-pro-preview",
        training_file_uri="gs://my-bucket/data/train.jsonl",
        validation_file_uri="gs://my-bucket/data/val.jsonl",
        output_dir="gs://my-bucket/models/nl2sql/"
    )
