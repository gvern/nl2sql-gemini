prepare-complex:
	python scripts/generate_jsonl.py --top_n 100 --filter_complexity advanced

prepare-append:
	python scripts/generate_jsonl.py --append --filter_complexity=advanced

train:
	python src/finetune/launch_finetune.py

deploy:
	python scripts/deploy_model.py

prepare-validation:
	PYTHONPATH=. python scripts/generate_jsonl.py --top_n 50 --filter_complexity=advanced --output Finetuning_dataset/validation_dataset.jsonl

evaluate:
	PYTHONPATH=. python scripts/evaluate_models.py

run:
	uvicorn src.inference.serve:app --reload

streamlit:
	streamlit run scripts/streamlit_app.py

test:
	PYTHONPATH=. pytest tests/
robust-eval:
	GOOGLE_CLOUD_PROJECT=avisia-self-service-analytics PYTHONPATH=. python -m src.evaluation.robust_eval

