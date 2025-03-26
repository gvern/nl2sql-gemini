# src/inference/serve.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.inference.predict import predict_sql
from src.security.safety_checks import validate_input, sanitize_sql_output
from src.security.scope_filter import classify_scope


app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/predict")
def get_prediction(payload: QueryRequest):
    if not validate_input(payload.question):
        raise HTTPException(status_code=400, detail="Entrée invalide.")
    if classify_scope(payload.question) == "out_of_scope":
        raise HTTPException(status_code=400, detail="Question hors-scope détectée.")

    sql = predict_sql(payload.question)

    is_safe, reason = sanitize_sql_output(sql)
    if not is_safe:
        raise HTTPException(status_code=403, detail=f"Sortie SQL non autorisée : {reason}")


    return {"sql": sql}
