# tests/test_inference.py

from src.inference.predict import predict_sql
from src.security.safety_checks import sanitize_sql_output

def test_inference():
    question = "Quel est le chiffre d'affaires total en 2023 ?"
    sql = predict_sql(question)
    assert sql is not None
    assert isinstance(sql, str)
    assert sql.startswith("SELECT") or sql == "INCOMPLETE_SCHEMA"

def test_sanitization_true_string():
    from src.security.safety_checks import sanitize_sql_output
    assert sanitize_sql_output("True") == (False, "Sortie booléenne invalide")

def test_sanitization_valid_sql():
    from src.security.safety_checks import sanitize_sql_output
    sql = "SELECT * FROM my_table"
    assert sanitize_sql_output(sql) == (True, "OK")

def test_get_prompt_versions():
    from src.prompts.utils import get_prompt
    assert "INCOMPLETE_SCHEMA" in get_prompt("v1")
    assert "Exemple" in get_prompt("v2")
def test_ft_and_base_generation():
    from src.inference.predict import generate_base_sql, generate_ft_sql
    question = "Quel est le total des ventes ?"
    base_sql = generate_base_sql(question)
    ft_sql = generate_ft_sql(question)
    assert isinstance(base_sql, str)
    assert isinstance(ft_sql, str)

def test_sql_injection():
    sql = "SELECT * FROM users; DROP TABLE clients;"
    is_safe, reason = sanitize_sql_output(sql)
    assert not is_safe
    assert "Mot-clé interdit" in reason or "ne commence pas" in reason
