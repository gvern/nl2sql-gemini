# tests/test_inference.py

from src.inference.predict import predict_sql

def test_inference():
    question = "Quel est le chiffre d'affaires total en 2023 ?"
    sql = predict_sql(question)
    assert sql is not None
    assert isinstance(sql, str)
    assert sql.startswith("SELECT") or sql == "INCOMPLETE_SCHEMA"
