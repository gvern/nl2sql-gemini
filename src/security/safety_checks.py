# src/security/safety_checks.py

import re

SQL_DANGEROUS_KEYWORDS = ["DROP", "DELETE", "ALTER", "TRUNCATE", "UPDATE", "INSERT"]

def validate_input(text):
    if not text or len(text.strip()) < 3:
        return False
    return True


def sanitize_sql_output(sql: str) -> tuple[bool, str | None]:
    """
    Vérifie que la requête SQL générée ne contient pas de mots-clés dangereux.

    Args:
        sql (str): Requête SQL à analyser.

    Returns:
        tuple[bool, str | None]: 
            - (True, None) si la requête est sûre.
            - (False, "mot-clé détecté") si un mot-clé dangereux est trouvé.
    """
    if not isinstance(sql, str) or not sql.strip():
        return False, "Sortie vide ou invalide"

    sql = sql.strip()
    if not sql.lower().startswith("select"):
        return False, "La requête ne commence pas par SELECT"

    for keyword in SQL_DANGEROUS_KEYWORDS:
        if re.search(rf'\b{keyword}\b', sql, re.IGNORECASE):
            return False, f"Mot-clé interdit détecté : {keyword.upper()}"

    return True, None

