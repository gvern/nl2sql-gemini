import pandas as pd
from src.evaluation.metrics import evaluate_model
from src.evaluation.plots import plot_results, plot_deltas
import os

RESULTS_PATH = "evaluation/evaluation_results_complete.csv"

def evaluate():
    print("📊 Lancement de l'évaluation...")
    results_df = evaluate_model()
    os.makedirs("evaluation", exist_ok=True)
    results_df.to_csv(RESULTS_PATH, index=False)
    
    filtered_df = results_df[
        (results_df['ft_sql'] != "INCOMPLETE_SCHEMA") & 
        (results_df['base_sql'].notna())
    ]

    print("\n✅ Scores principaux :")
    base_sem = filtered_df['base_semantic'].mean() / 2 * 100
    ft_sem = filtered_df['ft_semantic'].mean() / 2 * 100
    base_exec = filtered_df['base_exec'].mean() * 100
    ft_exec = filtered_df['ft_exec'].mean() * 100

    print(f"Base Semantic Accuracy: {base_sem:.2f}%")
    print(f"Fine-tuned Semantic Accuracy: {ft_sem:.2f}%")
    print(f"Base Execution Accuracy: {base_exec:.2f}%")
    print(f"Fine-tuned Execution Accuracy: {ft_exec:.2f}%")

    plot_results(base_exec, ft_exec, base_sem, ft_sem)
    plot_deltas(filtered_df)
