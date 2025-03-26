# src/security/safety_checks.py

import re

SQL_DANGEROUS_KEYWORDS = ["DROP", "DELETE", "ALTER", "TRUNCATE", "UPDATE", "INSERT"]

def validate_input(text):
    if not text or len(text.strip()) < 3:
        return False
    return True

def sanitize_sql_output(sql):
    if not sql:
        return False
    for keyword in SQL_DANGEROUS_KEYWORDS:
        if re.search(rf'\b{keyword}\b', sql, re.IGNORECASE):
            return False
    return True
