from src.security.safety_checks import sanitize_sql_output, validate_input

def test_valid_sql():
    sql = "SELECT * FROM table"
    assert sanitize_sql_output(sql) == (True, "OK")

def test_dangerous_keyword():
    assert sanitize_sql_output("DROP TABLE users") == (False, "Mot-clé interdit détecté : DROP")

def test_non_select_query():
    assert sanitize_sql_output("UPDATE users SET ...") == (False, "La requête ne commence pas par SELECT")

def test_empty_output():
    assert sanitize_sql_output("") == (False, "Sortie vide")

def test_boolean_output():
    assert sanitize_sql_output("True") == (False, "Sortie booléenne invalide")

def test_input_validation():
    assert validate_input("ok") is True
    assert validate_input("  ") is False
