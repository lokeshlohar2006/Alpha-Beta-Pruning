"""
Tree Visualizer Module
Interactive Tkinter Canvas renderer that displays the game tree,
animates state changes, highlights alpha-beta cutoffs, and illuminates optimal decision paths.
"""

import math
import tkinter as tk
from typing import Optional, Dict, Set, List
from core.game_tree import Node
from algorithms.trace import SearchEvent


class TreeVisualizer(tk.Frame):
    """
    Tkinter Canvas widget dedicated to rendering the adversarial game tree.
    Supports pan, dynamic scaling, visual status highlights, and cut markers.
    """

    # Modern curated color palette
    COLOR_BG = "#F8FAFC"
    COLOR_EDGE_DEFAULT = "#94A3B8"
    COLOR_EDGE_PRUNED = "#EF4444"
    COLOR_EDGE_OPTIMAL = "#10B981"

    # Node Fill & Border Colors by Status
    STATUS_STYLES = {
        "unevaluated": {"fill": "#FFFFFF", "outline": "#CBD5E1", "text": "#334155", "width": 2},
        "evaluating": {"fill": "#FEF3C7", "outline": "#D97706", "text": "#78350F", "width": 3},
        "evaluated": {"fill": "#E0F2FE", "outline": "#0284C7", "text": "#0369A1", "width": 2},
        "pruned": {"fill": "#FEE2E2", "outline": "#DC2626", "text": "#991B1B", "width": 2, "dash": (3, 3)},
    }

    # Accent colors for MAX and MIN roles
    COLOR_MAX_ACCENT = "#3B82F6"  # Blue
    COLOR_MIN_ACCENT = "#EC4899"  # Pink / Magenta

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.canvas = tk.Canvas(self, bg=self.COLOR_BG, highlightthickness=0)
        self.v_scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)

        self.canvas.configure(xscrollcommand=self.h_scrollbar.set, yscrollcommand=self.v_scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.root_node: Optional[Node] = None
        self.active_node_id: Optional[str] = None
        self.optimal_path_node_ids: Set[str] = set()
        self.pruned_node_ids: Set[str] = set()

        # Canvas node coordinates cache
        self.node_coords: Dict[str, Node] = {}

        # Bindings for resizing
        self.canvas.bind("<Configure>", lambda e: self.redraw())

    def set_tree(self, root: Node) -> None:
        """Sets a new tree and redraws."""
        self.root_node = root
        self.active_node_id = None
        self.optimal_path_node_ids.clear()
        self.pruned_node_ids.clear()
        self.redraw()

    def update_step(self, event: SearchEvent) -> None:
        """Applies a discrete step event and updates the visual representation."""
        if not self.root_node:
            return

        self.active_node_id = event.node_id

        # Update node internal state
        target_node = self._find_node(self.root_node, event.node_id)
        if target_node:
            if event.event_type == "VISIT":
                target_node.status = "evaluating"
            elif event.event_type in ("UPDATE_VAL", "UPDATE_BOUNDS"):
                target_node.status = "evaluating"
                if event.value is not None:
                    target_node.value = event.value
            elif event.event_type in ("FINISH_NODE", "EVAL_LEAF"):
                target_node.status = "evaluated"
                if event.value is not None:
                    target_node.value = event.value
            elif event.event_type == "PRUNE":
                for pid in event.pruned_node_ids:
                    pnode = self._find_node(self.root_node, pid)
                    if pnode:
                        pnode.status = "pruned"
                        self.pruned_node_ids.add(pid)

            target_node.alpha = event.alpha
            target_node.beta = event.beta

        if event.event_type == "DECISION":
            self._highlight_optimal_path(self.root_node)

        self.redraw()

    def highlight_optimal_path(self) -> None:
        """Traces the optimal best_child path from root down to leaf."""
        if self.root_node:
            self._highlight_optimal_path(self.root_node)
            self.redraw()

    def _highlight_optimal_path(self, root: Node) -> None:
        """Recursively builds the set of optimal node IDs."""
        self.optimal_path_node_ids.clear()
        curr = root
        while curr:
            self.optimal_path_node_ids.add(curr.node_id)
            curr = curr.best_child

    def _find_node(self, current: Node, target_id: str) -> Optional[Node]:
        """Finds node by ID."""
        if current.node_id == target_id:
            return current
        for child in current.children:
            found = self._find_node(child, target_id)
            if found:
                return found
        return None

    def redraw(self) -> None:
        """Re-renders the tree onto the canvas."""
        self.canvas.delete("all")
        if not self.root_node:
            self.canvas.create_text(
                self.canvas.winfo_width() / 2 or 400,
                self.canvas.winfo_height() / 2 or 250,
                text="No Game Tree Loaded.\nClick 'Generate Tree' to begin.",
                font=("Segoe UI", 14, "bold"),
                fill="#94A3B8",
                justify="center",
            )
            return

        width = max(self.canvas.winfo_width(), 950)
        height = max(self.canvas.winfo_height(), 520)

        # Dynamic layout calculation based on canvas size and tree depth/leaves
        num_leaves = len(self.root_node.get_leaves())
        req_width = max(width, num_leaves * 75 + 100)
        req_height = max(height, (self.root_node.max_depth() + 1) * 110 + 100)

        self.canvas.config(scrollregion=(0, 0, req_width, req_height))

        # Recompute positions for canvas dimensions
        from core.tree_generator import calculate_tree_layout
        calculate_tree_layout(self.root_node, width=req_width, height=req_height, top_margin=60, bottom_margin=60, side_margin=60)

        # 1. Draw Edges first so nodes appear on top
        self._draw_edges(self.root_node)

        # 2. Draw Nodes
        self._draw_nodes(self.root_node)

    def _draw_edges(self, node: Node) -> None:
        """Draws connecting lines and cutoff marks."""
        for child in node.children:
            is_optimal = (
                node.node_id in self.optimal_path_node_ids
                and child.node_id in self.optimal_path_node_ids
            )
            is_pruned = child.status == "pruned" or child.node_id in self.pruned_node_ids

            if is_optimal:
                line_color = self.COLOR_EDGE_OPTIMAL
                line_width = 3
                dash = None
            elif is_pruned:
                line_color = self.COLOR_EDGE_PRUNED
                line_width = 2
                dash = (4, 4)
            else:
                line_color = self.COLOR_EDGE_DEFAULT
                line_width = 2
                dash = None

            # Draw edge line
            self.canvas.create_line(
                node.x, node.y, child.x, child.y,
                fill=line_color,
                width=line_width,
                dash=dash,
                smooth=True,
            )

            # Draw Cut Marker if branch is pruned
            if is_pruned:
                mid_x = (node.x + child.x) / 2
                mid_y = (node.y + child.y) / 2
                # Draw scissors / red cross indicator
                self.canvas.create_oval(
                    mid_x - 10, mid_y - 10, mid_x + 10, mid_y + 10,
                    fill="#FEE2E2", outline="#EF4444", width=2
                )
                self.canvas.create_text(
                    mid_x, mid_y,
                    text="✕", fill="#DC2626",
                    font=("Segoe UI", 10, "bold")
                )

            # Recursive traversal
            self._draw_edges(child)

    def _draw_nodes(self, node: Node) -> None:
        """Renders the graphical node representation (MAX/MIN/Leaf), badges, and values."""
        x, y = node.x, node.y
        is_active = (node.node_id == self.active_node_id)
        is_optimal = (node.node_id == self.optimal_path_node_ids)

        style = self.STATUS_STYLES.get(node.status, self.STATUS_STYLES["unevaluated"]).copy()
        if is_active:
            style = self.STATUS_STYLES["evaluating"]

        radius = 24 if not node.is_leaf else 20

        # Draw Node Geometry
        if node.is_leaf:
            # Leaf node: Rounded rectangle or circle
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                fill=style["fill"],
                outline=style["outline"],
                width=style["width"] + (2 if is_active else 0),
            )
        elif node.is_max:
            # MAX Node: Equilateral upward-pointing triangle
            side = radius * 2.2
            h = (math.sqrt(3) / 2) * side
            points = [
                x, y - (2/3) * h,           # Top apex
                x - side / 2, y + (1/3) * h, # Bottom-left
                x + side / 2, y + (1/3) * h, # Bottom-right
            ]
            self.canvas.create_polygon(
                points,
                fill=style["fill"],
                outline=style["outline"],
                width=style["width"] + (2 if is_active else 0),
            )
        else:
            # MIN Node: Equilateral downward-pointing triangle
            side = radius * 2.2
            h = (math.sqrt(3) / 2) * side
            points = [
                x - side / 2, y - (1/3) * h, # Top-left
                x + side / 2, y - (1/3) * h, # Top-right
                x, y + (2/3) * h,           # Bottom apex
            ]
            self.canvas.create_polygon(
                points,
                fill=style["fill"],
                outline=style["outline"],
                width=style["width"] + (2 if is_active else 0),
            )

        # Node Label / Value inside or centered
        if node.is_leaf:
            val_text = f"{int(node.value) if node.value is not None and node.value.is_integer() else node.value}"
            self.canvas.create_text(
                x, y,
                text=val_text,
                fill=style["text"],
                font=("Segoe UI", 11, "bold"),
            )
        else:
            val_text = f"{int(node.value) if node.value is not None and isinstance(node.value, (int, float)) and node.value.is_integer() else (node.value if node.value is not None else '?')}"
            self.canvas.create_text(
                x, y,
                text=val_text,
                fill=style["text"],
                font=("Segoe UI", 10, "bold"),
            )

        # Draw Node Name & Role Header
        role_label = "MAX" if node.is_max else "MIN"
        role_color = self.COLOR_MAX_ACCENT if node.is_max else self.COLOR_MIN_ACCENT
        if not node.is_leaf:
            self.canvas.create_text(
                x, y - radius - 12,
                text=f"{node.name} [{role_label}]",
                fill=role_color,
                font=("Segoe UI", 8, "bold"),
            )
        else:
            self.canvas.create_text(
                x, y - radius - 10,
                text=node.name,
                fill="#64748B",
                font=("Segoe UI", 8),
            )

        # Draw Alpha / Beta Badge under internal nodes
        if not node.is_leaf and (node.alpha != -math.inf or node.beta != math.inf or is_active or node.status == "evaluated"):
            alpha_str = "-∞" if node.alpha == -math.inf else f"{node.alpha:g}"
            beta_str = "+∞" if node.beta == math.inf else f"{node.beta:g}"
            ab_text = f"α:{alpha_str} β:{beta_str}"
            self.canvas.create_text(
                x, y + radius + 12,
                text=ab_text,
                fill="#475569",
                font=("Consolas", 8, "bold"),
            )

        # Recursively draw children
        for child in node.children:
            self._draw_nodes(child)
