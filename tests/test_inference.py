# tests/test_inference.py

from src.inference.predict import predict_sql

def test_inference():
    question = "Quel est le chiffre d'affaires total en 2023 ?"
    sql = predict_sql(question)
    assert sql is not None
    assert isinstance(sql, str)
    assert sql.startswith("SELECT") or sql == "INCOMPLETE_SCHEMA"

def test_sanitization_true_string():
    from src.security.safety_checks import sanitize_sql_output
    assert sanitize_sql_output("True") == (False, "La requête ne commence pas par SELECT")

def test_sanitization_valid_sql():
    from src.security.safety_checks import sanitize_sql_output
    sql = "SELECT * FROM my_table"
    assert sanitize_sql_output(sql) == (True, None)
