prepare:
	python scripts/generate_jsonl.py

train:
	python src/finetune/launch_finetune.py

deploy:
	python scripts/deploy_model.py

evaluate:
	python scripts/evaluate_models.py

run:
	uvicorn src.inference.serve:app --reload
	
streamlit:
	streamlit run scripts/streamlit_app.py
