"""
Controls & Metrics Dashboard Module
Provides intuitive simulation controls, generation configuration,
educational execution narration, and live search metrics.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ControlPanel(tk.Frame):
    """
    Sidebar / Control panel providing tree configuration, simulation stepping,
    playback speed adjustment, and live metrics inspection.
    """

    def __init__(
        self,
        master,
        on_generate_tree: Callable,
        on_run_minimax: Callable,
        on_run_alphabeta: Callable,
        on_next_step: Callable,
        on_toggle_autoplay: Callable,
        on_reset: Callable,
        on_compare: Callable,
        **kwargs,
    ):
        super().__init__(master, bg="#F1F5F9", padx=15, pady=15, **kwargs)

        self.on_generate_tree = on_generate_tree
        self.on_run_minimax = on_run_minimax
        self.on_run_alphabeta = on_run_alphabeta
        self.on_next_step = on_next_step
        self.on_toggle_autoplay = on_toggle_autoplay
        self.on_reset = on_reset
        self.on_compare = on_compare

        self._create_widgets()

    def _create_widgets(self):
        # Header
        title = tk.Label(
            self,
            text="Control & Simulation",
            font=("Segoe UI", 13, "bold"),
            bg="#F1F5F9",
            fg="#0F172A",
        )
        title.pack(anchor="w", pady=(0, 10))

        # -------------------------------------------------------------
        # Section 1: Tree Generation
        # -------------------------------------------------------------
        gen_group = tk.LabelFrame(
            self,
            text=" 1. Tree Configuration ",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg="#1E293B",
            padx=10,
            pady=8,
        )
        gen_group.pack(fill="x", pady=(0, 10))

        # Tree Variant
        tk.Label(gen_group, text="Type:", bg="#F1F5F9", font=("Segoe UI", 8)).grid(row=0, column=0, sticky="w", pady=2)
        self.tree_type_var = tk.StringVar(value="classic_textbook")
        tree_type_cb = ttk.Combobox(
            gen_group,
            textvariable=self.tree_type_var,
            values=["classic_textbook", "binary_4ply", "random"],
            state="readonly",
            width=16,
        )
        tree_type_cb.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        tree_type_cb.bind("<<ComboboxSelected>>", self._on_tree_type_changed)

        # Branching factor (b)
        tk.Label(gen_group, text="Branching (b):", bg="#F1F5F9", font=("Segoe UI", 8)).grid(row=1, column=0, sticky="w", pady=2)
        self.branching_var = tk.IntVar(value=3)
        self.branching_sb = tk.Spinbox(gen_group, from_=2, to=4, textvariable=self.branching_var, width=5)
        self.branching_sb.grid(row=1, column=1, sticky="w", pady=2, padx=5)

        # Depth (d)
        tk.Label(gen_group, text="Depth (d):", bg="#F1F5F9", font=("Segoe UI", 8)).grid(row=2, column=0, sticky="w", pady=2)
        self.depth_var = tk.IntVar(value=3)
        self.depth_sb = tk.Spinbox(gen_group, from_=2, to=4, textvariable=self.depth_var, width=5)
        self.depth_sb.grid(row=2, column=1, sticky="w", pady=2, padx=5)

        # Seed
        tk.Label(gen_group, text="Seed (opt):", bg="#F1F5F9", font=("Segoe UI", 8)).grid(row=3, column=0, sticky="w", pady=2)
        self.seed_var = tk.StringVar(value="42")
        self.seed_entry = tk.Entry(gen_group, textvariable=self.seed_var, width=8)
        self.seed_entry.grid(row=3, column=1, sticky="w", pady=2, padx=5)

        # Generate Button
        btn_gen = tk.Button(
            gen_group,
            text="Generate Tree",
            bg="#2563EB",
            fg="white",
            activebackground="#1D4ED8",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._handle_generate,
        )
        btn_gen.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 2))

        # -------------------------------------------------------------
        # Section 2: Algorithm Mode
        # -------------------------------------------------------------
        algo_group = tk.LabelFrame(
            self,
            text=" 2. Search Algorithm ",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg="#1E293B",
            padx=10,
            pady=8,
        )
        algo_group.pack(fill="x", pady=(0, 10))

        btn_mm = tk.Button(
            algo_group,
            text="Run Minimax",
            bg="#475569",
            fg="white",
            activebackground="#334155",
            activeforeground="white",
            font=("Segoe UI", 9),
            relief="flat",
            cursor="hand2",
            command=self.on_run_minimax,
        )
        btn_mm.pack(fill="x", pady=2)

        btn_ab = tk.Button(
            algo_group,
            text="Run Alpha-Beta Pruning",
            bg="#0D9488",
            fg="white",
            activebackground="#0F766E",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.on_run_alphabeta,
        )
        btn_ab.pack(fill="x", pady=2)

        # -------------------------------------------------------------
        # Section 3: Step-by-Step Simulation Controls
        # -------------------------------------------------------------
        sim_group = tk.LabelFrame(
            self,
            text=" 3. Step Simulation Controls ",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg="#1E293B",
            padx=10,
            pady=8,
        )
        sim_group.pack(fill="x", pady=(0, 10))

        step_btn_frame = tk.Frame(sim_group, bg="#F1F5F9")
        step_btn_frame.pack(fill="x", pady=2)

        self.btn_next = tk.Button(
            step_btn_frame,
            text="Next Step ▶",
            bg="#3B82F6",
            fg="white",
            activebackground="#2563EB",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.on_next_step,
        )
        self.btn_next.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.btn_autoplay = tk.Button(
            step_btn_frame,
            text="Auto Play",
            bg="#10B981",
            fg="white",
            activebackground="#059669",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.on_toggle_autoplay,
        )
        self.btn_autoplay.pack(side="left", expand=True, fill="x")

        # Speed slider
        speed_frame = tk.Frame(sim_group, bg="#F1F5F9")
        speed_frame.pack(fill="x", pady=(6, 2))
        tk.Label(speed_frame, text="Speed (Delay ms):", bg="#F1F5F9", font=("Segoe UI", 8)).pack(side="left")
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=100,
            to=1200,
            orient="horizontal",
            bg="#F1F5F9",
            highlightthickness=0,
            length=110,
        )
        self.speed_scale.set(400)
        self.speed_scale.pack(side="right")

        btn_reset = tk.Button(
            sim_group,
            text="Reset Simulation ↺",
            bg="#E2E8F0",
            fg="#334155",
            font=("Segoe UI", 8),
            relief="flat",
            cursor="hand2",
            command=self.on_reset,
        )
        btn_reset.pack(fill="x", pady=(4, 0))

        # -------------------------------------------------------------
        # Section 4: Metrics Dashboard
        # -------------------------------------------------------------
        metrics_group = tk.LabelFrame(
            self,
            text=" 4. Search Metrics ",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg="#1E293B",
            padx=10,
            pady=8,
        )
        metrics_group.pack(fill="x", pady=(0, 10))

        self.metric_labels = {}
        metrics_meta = [
            ("Algorithm:", "algo", "None"),
            ("Active Node:", "active_node", "-"),
            ("Step Progress:", "step_progress", "0 / 0"),
            ("Current α / β:", "alpha_beta", "α: -∞ | β: +∞"),
            ("Visited Nodes:", "visited", "0"),
            ("Leaf Evaluations:", "leaf_evals", "0"),
            ("Pruned Nodes:", "pruned", "0"),
            ("Final Root Utility:", "root_val", "-"),
        ]

        for i, (label_text, key, initial) in enumerate(metrics_meta):
            tk.Label(metrics_group, text=label_text, bg="#F1F5F9", font=("Segoe UI", 8, "bold")).grid(
                row=i, column=0, sticky="w", pady=1
            )
            lbl = tk.Label(metrics_group, text=initial, bg="#F1F5F9", font=("Segoe UI", 8), fg="#0284C7")
            lbl.grid(row=i, column=1, sticky="e", pady=1)
            self.metric_labels[key] = lbl

        metrics_group.columnconfigure(1, weight=1)

        # -------------------------------------------------------------
        # Section 5: Educational Step Log
        # -------------------------------------------------------------
        log_group = tk.LabelFrame(
            self,
            text=" Step Narration ",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg="#1E293B",
            padx=6,
            pady=6,
        )
        log_group.pack(fill="both", expand=True, pady=(0, 10))

        self.log_text = tk.Text(
            log_group,
            height=5,
            width=26,
            wrap="word",
            bg="#FFFFFF",
            font=("Segoe UI", 8),
            relief="solid",
            bd=1,
        )
        self.log_text.pack(fill="both", expand=True)

        # -------------------------------------------------------------
        # Section 6: Algorithm Comparison Button
        # -------------------------------------------------------------
        btn_compare = tk.Button(
            self,
            text="Compare Algorithms (Side-by-Side)",
            bg="#8B5CF6",
            fg="white",
            activebackground="#7C3AED",
            activeforeground="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.on_compare,
        )
        btn_compare.pack(fill="x")

        # Initial widget state
        self._on_tree_type_changed()

    def _on_tree_type_changed(self, event=None):
        """Enables or disables spinboxes depending on whether tree is random or predefined."""
        t_type = self.tree_type_var.get()
        state = "normal" if t_type == "random" else "disabled"
        self.branching_sb.config(state=state)
        self.depth_sb.config(state=state)
        self.seed_entry.config(state=state)

    def _handle_generate(self):
        """Extracts configuration and delegates to callback."""
        t_type = self.tree_type_var.get()
        b = self.branching_var.get()
        d = self.depth_var.get()
        seed_str = self.seed_var.get().strip()
        seed = int(seed_str) if seed_str.isdigit() else None
        self.on_generate_tree(t_type, b, d, seed)

    def update_metrics(self, data: dict):
        """Updates metric dashboard labels."""
        for key, val in data.items():
            if key in self.metric_labels:
                self.metric_labels[key].config(text=str(val))

    def set_narration(self, text: str):
        """Sets the educational narration message."""
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert(tk.END, text)

    def get_autoplay_delay(self) -> int:
        """Returns the autoplay step delay in milliseconds."""
        return self.speed_scale.get()
