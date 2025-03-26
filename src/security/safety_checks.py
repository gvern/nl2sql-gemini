import re

SQL_DANGEROUS_KEYWORDS = ["DROP", "DELETE", "ALTER", "TRUNCATE", "UPDATE", "INSERT"]

def validate_input(text):
    if not text or len(text.strip()) < 3:
        return False
    return True

def sanitize_sql_output(sql):
    """
    Vérifie que la requête SQL générée est valide et sécurisée.

    Args:
        sql (str): Requête SQL générée par le modèle.

    Returns:
        (bool, str): Tuple indiquant si la requête est sûre, et pourquoi sinon.
    """
    if not isinstance(sql, str):
        return False, "Sortie non textuelle"
    
    sql = sql.strip()

    if not sql:
        return False, "Sortie vide"

    if sql.lower() in ["true", "false"]:
        return False, "Sortie booléenne invalide"

    if not sql.lower().startswith("select"):
        return False, "La requête ne commence pas par SELECT"

    for keyword in SQL_DANGEROUS_KEYWORDS:
        if re.search(rf'\b{keyword}\b', sql, re.IGNORECASE):
            return False, f"Mot-clé interdit détecté : {keyword}"

    return True, "OK"
