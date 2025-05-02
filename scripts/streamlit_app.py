# scripts/streamlit_app.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from src.inference.predict import predict_sql
from src.security.safety_checks import validate_input, sanitize_sql_output
from src.security.scope_filter import classify_scope
from google.cloud import bigquery
from config.settings import PROJECT_ID, BQ_LOCATION
from datetime import datetime # Added import
import logging # Added import

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Define BigQuery table for logging
LOG_TABLE_ID = f"{PROJECT_ID}.working.conversation_history" # Added table ID definition

# Action sur clic bouton
if st.button("🚀 Générer et Exécuter la requête SQL"):
    # Initialize log data
    current_time = datetime.utcnow() # Get current time once
    log_entry = {
        # Use a BigQuery DATE-compatible format
        "timestamp": current_time.strftime('%Y-%m-%d'), # Changed format to YYYY-MM-DD
        "log_time": current_time.strftime('%H:%M:%S.%f'), # Added time field (HH:MM:SS.ffffff)
        "user_question": user_input,
        "generated_sql": None,
        "scope": None,
        "safety_status": None,
        "safety_reason": None,
        "execution_status": None,
        "error_message": None,
        "result_rows": None,
        "estimated_cost": None, # Added cost field
    }
    bq_client = None # Initialize bq_client to ensure it's available for logging even if errors occur early
    sql = None # Initialize sql variable
    cost = None # Initialize cost variable

    try:
        bq_client = bigquery.Client(project=PROJECT_ID, location=BQ_LOCATION) # Initialize client earlier

        if not validate_input(user_input):
            st.error("❌ Entrée invalide. Veuillez formuler une question plus complète.")
            log_entry["execution_status"] = "Input Validation Failed"
            # st.stop()

        else: # Only proceed if input is valid
            scope_result = classify_scope(user_input)
            log_entry["scope"] = scope_result
            if scope_result == "out_of_scope":
                st.warning("🚫 Question hors-scope détectée.")
                log_entry["execution_status"] = "Out of Scope"
                # st.stop()
            else:
                try:
                    with st.spinner("💡 Génération de la requête SQL en cours..."):
                        # Unpack the result tuple from predict_sql
                        sql, cost = predict_sql(user_input)
                    log_entry["generated_sql"] = sql
                    log_entry["estimated_cost"] = cost # Log the estimated cost

                except Exception as pred_e:
                    logger.error(f"❌ Erreur lors de la prédiction SQL : {pred_e}", exc_info=True)
                    st.error(f"❌ Erreur lors de la génération SQL : {pred_e}")
                    log_entry["execution_status"] = "Prediction Error"
                    log_entry["error_message"] = str(pred_e)
                    # Stop further processing if prediction failed
                    sql = None # Ensure sql is None so subsequent checks fail safely or are skipped
                    cost = None # Ensure cost is None

                if sql and sql != "INCOMPLETE_SCHEMA": # Only proceed if SQL was generated successfully
                    is_safe, reason = sanitize_sql_output(sql)
                    log_entry["safety_status"] = "Safe" if is_safe else "Unsafe"
                    log_entry["safety_reason"] = reason
                    if not is_safe:
                        st.error(f"🚫 Requête refusée : {reason}")
                        log_entry["execution_status"] = "Safety Check Failed"
                    else:
                        st.success("✅ Requête SQL générée :")
                        st.code(sql, language="sql")

                        # Exécution BigQuery
                        try:
                            with st.spinner("📊 Exécution de la requête sur BigQuery..."):
                                df = bq_client.query(sql).result().to_dataframe()
                            st.markdown("### 📋 Résultat de la requête")
                            st.dataframe(df)
                            log_entry["execution_status"] = "Success"
                            log_entry["result_rows"] = len(df)
                        except Exception as exec_e:
                            logger.error(f"❌ Erreur lors de l'exécution SQL : {exec_e}", exc_info=True)
                            st.error(f"❌ Erreur lors de l'exécution SQL : {exec_e}")
                            log_entry["execution_status"] = "Execution Error"
                            log_entry["error_message"] = str(exec_e)

                elif sql == "INCOMPLETE_SCHEMA":
                    st.warning("🤖 Le modèle ne peut pas répondre : schéma incomplet ou question trop vague.")
                    log_entry["execution_status"] = "Incomplete Schema"
                # If sql is None (due to prediction error), this part is skipped,
                # and the finally block will log the "Prediction Error" status.

    except Exception as app_e:
        # Catch potential errors during client init or early stages
        logger.error(f"❌ Erreur applicative inattendue : {app_e}", exc_info=True)
        st.error(f"❌ Une erreur inattendue est survenue : {app_e}")
        log_entry["execution_status"] = "App Error"
        log_entry["error_message"] = str(app_e)

    finally:
        # Insert log entry into BigQuery regardless of success/failure
        # Make sure log_entry reflects the final status before logging
        if log_entry.get("execution_status") is None and sql is None and log_entry.get("error_message") is None:
             # If status is still None and SQL is None, it likely means validation/scope stopped execution
             # We already set the status in those blocks if st.stop() wasn't used.
             # If st.stop() *was* used, this finally block might not even run.
             # If status is None but an error message exists, it was likely caught by the outer try/except.
             pass # Status should already be set appropriately above

        if bq_client: # Check if client was initialized
            try:
                # Timestamp and time are already formatted correctly
                logger.info(f"Attempting to log to BigQuery: {log_entry}") # Log what's being sent
                errors = bq_client.insert_rows_json(LOG_TABLE_ID, [log_entry])
                if errors:
                    # Log the specific BQ error
                    bq_error_message = f"Erreur lors de l'écriture des logs dans BigQuery : {errors}"
                    logger.error(bq_error_message)
                    st.error(f"⚠️ {bq_error_message}")
                    # Optionally add BQ error to the log_entry itself if you have a field for it
                    # log_entry["logging_error"] = str(errors) # Requires schema change
                # else:
                #     st.info("📝 Log enregistré.") # Optional: uncomment for user feedback
            except Exception as log_e:
                # Log the exception during the BQ insert call
                log_error_message = f"Impossible d'écrire les logs dans BigQuery : {log_e}"
                logger.error(log_error_message, exc_info=True)
                st.error(f"⚠️ {log_error_message}")
                # Optionally add BQ error to the log_entry itself
                # log_entry["logging_error"] = str(log_e) # Requires schema change
        else:
             st.error("⚠️ Client BigQuery non initialisé, impossible d'écrire les logs.")
