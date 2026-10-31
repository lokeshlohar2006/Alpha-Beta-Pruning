"""
Benchmarking Framework for Minimax vs. Alpha-Beta Pruning
Conducts reproducible empirical evaluations across varying tree depths,
branching factors, and child-ordering strategies, logging real metrics to CSV.
"""

import os
import csv
import sys
import time
import platform
import statistics
from typing import List, Dict, Any, Tuple

# Ensure repository root is in sys.path when script is executed directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.game_tree import Node
from core.tree_generator import create_random_tree
from algorithms.minimax import Minimax
from algorithms.alpha_beta import AlphaBetaPruning


def sort_tree_children(node: Node, ordering: str = "best") -> None:
    """
    Recursively sorts child nodes to simulate best-case or worst-case child exploration orders.

    - "best": For MAX nodes, explore highest child value first (descending).
              For MIN nodes, explore lowest child value first (ascending).
    - "worst": For MAX nodes, explore lowest child value first (ascending).
               For MIN nodes, explore highest child value first (descending).
    """
    # First solve minimax value for children so we know their true values
    mm = Minimax(record_trace=False)

    for child in node.children:
        if not child.is_leaf:
            sort_tree_children(child, ordering)

    if not node.is_leaf:
        # Precompute child values
        for child in node.children:
            child_clone = child.clone()
            child.value = mm.search(child_clone).root_value

        if ordering == "best":
            # MAX wants max first; MIN wants min first
            node.children.sort(key=lambda c: c.value, reverse=node.is_max)
        elif ordering == "worst":
            # Reverse of best
            node.children.sort(key=lambda c: c.value, reverse=not node.is_max)


def run_benchmark_suite(
    output_csv: str = "benchmarks/results.csv",
    ordering_csv: str = "benchmarks/ordering_results.csv",
    num_trials: int = 5,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes a comprehensive battery of benchmark runs.

    Args:
        output_csv (str): Output path for the main scaling results.
        ordering_csv (str): Output path for the move-ordering ablation study.
        num_trials (int): Number of repetitions per instance for median timing.

    Returns:
        Tuple of (scaling_results, ordering_results).
    """
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    print("=" * 70)
    print("STARTING ALGORITHM BENCHMARK SUITE")
    print(f"Platform: {platform.system()} {platform.release()} | Python: {sys.version.split()[0]}")
    print(f"Repetitions per configuration: {num_trials} (Reporting median runtime)")
    print("=" * 70)

    # Matrix of configurations: branching factor b, depth d
    # Keeps tree size within practical limits for deep benchmarking
    configs = [
        # (b, d)
        (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
        (3, 2), (3, 3), (3, 4), (3, 5),
        (4, 2), (4, 3), (4, 4),
    ]

    scaling_results: List[Dict[str, Any]] = []

    mm_runner = Minimax(record_trace=False)
    ab_runner = AlphaBetaPruning(record_trace=False)

    for b, d in configs:
        seed = 42 + b * 10 + d
        base_tree = create_random_tree(branching_factor=b, depth=d, min_val=-20, max_val=50, seed=seed)
        total_tree_nodes = base_tree.count_nodes()
        total_leaves = len(base_tree.get_leaves())

        # Measure Minimax across trials
        mm_times = []
        mm_res = None
        for _ in range(num_trials):
            tree_run = base_tree.clone()
            res = mm_runner.search(tree_run)
            mm_times.append(res.execution_time_ms)
            mm_res = res
        mm_median_time = statistics.median(mm_times)

        # Measure Alpha-Beta across trials
        ab_times = []
        ab_res = None
        for _ in range(num_trials):
            tree_run = base_tree.clone()
            res = ab_runner.search(tree_run)
            ab_times.append(res.execution_time_ms)
            ab_res = res
        ab_median_time = statistics.median(ab_times)

        assert mm_res.root_value == ab_res.root_value, (
            f"Value mismatch at b={b}, d={d}: Minimax={mm_res.root_value}, AB={ab_res.root_value}"
        )

        pruned_nodes = ab_res.pruned_nodes
        efficiency = ((mm_res.nodes_visited - ab_res.nodes_visited) / mm_res.nodes_visited) * 100.0
        speedup = (mm_median_time / ab_median_time) if ab_median_time > 0 else 1.0

        row = {
            "branching_factor": b,
            "depth": d,
            "total_nodes": total_tree_nodes,
            "total_leaves": total_leaves,
            "root_value": mm_res.root_value,
            "mm_nodes_visited": mm_res.nodes_visited,
            "mm_leaf_evals": mm_res.leaf_evaluations,
            "mm_time_ms": round(mm_median_time, 4),
            "ab_nodes_visited": ab_res.nodes_visited,
            "ab_leaf_evals": ab_res.leaf_evaluations,
            "ab_pruned_nodes": pruned_nodes,
            "ab_time_ms": round(ab_median_time, 4),
            "pruning_efficiency_pct": round(efficiency, 2),
            "speedup_factor": round(speedup, 2),
        }
        scaling_results.append(row)
        print(
            f"b={b}, d={d:1d} | Tree Nodes: {total_tree_nodes:5d} | "
            f"MM Visited: {mm_res.nodes_visited:5d} | AB Visited: {ab_res.nodes_visited:5d} | "
            f"Pruned: {pruned_nodes:4d} ({efficiency:5.2f}%) | Speedup: {speedup:5.2f}x"
        )

    # Write scaling results to CSV
    fieldnames = list(scaling_results[0].keys())
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scaling_results)
    print(f"\nSaved scaling benchmark data to: {output_csv}")

    # Ordering impact evaluation
    print("\n" + "=" * 70)
    print("EVALUATING CHILD-ORDERING IMPACT ON ALPHA-BETA PRUNING")
    print("=" * 70)

    ordering_configs = [
        (2, 4), (2, 5), (3, 3), (3, 4), (4, 3)
    ]
    ordering_results: List[Dict[str, Any]] = []

    for b, d in ordering_configs:
        seed = 100 + b * 5 + d
        for ordering in ["best", "random", "worst"]:
            tree = create_random_tree(branching_factor=b, depth=d, min_val=-20, max_val=50, seed=seed)
            if ordering != "random":
                sort_tree_children(tree, ordering)

            tree_mm = tree.clone()
            tree_ab = tree.clone()

            res_mm = mm_runner.search(tree_mm)
            res_ab = ab_runner.search(tree_ab)

            eff = ((res_mm.nodes_visited - res_ab.nodes_visited) / res_mm.nodes_visited) * 100.0
            order_row = {
                "branching_factor": b,
                "depth": d,
                "ordering_strategy": ordering,
                "total_nodes": tree.count_nodes(),
                "mm_nodes_visited": res_mm.nodes_visited,
                "ab_nodes_visited": res_ab.nodes_visited,
                "ab_pruned_nodes": res_ab.pruned_nodes,
                "pruning_efficiency_pct": round(eff, 2),
            }
            ordering_results.append(order_row)
            print(
                f"b={b}, d={d} | Ordering: {ordering:7s} | "
                f"AB Visited: {res_ab.nodes_visited:4d}/{res_mm.nodes_visited:4d} | "
                f"Pruning Efficiency: {eff:5.2f}%"
            )

    order_fieldnames = list(ordering_results[0].keys())
    with open(ordering_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=order_fieldnames)
        writer.writeheader()
        writer.writerows(ordering_results)
    print(f"Saved ordering benchmark data to: {ordering_csv}")

    return scaling_results, ordering_results


if __name__ == "__main__":
    run_benchmark_suite()
