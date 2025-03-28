# scripts/replot_robust.py

from src.evaluation.plots import (
    plot_results,
    plot_comparatif_performance,
    plot_refusal_rate,
    plot_complexity_distribution,
    plot_scores_by_complexity,
    plot_scores_by_complexity_group,
    plot_validation_curve
)
import pandas as pd
import os
from generate_jsonl import score_sql_complexity


def main():
    path = "evaluation/evaluation_robust.csv"
    if not os.path.exists(path):
        print("❌ Fichier 'evaluation_robust.csv' non trouvé.")
        return

    df = pd.read_csv(path)
    # Ajoute la complexité si absente
    if "complexity_score" not in df.columns:
        df["complexity_score"] = df["expected_sql"].fillna("").apply(score_sql_complexity)

    # Séparation des scopes
    in_scope = df[df["scope"] == "in_scope"]
    out_scope = df[df["scope"] == "out_of_scope"]

    # Replots principaux
    print("📊 Replot des performances globales...")
    plot_results(
        base_exec=in_scope["base_exec"].mean() * 100,
        ft_exec=in_scope["ft_exec"].mean() * 100,
        base_accuracy=in_scope["base_semantic"].mean() / 2 * 100,
        ft_accuracy=in_scope["ft_semantic"].mean() / 2 * 100,
    )

    print("📊 Replot des deltas FT/Base...")
    plot_comparatif_performance(in_scope)



    print("📊 Replot des refus corrects...")
    ft_rate = (~out_scope["ft_safe"]).mean() * 100
    base_rate = (~out_scope["base_safe"]).mean() * 100
    plot_refusal_rate(ft_rate, base_rate)

    print("📊 Replot de la distribution des complexités...")
    plot_complexity_distribution(df)

    print("📊 Replot des scores selon la complexité...")
    plot_scores_by_complexity(df)

    print("📊 Replot des scores par complexité...")
    plot_scores_by_complexity_group(df)

    print("📊 Replot de la courbe de validation (si disponible)...")
    plot_validation_curve()  # Par défaut path = evaluation/validation_scores.csv

if __name__ == "__main__":
    main()
