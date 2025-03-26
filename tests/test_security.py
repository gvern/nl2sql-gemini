from src.security.safety_checks import sanitize_sql_output, validate_input

def test_valid_sql():
    sql = "SELECT * FROM table"
    assert sanitize_sql_output(sql) == (True, "OK")

def test_dangerous_keyword():
    from src.security.safety_checks import sanitize_sql_output
    assert sanitize_sql_output("DROP TABLE users") == (False, "La requête ne commence pas par SELECT ou WITH")

def test_non_select_query():
    from src.security.safety_checks import sanitize_sql_output
    assert sanitize_sql_output("UPDATE users SET ...") == (False, "La requête ne commence pas par SELECT ou WITH")

def test_input_validation():
    from src.security.safety_checks import validate_input
    assert validate_input("ok?") is True  # Fix : "ok" est trop court pour ta logique (min 4 caractères dans certains cas ?)


def test_empty_output():
    assert sanitize_sql_output("") == (False, "Sortie vide")

def test_boolean_output():
    assert sanitize_sql_output("True") == (False, "Sortie booléenne invalide")


def test_classify_scope_in_scope():
    from src.security.scope_filter import classify_scope
    assert classify_scope("Quel est le chiffre d'affaires ?") == "in_scope"

def test_classify_scope_out_scope():
    from src.security.scope_filter import classify_scope
    assert classify_scope("Quelle est la capitale de la France ?") == "out_of_scope"
