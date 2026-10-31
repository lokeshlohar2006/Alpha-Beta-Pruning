"""
Main Window Module
Integrates the Tree Visualizer, Control Panel, Legend, and Comparison Modal
into a responsive, modern Tkinter application window.
"""

import math
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from core.game_tree import Node
from core.tree_generator import create_predefined_tree, create_random_tree
from algorithms.minimax import Minimax
from algorithms.alpha_beta import AlphaBetaPruning
from algorithms.trace import SearchResult, SearchEvent
from gui.tree_visualizer import TreeVisualizer
from gui.controls import ControlPanel


class MainWindow(tk.Tk):
    """
    Primary application window for the Alpha-Beta Pruning educational simulator.
    """

    def __init__(self):
        super().__init__()

        self.title("Alpha-Beta Pruning Simulator | Adani University – ECSCT24301 Foundation of AI")
        self.geometry("1280x760")
        self.minsize(1050, 650)
        self.configure(bg="#F8FAFC")

        # Current working tree and state
        self.current_tree: Optional[Node] = None
        self.current_algo_name: str = "None"
        self.search_result: Optional[SearchResult] = None
        self.trace_index: int = 0
        self.is_autoplay_active: bool = False
        self._autoplay_job: Optional[str] = None

        # Build UI layout
        self._build_top_banner()
        self._build_main_content()

        # Load initial canonical tree
        self.handle_generate_tree(tree_type="classic_textbook")

    def _build_top_banner(self):
        """Builds header bar with title, academic course badges, and visual legend."""
        banner = tk.Frame(self, bg="#0F172A", padx=16, pady=10)
        banner.pack(fill="x", side="top")

        # Title & Course info
        text_frame = tk.Frame(banner, bg="#0F172A")
        text_frame.pack(side="left")

        title = tk.Label(
            text_frame,
            text="Interactive Alpha-Beta Pruning Simulator",
            font=("Segoe UI", 14, "bold"),
            fg="#F8FAFC",
            bg="#0F172A",
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            text_frame,
            text="Adani University  •  FEST  •  CSE (AI-ML)  •  Course: ECSCT24301 Foundation of AI",
            font=("Segoe UI", 8),
            fg="#94A3B8",
            bg="#0F172A",
        )
        subtitle.pack(anchor="w")

        # Legend Bar
        legend_frame = tk.Frame(banner, bg="#1E293B", padx=10, pady=5, bd=1, relief="ridge")
        legend_frame.pack(side="right")

        legend_items = [
            ("▲ MAX", "#3B82F6"),
            ("▼ MIN", "#EC4899"),
            ("● Leaf", "#64748B"),
            ("Evaluating", "#D97706"),
            ("Evaluated", "#0284C7"),
            ("✕ Cut (Pruned)", "#EF4444"),
            ("— Optimal Path", "#10B981"),
        ]

        for text, color in legend_items:
            item_box = tk.Frame(legend_frame, bg="#1E293B")
            item_box.pack(side="left", padx=6)
            tk.Label(item_box, text=text, font=("Segoe UI", 8, "bold"), fg=color, bg="#1E293B").pack()

    def _build_main_content(self):
        """Constructs split-pane view with visualizer canvas on left and controls on right."""
        content = tk.Frame(self, bg="#F8FAFC")
        content.pack(fill="both", expand=True)

        # Left / Center: Tree Visualizer
        self.visualizer = TreeVisualizer(content, relief="flat", bd=0)
        self.visualizer.pack(side="left", fill="both", expand=True)

        # Right: Sidebar Controls
        self.controls = ControlPanel(
            content,
            on_generate_tree=self.handle_generate_tree,
            on_run_minimax=self.handle_run_minimax,
            on_run_alphabeta=self.handle_run_alphabeta,
            on_next_step=self.handle_next_step,
            on_toggle_autoplay=self.handle_toggle_autoplay,
            on_reset=self.handle_reset,
            on_compare=self.handle_compare,
            width=320,
        )
        self.controls.pack(side="right", fill="y")

    def handle_generate_tree(self, tree_type: str = "classic_textbook", b: int = 2, d: int = 3, seed: Optional[int] = 42):
        """Generates and mounts a new game tree."""
        self._stop_autoplay()
        self.current_algo_name = "None"
        self.search_result = None
        self.trace_index = 0

        if tree_type == "classic_textbook":
            self.current_tree = create_predefined_tree("classic_textbook")
        elif tree_type == "binary_4ply":
            self.current_tree = create_predefined_tree("binary_4ply")
        else:
            self.current_tree = create_random_tree(branching_factor=b, depth=d, seed=seed)

        self.visualizer.set_tree(self.current_tree)
        self.controls.update_metrics({
            "algo": "None",
            "active_node": "-",
            "step_progress": "0 / 0",
            "alpha_beta": "α: -∞ | β: +∞",
            "visited": "0",
            "leaf_evals": "0",
            "pruned": "0",
            "root_val": "-",
        })
        self.controls.set_narration(f"Generated {tree_type} tree ({self.current_tree.count_nodes()} total nodes). Ready to run Minimax or Alpha-Beta.")

    def handle_run_minimax(self):
        """Executes Minimax and prepares trace replay."""
        if not self.current_tree:
            return
        self._stop_autoplay()
        self.current_algo_name = "Minimax"
        runner = Minimax(record_trace=True)
        # Run on clone so original remains clean
        tree_run = self.current_tree.clone()
        self.search_result = runner.search(tree_run)

        # Reset visual tree to fresh state
        self.current_tree.reset_state()
        self.visualizer.set_tree(self.current_tree)
        self.trace_index = 0

        self.controls.update_metrics({
            "algo": "Minimax",
            "step_progress": f"0 / {len(self.search_result.trace)}",
            "visited": f"0 (Total: {self.search_result.nodes_visited})",
            "leaf_evals": f"0 (Total: {self.search_result.leaf_evaluations})",
            "pruned": "0 (Minimax prunes 0)",
            "root_val": f"Pending ({self.search_result.root_value})",
        })
        self.controls.set_narration("Minimax search executed. Use 'Next Step' or 'Auto Play' to step through execution.")

    def handle_run_alphabeta(self):
        """Executes Alpha-Beta Pruning and prepares trace replay."""
        if not self.current_tree:
            return
        self._stop_autoplay()
        self.current_algo_name = "Alpha-Beta"
        runner = AlphaBetaPruning(record_trace=True)
        tree_run = self.current_tree.clone()
        self.search_result = runner.search(tree_run)

        self.current_tree.reset_state()
        self.visualizer.set_tree(self.current_tree)
        self.trace_index = 0

        self.controls.update_metrics({
            "algo": "Alpha-Beta",
            "step_progress": f"0 / {len(self.search_result.trace)}",
            "visited": f"0 (Total: {self.search_result.nodes_visited})",
            "leaf_evals": f"0 (Total: {self.search_result.leaf_evaluations})",
            "pruned": f"0 (Total: {self.search_result.pruned_nodes})",
            "root_val": f"Pending ({self.search_result.root_value})",
        })
        self.controls.set_narration("Alpha-Beta Pruning executed. Step through to observe alpha/beta bounds and cutoffs.")

    def handle_next_step(self):
        """Advances one discrete event in the search trace."""
        if not self.search_result or not self.search_result.trace:
            messagebox.showinfo("Information", "Please run Minimax or Alpha-Beta first.")
            return

        if self.trace_index >= len(self.search_result.trace):
            self._stop_autoplay()
            self.visualizer.highlight_optimal_path()
            self.controls.set_narration(
                f"Search simulation complete! Final root optimal value = {self.search_result.root_value} "
                f"via action {self.search_result.best_move_node_id}."
            )
            return

        event: SearchEvent = self.search_result.trace[self.trace_index]
        self.visualizer.update_step(event)

        # Update metrics panel
        alpha_str = "-∞" if event.alpha == -math.inf else f"{event.alpha:g}"
        beta_str = "+∞" if event.beta == math.inf else f"{event.beta:g}"

        self.controls.update_metrics({
            "active_node": f"{event.node_id} ({'MAX' if event.is_max else 'MIN'})",
            "step_progress": f"{self.trace_index + 1} / {len(self.search_result.trace)}",
            "alpha_beta": f"α: {alpha_str} | β: {beta_str}",
            "root_val": f"{event.value if event.value is not None else 'Evaluating'}",
        })
        self.controls.set_narration(f"Step {self.trace_index + 1}: {event.description}")
        self.trace_index += 1

        if self.trace_index == len(self.search_result.trace):
            self.visualizer.highlight_optimal_path()
            self.controls.update_metrics({
                "root_val": str(self.search_result.root_value),
                "visited": str(self.search_result.nodes_visited),
                "leaf_evals": str(self.search_result.leaf_evaluations),
                "pruned": str(self.search_result.pruned_nodes),
            })

    def handle_toggle_autoplay(self):
        """Toggles continuous playback."""
        if self.is_autoplay_active:
            self._stop_autoplay()
        else:
            if not self.search_result:
                self.handle_run_alphabeta()
            self.is_autoplay_active = True
            self.controls.btn_autoplay.config(text="Pause ⏸", bg="#EF4444")
            self._autoplay_step()

    def _autoplay_step(self):
        """Timer callback for autoplay."""
        if not self.is_autoplay_active:
            return

        if self.search_result and self.trace_index < len(self.search_result.trace):
            self.handle_next_step()
            delay = self.controls.get_autoplay_delay()
            self._autoplay_job = self.after(delay, self._autoplay_step)
        else:
            self._stop_autoplay()

    def _stop_autoplay(self):
        """Stops the autoplay loop."""
        self.is_autoplay_active = False
        if self._autoplay_job:
            self.after_cancel(self._autoplay_job)
            self._autoplay_job = None
        self.controls.btn_autoplay.config(text="Auto Play ▶", bg="#10B981")

    def handle_reset(self):
        """Resets the current tree and rewinds trace to beginning."""
        self._stop_autoplay()
        self.trace_index = 0
        if self.current_tree:
            self.current_tree.reset_state()
            self.visualizer.set_tree(self.current_tree)
            self.controls.update_metrics({
                "active_node": "-",
                "step_progress": "0 / 0",
                "alpha_beta": "α: -∞ | β: +∞",
                "root_val": "-",
            })
            self.controls.set_narration("Tree reset. Ready to run search.")

    def handle_compare(self):
        """Executes both algorithms on identical tree and opens comparison dialog."""
        if not self.current_tree:
            messagebox.showwarning("Warning", "No game tree loaded.")
            return

        # Clone trees for fair, unpolluted runs
        tree_mm = self.current_tree.clone()
        tree_ab = self.current_tree.clone()

        mm_res = Minimax(record_trace=False).search(tree_mm)
        ab_res = AlphaBetaPruning(record_trace=False).search(tree_ab)

        efficiency = ((mm_res.nodes_visited - ab_res.nodes_visited) / mm_res.nodes_visited) * 100.0 if mm_res.nodes_visited > 0 else 0.0

        # Create Comparison Dialog Window
        dlg = tk.Toplevel(self)
        dlg.title("Algorithm Comparison: Minimax vs. Alpha-Beta Pruning")
        dlg.geometry("640x520")
        dlg.minsize(580, 480)
        dlg.configure(bg="#F8FAFC")
        dlg.transient(self)
        dlg.grab_set()

        # Header
        hdr = tk.Frame(dlg, bg="#0F172A", padx=16, pady=12)
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text="Adversarial Search Efficiency Comparison",
            font=("Segoe UI", 12, "bold"),
            fg="#F8FAFC",
            bg="#0F172A",
        ).pack(anchor="w")
        tk.Label(
            hdr,
            text=f"Evaluated on {self.current_tree.count_nodes()} total tree nodes ({len(self.current_tree.get_leaves())} leaves)",
            font=("Segoe UI", 8),
            fg="#94A3B8",
            bg="#0F172A",
        ).pack(anchor="w")

        # Table Frame
        tbl_frame = tk.Frame(dlg, bg="#F8FAFC", padx=20, pady=15)
        tbl_frame.pack(fill="x")

        # Table Columns
        headers = ["Metric / Parameter", "Standard Minimax", "Alpha-Beta Pruning", "Difference / Gain"]
        for col, h in enumerate(headers):
            tk.Label(
                tbl_frame,
                text=h,
                font=("Segoe UI", 9, "bold"),
                bg="#E2E8F0",
                fg="#0F172A",
                padx=8,
                pady=6,
                relief="solid",
                bd=1,
            ).grid(row=0, column=col, sticky="nsew")

        rows = [
            ("Final Root Utility", f"{mm_res.root_value}", f"{ab_res.root_value}", "Identical (100% optimal)"),
            ("Optimal Root Move", f"{mm_res.best_move_node_id}", f"{ab_res.best_move_node_id}", "Identical choice"),
            ("Nodes Visited", f"{mm_res.nodes_visited}", f"{ab_res.nodes_visited}", f"-{mm_res.nodes_visited - ab_res.nodes_visited} nodes"),
            ("Leaf Evaluations", f"{mm_res.leaf_evaluations}", f"{ab_res.leaf_evaluations}", f"-{mm_res.leaf_evaluations - ab_res.leaf_evaluations} leaves"),
            ("Pruned Nodes", "0", f"{ab_res.pruned_nodes}", f"{ab_res.pruned_nodes} bypassed"),
            ("Execution Time (ms)", f"{mm_res.execution_time_ms:.3f} ms", f"{ab_res.execution_time_ms:.3f} ms", f"{mm_res.execution_time_ms - ab_res.execution_time_ms:+.3f} ms"),
        ]

        for r_idx, (m, val_mm, val_ab, diff) in enumerate(rows, 1):
            bg = "#FFFFFF" if r_idx % 2 == 1 else "#F1F5F9"
            for c_idx, val in enumerate([m, val_mm, val_ab, diff]):
                tk.Label(
                    tbl_frame,
                    text=val,
                    font=("Segoe UI", 8),
                    bg=bg,
                    fg="#1E293B",
                    padx=8,
                    pady=4,
                    relief="solid",
                    bd=1,
                ).grid(row=r_idx, column=c_idx, sticky="nsew")

        for col in range(4):
            tbl_frame.columnconfigure(col, weight=1)

        # Efficiency Card
        eff_card = tk.LabelFrame(
            dlg,
            text=" Pruning Efficiency Metric ",
            font=("Segoe UI", 9, "bold"),
            bg="#F8FAFC",
            fg="#0F172A",
            padx=15,
            pady=10,
        )
        eff_card.pack(fill="x", padx=20, pady=(0, 10))

        formula_text = (
            "Formula: Efficiency = ((Minimax Visited - AlphaBeta Visited) / Minimax Visited) × 100\n"
            f"Calculated: (({mm_res.nodes_visited} - {ab_res.nodes_visited}) / {mm_res.nodes_visited}) × 100 = {efficiency:.2f}%\n\n"
            "Academic Note: Both algorithms guarantee returning the identical theoretical minimax root value. "
            "Alpha-Beta achieves this while skipping subtrees whose bounds prove they cannot affect the outcome. "
            "Pruning efficiency is highly sensitive to child move ordering."
        )
        tk.Label(
            eff_card,
            text=formula_text,
            font=("Segoe UI", 8),
            justify="left",
            bg="#F8FAFC",
            fg="#334155",
        ).pack(anchor="w")

        # Close button
        tk.Button(
            dlg,
            text="Close",
            bg="#0F172A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=4,
            command=dlg.destroy,
        ).pack(pady=(0, 15))
