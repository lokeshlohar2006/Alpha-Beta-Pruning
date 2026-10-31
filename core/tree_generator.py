"""
Tree Generator Module
Provides utilities to create predefined, canonical, and randomly generated game trees
for adversarial search simulation and benchmarking.
"""

import random
from typing import Optional, List
from core.game_tree import Node


def create_predefined_tree(variant: str = "classic_textbook") -> Node:
    """
    Creates a standard, canonical game tree frequently used in AI textbooks
    (e.g., Russell & Norvig / standard FAI lectures) to illustrate alpha-beta pruning.

    Variants:
        - "classic_textbook": Branching factor 3, Depth 3 (Root MAX -> 3 MIN nodes -> 3 leaves each).
          Leaf values:
            Branch 1 (A): [3, 12, 8] -> MIN picks 3. (alpha becomes 3)
            Branch 2 (B): [2, 4, 6]  -> First leaf is 2; 2 <= alpha=3, so remaining [4, 6] pruned!
            Branch 3 (C): [14, 5, 2] -> Leaf 14, then 5, then 2 -> MIN picks 2.
          Root chooses max(3, 2) = 3.
        - "binary_4ply": Branching factor 2, Depth 4 (Root MAX -> 16 leaves).
          Leaf values: [10, 9, 14, 18, 5, 4, 50, 3, 7, 12, -2, 1, 8, 6, 15, 20]
          Produces distinct alpha and beta cutoffs at multiple levels.
    """
    if variant == "binary_4ply":
        root = Node(node_id="Root", name="Root (MAX)", depth=0, is_max=True)
        leaf_values = [10, 9, 14, 18, 5, 4, 50, 3, 7, 12, -2, 1, 8, 6, 15, 20]
        leaf_idx = 0

        # Construct full binary tree of depth 4 (levels 0, 1, 2, 3, 4)
        current_level = [root]
        for depth in range(1, 5):
            next_level = []
            is_max = (depth % 2 == 0)
            for parent in current_level:
                for child_idx in range(2):
                    node_id = f"{parent.node_id}_{child_idx + 1}"
                    role = "MAX" if is_max else "MIN"
                    name = f"N_{node_id[-5:]} ({role})"
                    if depth == 4:
                        val = leaf_values[leaf_idx]
                        leaf_idx += 1
                        child = Node(node_id=node_id, name=f"Leaf[{val}]", depth=depth, is_max=is_max, value=val)
                    else:
                        child = Node(node_id=node_id, name=name, depth=depth, is_max=is_max)
                    parent.add_child(child)
                    next_level.append(child)
            current_level = next_level
        calculate_tree_layout(root)
        return root

    # Default: "classic_textbook" (Russell & Norvig Figure 5.5 variant)
    root = Node(node_id="Root", name="Root (MAX)", depth=0, is_max=True)

    # 3 MIN children
    child_a = Node(node_id="A", name="A (MIN)", depth=1, is_max=False)
    child_b = Node(node_id="B", name="B (MIN)", depth=1, is_max=False)
    child_c = Node(node_id="C", name="C (MIN)", depth=1, is_max=False)
    root.add_child(child_a)
    root.add_child(child_b)
    root.add_child(child_c)

    # Leaves for A: [3, 12, 8]
    a_vals = [3, 12, 8]
    for i, val in enumerate(a_vals, 1):
        leaf = Node(node_id=f"A{i}", name=f"L_{val}", depth=2, is_max=True, value=val)
        child_a.add_child(leaf)

    # Leaves for B: [2, 4, 6] (Note: 4 and 6 will be pruned)
    b_vals = [2, 4, 6]
    for i, val in enumerate(b_vals, 1):
        leaf = Node(node_id=f"B{i}", name=f"L_{val}", depth=2, is_max=True, value=val)
        child_b.add_child(leaf)

    # Leaves for C: [14, 5, 2]
    c_vals = [14, 5, 2]
    for i, val in enumerate(c_vals, 1):
        leaf = Node(node_id=f"C{i}", name=f"L_{val}", depth=2, is_max=True, value=val)
        child_c.add_child(leaf)

    calculate_tree_layout(root)
    return root


def create_random_tree(
    branching_factor: int = 2,
    depth: int = 3,
    min_val: int = -10,
    max_val: int = 20,
    seed: Optional[int] = None,
) -> Node:
    """
    Generates a deterministic or pseudorandom adversarial game tree with configurable
    depth and branching factor.

    Args:
        branching_factor (int): Uniform number of actions/children per internal state.
        depth (int): Maximum depth (terminal leaf ply).
        min_val (int): Minimum possible integer utility value.
        max_val (int): Maximum possible integer utility value.
        seed (Optional[int]): Random seed for deterministic reproducibility.

    Returns:
        Node: Root node of the freshly generated game tree.
    """
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    root = Node(node_id="Root", name="Root (MAX)", depth=0, is_max=True)

    def build_subtree(parent: Node, current_depth: int) -> None:
        if current_depth >= depth:
            return

        is_next_max = ((current_depth + 1) % 2 == 0)
        role_label = "MAX" if is_next_max else "MIN"

        for i in range(branching_factor):
            child_id = f"{parent.node_id}_{i + 1}"
            if current_depth + 1 == depth:
                val = rng.randint(min_val, max_val)
                child = Node(
                    node_id=child_id,
                    name=f"L_{val}",
                    depth=current_depth + 1,
                    is_max=is_next_max,
                    value=val,
                )
            else:
                child = Node(
                    node_id=child_id,
                    name=f"{child_id[-6:]} ({role_label})",
                    depth=current_depth + 1,
                    is_max=is_next_max,
                )
                build_subtree(child, current_depth + 1)

            parent.add_child(child)

    build_subtree(root, 0)
    calculate_tree_layout(root)
    return root


def calculate_tree_layout(
    root: Node,
    width: float = 1000.0,
    height: float = 500.0,
    top_margin: float = 50.0,
    bottom_margin: float = 50.0,
    side_margin: float = 40.0,
) -> None:
    """
    Computes balanced (x, y) coordinates for all nodes in the tree for 2D rendering.
    Leaf nodes are spaced evenly across the available horizontal canvas width.
    Each parent's x-coordinate is computed as the midpoint of its children.
    """
    max_d = root.max_depth()
    usable_height = height - top_margin - bottom_margin
    y_step = usable_height / max_d if max_d > 0 else 0

    leaves = root.get_leaves()
    num_leaves = len(leaves)
    usable_width = width - 2 * side_margin

    if num_leaves <= 1:
        leaf_step = 0
    else:
        leaf_step = usable_width / (num_leaves - 1)

    for i, leaf in enumerate(leaves):
        leaf.x = side_margin + i * leaf_step
        leaf.y = top_margin + leaf.depth * y_step

    # Post-order traversal to position internal nodes as the center of their children
    def assign_internal_positions(node: Node) -> None:
        for child in node.children:
            if not child.is_leaf:
                assign_internal_positions(child)

        if not node.is_leaf:
            node.x = sum(child.x for child in node.children) / len(node.children)
            node.y = top_margin + node.depth * y_step

    assign_internal_positions(root)
