"""
Chart Generation Module
Reads empirical benchmark CSV files and generates publication-grade comparative
visualizations for project reports and academic defense.
"""

import os
import sys
import csv
import matplotlib.pyplot as plt
import numpy as np

# Styling configuration for academic presentation
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})

CHARTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "documentation", "charts"))


def load_csv(filepath: str):
    """Loads CSV file into a list of row dictionaries with type coercion."""
    data = []
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = {}
            for k, v in row.items():
                try:
                    if "." in v:
                        parsed[k] = float(v)
                    else:
                        parsed[k] = int(v)
                except ValueError:
                    parsed[k] = v
            data.append(parsed)
    return data


def plot_tree_size_vs_nodes_visited(data, save_path: str):
    """Plots Total Tree Size vs. Visited Nodes for Minimax and Alpha-Beta."""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Sort data by total tree nodes
    sorted_data = sorted(data, key=lambda x: x["total_nodes"])
    total_nodes = [d["total_nodes"] for d in sorted_data]
    mm_visited = [d["mm_nodes_visited"] for d in sorted_data]
    ab_visited = [d["ab_nodes_visited"] for d in sorted_data]

    ax.plot(total_nodes, mm_visited, "o-", color="#D9534F", linewidth=2, label="Minimax (Full Exploration)")
    ax.plot(total_nodes, ab_visited, "s-", color="#1E88E5", linewidth=2, label="Alpha-Beta (Pruned Exploration)")

    # Diagonal reference line (100% exploration)
    ax.plot(total_nodes, total_nodes, "--", color="#888888", alpha=0.6, label="Complete Tree Size (Reference)")

    ax.set_xlabel("Total Nodes in Game Tree")
    ax.set_ylabel("Nodes Evaluated / Visited")
    ax.set_title("Search Scalability: Minimax vs. Alpha-Beta Node Expansions")
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"Generated chart: {save_path}")


def plot_tree_depth_vs_runtime(data, save_path: str):
    """Plots Depth vs. Execution Time grouped by Branching Factor."""
    fig, ax = plt.subplots(figsize=(8, 5))

    branching_factors = sorted(list(set(d["branching_factor"] for d in data)))
    colors = ["#2E7D32", "#E65100", "#6A1B9A"]

    for i, b in enumerate(branching_factors):
        sub = [d for d in data if d["branching_factor"] == b]
        sub = sorted(sub, key=lambda x: x["depth"])
        depths = [d["depth"] for d in sub]
        mm_times = [d["mm_time_ms"] for d in sub]
        ab_times = [d["ab_time_ms"] for d in sub]

        ax.plot(depths, mm_times, "--", marker="o", color=colors[i % len(colors)], alpha=0.7,
                label=f"Minimax (b={b})")
        ax.plot(depths, ab_times, "-", marker="s", color=colors[i % len(colors)], linewidth=2,
                label=f"Alpha-Beta (b={b})")

    ax.set_xlabel("Tree Depth (Search Ply)")
    ax.set_ylabel("Median Execution Time (ms)")
    ax.set_title("Computational Latency Across Tree Depth and Branching Factor")
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"Generated chart: {save_path}")


def plot_minimax_vs_alphabeta_evaluations(data, save_path: str):
    """Bar chart comparing Leaf Evaluations across selected problem scales."""
    fig, ax = plt.subplots(figsize=(9, 5))

    # Pick representative configurations
    selected_labels = ["b=2, d=4", "b=2, d=5", "b=2, d=6", "b=3, d=3", "b=3, d=4", "b=3, d=5", "b=4, d=3", "b=4, d=4"]
    selected_items = []
    for d in data:
        label = f"b={d['branching_factor']}, d={d['depth']}"
        if label in selected_labels:
            selected_items.append((label, d["mm_leaf_evals"], d["ab_leaf_evals"]))

    labels = [item[0] for item in selected_items]
    mm_evals = [item[1] for item in selected_items]
    ab_evals = [item[2] for item in selected_items]

    x = np.arange(len(labels))
    width = 0.35

    rects1 = ax.bar(x - width/2, mm_evals, width, label="Minimax Leaf Evaluations", color="#EF5350")
    rects2 = ax.bar(x + width/2, ab_evals, width, label="Alpha-Beta Leaf Evaluations", color="#42A5F5")

    ax.set_ylabel("Terminal Leaf Evaluations")
    ax.set_title("Terminal State Evaluations: Pruning Reduction Factor")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")

    plt.tight_layout()
    fig.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"Generated chart: {save_path}")


def plot_ordering_effect_on_pruning(order_data, save_path: str):
    """Grouped bar chart showing the effect of move ordering on Pruning Efficiency (%)."""
    fig, ax = plt.subplots(figsize=(9, 5))

    instances = sorted(list(set((d["branching_factor"], d["depth"]) for d in order_data)))
    labels = [f"b={b}, d={d}" for b, d in instances]

    best_eff = []
    rand_eff = []
    worst_eff = []

    for b, d in instances:
        b_sub = [x for x in order_data if x["branching_factor"] == b and x["depth"] == d]
        b_map = {x["ordering_strategy"]: x["pruning_efficiency_pct"] for x in b_sub}
        best_eff.append(b_map.get("best", 0.0))
        rand_eff.append(b_map.get("random", 0.0))
        worst_eff.append(b_map.get("worst", 0.0))

    x = np.arange(len(labels))
    width = 0.25

    ax.bar(x - width, best_eff, width, label="Best-Case Ordering", color="#2E7D32")
    ax.bar(x, rand_eff, width, label="Random / Natural Ordering", color="#FB8C00")
    ax.bar(x + width, worst_eff, width, label="Worst-Case Ordering", color="#C62828")

    ax.set_ylabel("Pruning Efficiency (%)")
    ax.set_xlabel("Game Tree Configuration")
    ax.set_title("Ablation Study: Move Ordering Impact on Alpha-Beta Pruning Efficiency")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.legend(frameon=True, facecolor="white", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")

    plt.tight_layout()
    fig.savefig(save_path, dpi=300)
    plt.close(fig)
    print(f"Generated chart: {save_path}")


def main():
    os.makedirs(CHARTS_DIR, exist_ok=True)
    scaling_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "results.csv"))
    ordering_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "ordering_results.csv"))

    if not os.path.exists(scaling_csv) or not os.path.exists(ordering_csv):
        print("Benchmark CSV files not found. Running benchmark suite first...")
        from benchmarks.benchmark import run_benchmark_suite
        run_benchmark_suite(scaling_csv, ordering_csv)

    scaling_data = load_csv(scaling_csv)
    ordering_data = load_csv(ordering_csv)

    plot_tree_size_vs_nodes_visited(scaling_data, os.path.join(CHARTS_DIR, "tree_size_vs_nodes_visited.png"))
    plot_tree_depth_vs_runtime(scaling_data, os.path.join(CHARTS_DIR, "tree_depth_vs_runtime.png"))
    plot_minimax_vs_alphabeta_evaluations(scaling_data, os.path.join(CHARTS_DIR, "minimax_vs_alphabeta_evaluations.png"))
    plot_ordering_effect_on_pruning(ordering_data, os.path.join(CHARTS_DIR, "ordering_effect_on_pruning.png"))

    print("\nAll comparative charts successfully generated in:", CHARTS_DIR)


if __name__ == "__main__":
    main()
