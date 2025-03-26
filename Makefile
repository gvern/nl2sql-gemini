prepare:
	python scripts/generate_jsonl.py

train:
	python src/finetune/launch_finetune.py

deploy:
	python scripts/deploy_model.py

evaluate:
	PYTHONPATH=. python scripts/evaluate_models.py

run:
	uvicorn src.inference.serve:app --reload

streamlit:
	streamlit run scripts/streamlit_app.py

test:
	PYTHONPATH=. pytest tests/
