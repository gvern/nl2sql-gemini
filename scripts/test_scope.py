# scripts/test_scope.py
from src.security.scope_filter import classify_scope

questions = [
    "Quel est le chiffre d'affaires total en 2023 ?",                  # in_scope
    "Combien de clients ont acheté un produit en solde ?",             # in_scope
    "Quelle est la capitale de la France ?",                           # out_of_scope
    "Combien de tickets ont été vendus à Paris ?",                     # in_scope
    "Combien de temps met la lumière à traverser la galaxie ?",        # out_of_scope
    "Qui a gagné la coupe du monde en 2018 ?",                         # out_of_scope
    "Quels sont les produits les plus vendus par région ?"            # in_scope
]

for q in questions:
    scope = classify_scope(q)
    print(f"[{scope.upper()}] {q}")
