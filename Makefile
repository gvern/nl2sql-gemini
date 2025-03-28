# =======================
# 📦 Données & Fine-tuning
# =======================

prepare-complex:
	PYTHONPATH=. python scripts/generate_jsonl.py --top_n 100 --filter_complexity advanced

prepare-append:
	PYTHONPATH=. python scripts/generate_jsonl.py --append --filter_complexity=advanced

prepare-validation:
	PYTHONPATH=. python scripts/generate_jsonl.py --top_n 50 --filter_complexity=advanced --output Finetuning_dataset/validation_dataset.jsonl

train:
	PYTHONPATH=. python src/finetune/launch_finetune.py

deploy:
	PYTHONPATH=. python scripts/deploy_model.py

# =========================
# 📊 Évaluation des modèles
# =========================

evaluate:
	PYTHONPATH=. python scripts/evaluate_models.py

robust-eval:
	GOOGLE_CLOUD_PROJECT=avisia-self-service-analytics PYTHONPATH=. python -m src.evaluation.robust_eval

replot:
	PYTHONPATH=. python scripts/replot_robust.py

# =========================
# 🧠 Inference & UI
# =========================

run:
	PYTHONPATH=. uvicorn src.inference.serve:app --reload

streamlit:
	PYTHONPATH=. streamlit run scripts/streamlit_app.py

# =========================
# 🧪 Tests
# =========================

test:
	PYTHONPATH=. pytest tests/


