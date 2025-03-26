# src/inference/serve.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.inference.predict import predict_sql
from src.security.safety_checks import validate_input, sanitize_sql_output

app = FastAPI()

class QueryRequest(BaseModel):
    question: str

@app.post("/predict")
def get_prediction(payload: QueryRequest):
    if not validate_input(payload.question):
        raise HTTPException(status_code=400, detail="Entrée invalide.")

    sql = predict_sql(payload.question)

    if not sanitize_sql_output(sql):
        raise HTTPException(status_code=403, detail="Sortie SQL non autorisée.")

    return {"sql": sql}
