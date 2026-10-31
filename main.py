"""
Interactive Alpha-Beta Pruning Simulator
Adani University - ECSCT24301 Foundation of AI
Applied AI Project Track

Main entry point for launching the graphical user interface or running automated utilities.
"""

import sys
import argparse


def launch_gui():
    """Launches the Tkinter Graphical User Interface."""
    from gui.main_window import MainWindow

    app = MainWindow()
    app.mainloop()


def run_cli_demo():
    """Runs a quick command-line demonstration of Minimax vs. Alpha-Beta Pruning."""
    from core.tree_generator import create_predefined_tree
    from algorithms.minimax import Minimax
    from algorithms.alpha_beta import AlphaBetaPruning

    print("=" * 70)
    print("ALPHA-BETA PRUNING SIMULATOR (CLI DEMO)")
    print("Course: ECSCT24301 Foundation of AI | Adani University")
    print("=" * 70)

    tree_mm = create_predefined_tree("classic_textbook")
    tree_ab = create_predefined_tree("classic_textbook")

    mm = Minimax(record_trace=False).search(tree_mm)
    ab = AlphaBetaPruning(record_trace=False).search(tree_ab)

    efficiency = ((mm.nodes_visited - ab.nodes_visited) / mm.nodes_visited) * 100

    print("\n--- RESULTS ON CLASSIC TEXTBOOK TREE ---")
    print(f"{'Metric':<28} | {'Minimax':<15} | {'Alpha-Beta':<15}")
    print("-" * 65)
    print(f"{'Optimal Root Value':<28} | {mm.root_value:<15} | {ab.root_value:<15}")
    print(f"{'Best Action Choice':<28} | {str(mm.best_move_node_id):<15} | {str(ab.best_move_node_id):<15}")
    print(f"{'Nodes Visited':<28} | {mm.nodes_visited:<15} | {ab.nodes_visited:<15}")
    print(f"{'Leaf Evaluations':<28} | {mm.leaf_evaluations:<15} | {ab.leaf_evaluations:<15}")
    print(f"{'Pruned Nodes':<28} | {0:<15} | {ab.pruned_nodes:<15}")
    print(f"{'Execution Time (ms)':<28} | {mm.execution_time_ms:<15.4f} | {ab.execution_time_ms:<15.4f}")
    print("-" * 65)
    print(f"Calculated Pruning Efficiency: {efficiency:.2f}%\n")


def main():
    parser = argparse.ArgumentParser(
        description="Interactive Alpha-Beta Pruning Simulator for Game-Tree Search",
    )
    parser.add_argument("--cli", action="store_true", help="Run a quick command-line search demonstration")
    parser.add_argument("--benchmark", action="store_true", help="Execute the empirical benchmark suite")
    parser.add_argument("--charts", action="store_true", help="Generate publication charts from benchmark data")
    parser.add_argument("--test", action="store_true", help="Execute the full unittest test suite")

    args = parser.parse_args()

    if args.cli:
        run_cli_demo()
    elif args.benchmark:
        from benchmarks.benchmark import run_benchmark_suite
        run_benchmark_suite()
    elif args.charts:
        from benchmarks.generate_charts import main as generate_charts_main
        generate_charts_main()
    elif args.test:
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover("tests")
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
    else:
        launch_gui()


if __name__ == "__main__":
    main()
