import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_results(base_exec, ft_exec, base_accuracy, ft_accuracy):
    labels = ['Execution Accuracy', 'Semantic Score']
    base_scores = [base_exec, base_accuracy]
    ft_scores = [ft_exec, ft_accuracy]

    x = range(len(labels))
    fig, ax = plt.subplots()
    bar_base = ax.bar(x, base_scores, width=0.4, label='Base', color='#8DA0CB')
    bar_ft = ax.bar([i + 0.4 for i in x], ft_scores, width=0.4, label='Fine-tuned', color='#66C2A5')

    # Affichage des scores sur les barres
    for bars in [bar_base, bar_ft]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1, f'{height:.1f}%', ha='center', va='bottom', fontsize=10)

    ax.set_xticks([i + 0.2 for i in x])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 110)
    ax.set_ylabel('Accuracy (%)')
    ax.set_title('Comparaison des modèles')
    ax.legend()
    plt.tight_layout()
    os.makedirs("evaluation", exist_ok=True)
    plt.savefig("evaluation/comparaison_modeles.png")
    plt.show()

def plot_deltas(df):
    df['delta_semantic'] = df['ft_semantic'] - df['base_semantic']
    df['delta_exec'] = df['ft_exec'].astype(int) - df['base_exec'].astype(int)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    sns.histplot(df['delta_semantic'], bins=3, ax=axes[0], kde=False, color="#FC8D62")
    axes[0].set_title("🧠 Écart de similarité sémantique")
    axes[0].set_xlabel("Delta Semantic Score (FT - Base)")
    axes[0].grid(True)

    sns.histplot(df['delta_exec'], bins=3, ax=axes[1], kde=False, color="#E78AC3")
    axes[1].set_title("⚙️ Écart d’exécution")
    axes[1].set_xlabel("Delta Execution (FT - Base)")
    axes[1].grid(True)

    plt.tight_layout()
    os.makedirs("evaluation", exist_ok=True)
    plt.savefig("evaluation/ecarts_deltas.png")
    plt.show()

def plot_scores_by_scope(df):
    """
    Affiche les scores d'exécution et de similarité sémantique pour les questions in-scope vs out-of-scope.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    import os

    # Préparation des données
    grouped = df.groupby("scope").agg({
        "ft_exec": "mean",
        "ft_semantic": "mean"
    }).reset_index()
    grouped["ft_exec"] *= 100
    grouped["ft_semantic"] = grouped["ft_semantic"] / 2 * 100  # Normalisé sur 100%

    # Melt pour seaborn
    plot_df = grouped.melt(id_vars="scope", var_name="metric", value_name="score")

    # Plot
    plt.figure(figsize=(8, 6))
    sns.barplot(data=plot_df, x="metric", y="score", hue="scope", palette="Set2")
    plt.title("🔎 Scores du modèle fine-tuné par type de question")
    plt.ylabel("Score (%)")
    plt.ylim(0, 110)
    plt.grid(True, axis='y')
    plt.tight_layout()

    os.makedirs("evaluation", exist_ok=True)
    plt.savefig("evaluation/scores_by_scope.png")
    plt.show()
