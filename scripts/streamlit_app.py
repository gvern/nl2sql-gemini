# scripts/streamlit_app.py

import streamlit as st
from src.inference.predict import predict_sql
from src.security.safety_checks import validate_input, sanitize_sql_output
from google.cloud import bigquery
from config.settings import PROJECT_ID, BQ_LOCATION

st.set_page_config(page_title="💬 NL-to-SQL avec Gemini", layout="centered")

st.title("🧠 Reine des Maracas - Générateur SQL")
st.markdown("Posez une question en langage naturel. Le modèle génère une requête SQL, l'exécute, et affiche les résultats.")

user_input = st.text_input("📥 Question utilisateur", placeholder="Exemple : Quel est le CA total en 2023 ?")

if st.button("🚀 Générer et Exécuter SQL"):
    if not validate_input(user_input):
        st.error("❌ Entrée invalide. Veuillez entrer une question plus descriptive.")
    else:
        with st.spinner("💡 Génération en cours..."):
            sql = predict_sql(user_input)

        if not sanitize_sql_output(sql):
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
                st.dataframe(df)
            except Exception as e:
                st.error(f"❌ Erreur lors de l'exécution de la requête : {e}")
