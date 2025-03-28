# scripts/replot_robust.py

import pandas as pd
from src.evaluation.plots import (
    plot_results,
    plot_deltas,
    plot_scores_by_scope,
    plot_refusal_rate,
    plot_scope_distribution,
    plot_complexity_vs_accuracy,
    plot_comparatif_performance
)

RESULTS_CSV = "evaluation/evaluation_robust.csv"

if __name__ == "__main__":
    df = pd.read_csv(RESULTS_CSV)

    print("📊 Relance des visualisations à partir de :", RESULTS_CSV)

    in_scope = df[df["scope"] == "in_scope"]

    # 1. Résultats globaux sur in-scope uniquement
    plot_results(
        base_exec=in_scope["base_exec"].mean() * 100,
        ft_exec=in_scope["ft_exec"].mean() * 100,
        base_accuracy=in_scope["base_semantic"].mean() / 2 * 100,
        ft_accuracy=in_scope["ft_semantic"].mean() / 2 * 100,
    )

    # 2. Deltas FT vs Base
    plot_deltas(in_scope)

    # Refus corrects
    plot_refusal_rate(df)

    # Comparaison fine
    plot_comparatif_performance(df)

    # Par scope
    plot_scores_by_scope(df)

    # 4. Taux de refus corrects sur out-of-scope
    plot_refusal_rates(df)

    # 5. Distribution des types de question
    plot_scope_distribution(df)

    # 6. Complexité vs précision (si dispo)
    plot_complexity_vs_accuracy(df)

    print("✅ Tous les graphiques ont été sauvegardés dans le dossier evaluation/")
