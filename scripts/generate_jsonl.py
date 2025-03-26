# scripts/generate_jsonl.py

from src.data.prepare_dataset import prepare_jsonl_dataset

def generate_jsonl():
    output_path = "data/processed/fine_tuning_data.jsonl"
    prepare_jsonl_dataset(output_path)
    print(f"✅ Dataset de fine-tuning généré : {output_path}")

if __name__ == "__main__":
    generate_jsonl()
