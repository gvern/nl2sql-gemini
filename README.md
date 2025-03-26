# 🧠 NL-to-SQL with Gemini + Vertex AI

This project enables natural language to SQL query generation using a fine-tuned Gemini model on Google Cloud's Vertex AI. It is tailored for the "Reine des Maracas" BigQuery dataset.

## 🚀 Features
- Data preparation & schema injection
- Prompt engineering with context
- Vertex AI fine-tuning integration
- Model evaluation (semantic + execution)
- Secure inference API (FastAPI)
- Full pipeline automation

## 📁 Structure
(→ voir détail dans ce repo)

## 🛠️ Setup
```bash
pip install -r requirements.txt
gcloud auth application-default login

## 📂 Structure
nl2sql-gemini/
├── config/               # Paramètres globaux du projet
├── docs/                 # Whitepaper & sécurité
├── notebooks/            # Exploration EDA
├── scripts/              # Scripts principaux (API, déploiement, démo)
├── src/                 # Code principal modulaire
│   ├── data/            # Préparation de dataset
│   ├── schema/          # Extraction de schéma
│   ├── inference/       # Prédictions + API
│   ├── finetune/        # Entraînement sur Vertex AI
│   ├── evaluation/      # Évaluation (SxS, exécution)
│   └── security/        # Sécurité (validation, filtrage)
└── tests/                # Tests automatisés


## 🚀 Exécution rapide
make prepare       # Génère le fichier JSONL + upload GCS
make train         # Lance le fine-tuning Vertex AI
make deploy        # Déploie le modèle fine-tuné
make evaluate      # Compare modèle de base vs fine-tuné
make streamlit     # Lance l'app de démonstration
make test          # Exécute les tests
