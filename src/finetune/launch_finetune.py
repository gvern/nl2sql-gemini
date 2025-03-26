import time
import vertexai
from vertexai.tuning import sft

# === Configuration ===
project_id = "avisia-self-service-analytics"
location = "europe-west1"
training_data_uri = "gs://self-service-analytics-bucket/data/Finetuning_dataset/finetuning_data.jsonl"
validation_data_uri = "gs://self-service-analytics-bucket/data/Finetuning_dataset/validation_dataset.jsonl"
source_model = "gemini-2.0-flash-001"

# === Fine-tuning ===
def finetune_gemini_model():
    vertexai.init(project=project_id, location=location)
    try:
        job = sft.train(
            source_model=source_model,
            train_dataset=training_data_uri,
            validation_dataset=validation_data_uri
        )
        while not job.has_ended:
            print(f"⏳ Tuning job state: {job.state}")
            time.sleep(120)
            job.refresh()
        if job.state == 4:
            print("✅ Fine-tuning terminé avec succès.")
            print(f"🔧 Nom du modèle fine-tuné : {job.tuned_model_name}")
            return job.tuned_model_name
        else:
            raise RuntimeError(f"💥 Échec du fine-tuning. État final: {job.state}")
    except Exception as e:
        print(f"❌ Erreur lors du fine-tuning : {e}")
        raise

# === Lancement ===
if __name__ == "__main__":
    finetune_gemini_model()
