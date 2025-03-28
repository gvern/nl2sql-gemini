import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd

def plot_results(base_exec, ft_exec, base_accuracy, ft_accuracy):
    labels = ['Execution Accuracy', 'Semantic Score']
    base_scores = [base_exec, base_accuracy]
    ft_scores = [ft_exec, ft_accuracy]

    x = range(len(labels))
    fig, ax = plt.subplots()
    bar_base = ax.bar(x, base_scores, width=0.4, label='Base', color='#8DA0CB')
    bar_ft = ax.bar([i + 0.4 for i in x], ft_scores, width=0.4, label='Fine-tuned', color='#66C2A5')

    for bars in [bar_base, bar_ft]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1, f'{height:.1f}%', ha='center', va='bottom', fontsize=10)

    ax.set_xticks([i + 0.2 for i in x])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 110)
    ax.set_ylabel('Accuracy (%)')
    ax.set_title('📊 Comparaison des modèles')
    ax.legend()
    plt.tight_layout()
    os.makedirs("evaluation", exist_ok=True)
    plt.savefig("evaluation/comparaison_modeles.png")
    plt.show()

def plot_comparatif_performance(df):
    semantic_delta = df['ft_semantic'] - df['base_semantic']
    exec_delta = df['ft_exec'].astype(int) - df['base_exec'].astype(int)

    sem = {
        'Fine-tuned meilleur': (semantic_delta > 0).sum(),
        'Égalité': (semantic_delta == 0).sum(),
        'Base meilleur': (semantic_delta < 0).sum()
    }
    exe = {
        'Fine-tuned meilleur': (exec_delta > 0).sum(),
        'Égalité': (exec_delta == 0).sum(),
        'Base meilleur': (exec_delta < 0).sum()
    }

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("🔍 Comparaison directe FT vs Base", fontsize=14, fontweight="bold")
    bar_colors = ["#2ca02c", "#1f77b4", "#d62728"]

    axes[0].bar(sem.keys(), sem.values(), color=bar_colors)
    axes[0].set_title("Similarité Sémantique")
    axes[0].set_ylabel("Nombre de questions")

    axes[1].bar(exe.keys(), exe.values(), color=bar_colors)
    axes[1].set_title("Exécution réussie")

    for ax in axes:
        for bar in ax.patches:
            height = bar.get_height()
            ax.annotate(f'{height}', (bar.get_x() + bar.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=10)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig("evaluation/comparaison_claire.png")
    plt.show()


def plot_refusal_rate(ft_rate, base_rate):
    plt.figure(figsize=(6, 4))
    bars = plt.bar(["Fine-tuned", "Base"], [ft_rate, base_rate], color=["#66C2A5", "#8DA0CB"])
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1, f'{height:.1f}%', ha='center', fontsize=10)
    plt.ylim(0, 100)
    plt.title("🚫 Taux de refus corrects sur questions hors-scope")
    plt.ylabel("Taux de refus correct (%)")
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig("evaluation/refus_corrects.png")
    plt.show()

def plot_complexity_distribution(df):
    plt.figure(figsize=(8, 5))
    sns.histplot(df["complexity_score"], bins=15, color="#69b3a2")
    plt.axvline(df["complexity_score"].mean(), color="red", linestyle="--", label="Moyenne")
    plt.axvline(5, color="orange", linestyle="--", label="Seuil low/medium")
    plt.axvline(10, color="purple", linestyle="--", label="Seuil medium/high")
    plt.legend()
    plt.title("📊 Distribution des complexités SQL")
    plt.xlabel("Score de complexité")
    plt.ylabel("Nombre de requêtes")
    plt.legend()
    plt.tight_layout()
    os.makedirs("evaluation", exist_ok=True)
    plt.savefig("evaluation/complexity_distribution.png")
    plt.show()

def plot_scores_by_complexity(df):
    bins = pd.cut(df["complexity_score"], bins=[-1, 5, 10, 100], labels=["Low", "Medium", "High"])
    df["complexity_level"] = bins

    grouped = df.groupby("complexity_level").agg({
        "ft_exec": "mean",
        "ft_semantic": "mean"
    }).reset_index()

    grouped["ft_exec"] *= 100
    grouped["ft_semantic"] = grouped["ft_semantic"] / 2 * 100

    plt.figure(figsize=(8, 5))
    plt.plot(grouped["complexity_level"], grouped["ft_exec"], marker='o', label="Execution (%)")
    plt.plot(grouped["complexity_level"], grouped["ft_semantic"], marker='s', label="Semantic (%)")
    plt.title("📊 Performance du modèle fine-tuned selon la complexité")
    plt.xlabel("Score de complexité")
    plt.ylabel("Score (%)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("evaluation/scores_by_complexity.png")
    plt.show()



def plot_validation_curve(path="evaluation/validation_scores.csv"):
    if not os.path.exists(path):
        print(f"❌ Fichier de validation introuvable : {path}")
        return

    df = pd.read_csv(path)
    plt.figure(figsize=(8, 5))
    plt.plot(df["epoch"], df["val_score"], marker="o", color="#fc8d62")
    plt.title("📈 Courbe de validation du fine-tuning")
    plt.xlabel("Époch")
    plt.ylabel("Score de validation (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("evaluation/validation_curve.png")
    plt.show()

def plot_scores_by_complexity_group(df):
    """
    Compare les performances Base vs Fine-tuned selon la complexité SQL : simple, medium, avancée.
    """
    # Définir les groupes
    def label_complexity(score):
        if score < 5:
            return "Simple"
        elif score < 10:
            return "Moyenne"
        else:
            return "Complexe"

    df["complexity_level"] = df["complexity_score"].apply(label_complexity)

    grouped = df.groupby("complexity_level").agg({
        "base_semantic": "mean",
        "ft_semantic": "mean",
        "base_exec": "mean",
        "ft_exec": "mean"
    }).reset_index()

    # Conversion en %
    for col in ["base_semantic", "ft_semantic"]:
        grouped[col] = grouped[col] / 2 * 100
    for col in ["base_exec", "ft_exec"]:
        grouped[col] *= 100

    # Affichage
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("🎯 Performance par complexité SQL", fontsize=14, fontweight="bold")

    # Sémantique
    sns.barplot(data=grouped.melt(id_vars="complexity_level", value_vars=["base_semantic", "ft_semantic"]),
                x="complexity_level", y="value", hue="variable", ax=axes[0], palette="Set2")
    axes[0].set_title("Score Sémantique")
    axes[0].set_ylabel("Score (%)")
    axes[0].set_xlabel("Complexité SQL")

    # Exécution
    sns.barplot(data=grouped.melt(id_vars="complexity_level", value_vars=["base_exec", "ft_exec"]),
                x="complexity_level", y="value", hue="variable", ax=axes[1], palette="Set2")
    axes[1].set_title("Taux d'Exécution")
    axes[1].set_ylabel("Score (%)")
    axes[1].set_xlabel("Complexité SQL")

    plt.tight_layout()
    os.makedirs("evaluation", exist_ok=True)
    plt.savefig("evaluation/scores_by_complexity_group.png")
    plt.show()
