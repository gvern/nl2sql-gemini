import time
import vertexai
from vertexai.tuning import sft
from config.settings import (
    PROJECT_ID,
    VERTEX_LOCATION,
    TRAINING_DATA_URI,
    VALIDATION_DATA_URI,
    SOURCE_MODEL
)



# === Fine-tuning ===
def finetune_gemini_model():
    vertexai.init(project=PROJECT_ID, location=VERTEX_LOCATION)
    try:
        job = sft.train(
            source_model=SOURCE_MODEL,
            train_dataset=TRAINING_DATA_URI,
            validation_dataset=VALIDATION_DATA_URI
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
