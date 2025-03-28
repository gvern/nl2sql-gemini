
# 🧠 NL2SQL avec Gemini + Vertex AI

Une solution complète pour traduire des questions en langage naturel en requêtes SQL BigQuery grâce à un modèle Gemini fine-tuné sur Vertex AI. Conçu pour la base de données *Reine des Maracas* et pensé pour la production, ce projet intègre **préparation de données**, **fine-tuning**, **déploiement sécurisé**, **inférence via API et Streamlit**, et **évaluation robuste**.

---

## 🚀 Fonctionnalités

- ✅ **Fine-tuning Vertex AI** avec JSONL enrichi (schéma + few-shot)
- ✅ **Reformulation & Sécurité** : classification in/out-of-scope, sanitization
- ✅ **Exécution SQL BigQuery sécurisée** avec requêtes paramétrées
- ✅ **Démo interactive** via **Streamlit**
- ✅ **API REST sécurisée** via **FastAPI**
- ✅ **Évaluation avancée** (sémantique, exécution, complexité, refus)
- ✅ **Monitoring et visualisations** complètes (`matplotlib`, `seaborn`)

---

## 📁 Arborescence du dépôt

``` bash
nl2sql-gemini/
├── config/               # Paramètres globaux
├── docs/                 # Whitepaper + sécurité
├── notebooks/            # EDA
├── scripts/              # Entrées CLI : training, démo, génération
├── src/                  # Code principal (modulaire et sécurisé)
│   ├── data/             # Dataset + JSONL
│   ├── schema/           # Extraction de schéma
│   ├── prompts/          # Prompts versionnés (v1/v2)
│   ├── finetune/         # Fine-tuning Vertex AI
│   ├── inference/        # Prédiction + API
│   ├── evaluation/       # Évaluation & visualisations
│   └── security/         # Sécurité & filtrage
└── tests/                # Tests unitaires
```

---

## ⚙️ Installation

```bash

cd nl2sql-gemini
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
gcloud auth application-default login
```

---

## 🔧 Paramétrage GCP

Assurez-vous d'avoir :
- Un projet GCP actif avec BigQuery et Vertex AI
- Les variables définies dans `config/settings.py` :
  - `PROJECT_ID`, `ENDPOINT_ID`, `DATASET_ID`, `BUCKET_ID`, etc.
- Un compte de service avec des permissions minimales (IAM restreint)

---

## 🛠️ Exécution rapide

```bash
make prepare         # Génère le JSONL de fine-tuning
make train           # Lance le fine-tuning sur Vertex AI
make deploy          # Déploie le modèle fine-tuné
make evaluate        # Évalue le modèle sur des cas approuvés
make robust-eval     # Évalue le modèle sur des cas robustes (sécurité, refus, scope)
make streamlit       # Lance l'app Streamlit
make test            # Exécute tous les tests
```

---

## 🧪 Évaluation des modèles

Deux modes d’évaluation disponibles :

```bash
make evaluate        # Évaluation standard (base vs fine-tuned)
make robust-eval     # Évaluation robuste (scope, refus, sécurité, complexité)
make replot          # Génère tous les graphiques à partir des CSV
```

Exemples de visualisations :
- `comparaison_modeles.png`
- `scores_by_complexity_group.png`
- `refus_corrects.png`
- `validation_curve.png`

---

## 💡 Fonctionnalités de sécurité

- 🔒 Validation stricte des entrées (`length`, `caractères interdits`)
- 🔐 Filtrage automatique des questions hors-scope (`classify_scope`)
- ⚠️ Requêtes SQL sécurisées via `sanitize_sql_output` + requêtes paramétrées
- 🔁 Audit de l’ensemble des résultats et refus corrects

---

## 🖥️ API REST (FastAPI)

```bash
make run
```

- Endpoint `/predict`
- Entrée : question utilisateur
- Sortie : requête SQL générée ou message d'erreur sécurisé

---

## 🧑‍💻 Démo Streamlit

```bash
make streamlit
```

- Interface utilisateur intuitive
- Génération + exécution SQL avec résultats en temps réel

---
