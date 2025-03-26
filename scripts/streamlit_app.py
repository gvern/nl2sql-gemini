# scripts/streamlit_app.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from src.inference.predict import predict_sql
from src.security.safety_checks import validate_input, sanitize_sql_output
from google.cloud import bigquery
from config.settings import PROJECT_ID, BQ_LOCATION

# Configuration de la page
st.set_page_config(
    page_title="💬 NL-to-SQL avec Gemini",
    layout="centered",
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main {
        background-color: #f5f8fa;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton > button {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    .stTextInput > div > div > input {
        font-size: 1.1rem;
        padding: 0.6em;
    }
</style>
""", unsafe_allow_html=True)

# Titre et sous-titre
st.title("🧠 Reine des Maracas - Générateur SQL")
st.markdown("💬 Posez une question en langage naturel. Le modèle génère une requête SQL, l'exécute, et affiche les résultats.")

# Saisie utilisateur
user_input = st.text_input("📥 Votre question :", placeholder="Exemple : Quel est le chiffre d'affaires total en 2023 ?")

# Action sur clic bouton
if st.button("🚀 Générer et Exécuter la requête SQL"):
    if not validate_input(user_input):
        st.error("❌ Entrée invalide. Veuillez formuler une question plus complète.")
    else:
        with st.spinner("💡 Génération de la requête SQL en cours..."):
            sql = predict_sql(user_input)

        if not sanitize_sql_output(sql):
            st.error(f"{sql}")
            st.error("⚠️ La requête générée contient des mots-clés interdits (DROP, DELETE, etc).")
        elif sql == "INCOMPLETE_SCHEMA":
            st.warning("🤖 Le modèle ne peut pas répondre : schéma incomplet ou question trop vague.")
        else:
            st.success("✅ Requête SQL générée :")
            st.code(sql, language="sql")

            # Exécution BigQuery
            bq_client = bigquery.Client(project=PROJECT_ID, location=BQ_LOCATION)
            try:
                with st.spinner("📊 Exécution de la requête sur BigQuery..."):
                    df = bq_client.query(sql).result().to_dataframe()
                st.markdown("### 📋 Résultat de la requête")
                st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Erreur lors de l'exécution SQL : {e}")
