"""
Core Game Tree Module
Defines the Node data structure representing states in an adversarial game tree.
"""

from typing import List, Optional, Any
import copy
import math


class Node:
    """
    Represents a single state/node in a two-player zero-sum adversarial game tree.

    Attributes:
        node_id (str): Unique identifier for the node.
        name (str): Human-readable label (e.g., 'Root', 'A', 'B', etc.).
        depth (int): Tree depth (root is at depth 0).
        is_max (bool): True if the node belongs to the MAX player, False for MIN.
        value (Optional[float]): Static utility value (for leaves) or backed-up minimax value.
        children (List['Node']): Ordered list of successor child nodes.
        parent (Optional['Node']): Reference to parent node (None for root).
        alpha (float): Best value achievable by MAX along path to root.
        beta (float): Best value achievable by MIN along path to root.
        status (str): Current status ('unevaluated', 'evaluating', 'evaluated', 'pruned').
        best_child (Optional['Node']): The successor child yielding the optimal minimax value.
        x (float): Horizontal canvas coordinate for visual rendering.
        y (float): Vertical canvas coordinate for visual rendering.
    """

    def __init__(
        self,
        node_id: str,
        name: str = "",
        depth: int = 0,
        is_max: bool = True,
        value: Optional[float] = None,
        parent: Optional['Node'] = None,
    ):
        self.node_id = node_id
        self.name = name if name else node_id
        self.depth = depth
        self.is_max = is_max
        self.value = value
        self.children: List['Node'] = []
        self.parent = parent
        self.alpha = -math.inf
        self.beta = math.inf
        self.status = "unevaluated"
        self.best_child: Optional['Node'] = None
        self.x: float = 0.0
        self.y: float = 0.0

    @property
    def is_leaf(self) -> bool:
        """Returns True if the node has no children (terminal/leaf state)."""
        return len(self.children) == 0

    def add_child(self, child: 'Node') -> None:
        """Adds a child node and links its parent reference."""
        child.parent = self
        self.children.append(child)

    def reset_state(self) -> None:
        """
        Recursively resets dynamic search variables (alpha, beta, status, values for internal nodes)
        while preserving tree topology and static leaf utilities.
        """
        self.alpha = -math.inf
        self.beta = math.inf
        self.status = "unevaluated"
        self.best_child = None
        if not self.is_leaf:
            self.value = None

        for child in self.children:
            child.reset_state()

    def clone(self) -> 'Node':
        """
        Creates a deep clone of the tree rooted at this node,
        preserving topology and leaf values with fresh node references.
        """
        new_node = Node(
            node_id=self.node_id,
            name=self.name,
            depth=self.depth,
            is_max=self.is_max,
            value=self.value,
        )
        new_node.alpha = self.alpha
        new_node.beta = self.beta
        new_node.status = self.status
        new_node.x = self.x
        new_node.y = self.y

        for child in self.children:
            cloned_child = child.clone()
            new_node.add_child(cloned_child)

        return new_node

    def get_all_nodes(self) -> List['Node']:
        """Returns a flat list of all nodes in the subtree using breadth-first traversal."""
        nodes = []
        queue = [self]
        while queue:
            current = queue.pop(0)
            nodes.append(current)
            queue.extend(current.children)
        return nodes

    def get_leaves(self) -> List['Node']:
        """Returns a list of all leaf nodes under this node."""
        leaves = []
        stack = [self]
        while stack:
            current = stack.pop()
            if current.is_leaf:
                leaves.append(current)
            else:
                for child in reversed(current.children):
                    stack.append(child)
        return leaves

    def count_nodes(self) -> int:
        """Returns the total number of nodes in the subtree."""
        return 1 + sum(child.count_nodes() for child in self.children)

    def max_depth(self) -> int:
        """Returns the maximum depth of the subtree rooted here."""
        if self.is_leaf:
            return self.depth
        return max(child.max_depth() for child in self.children)

    def __repr__(self) -> str:
        type_str = "MAX" if self.is_max else "MIN"
        val_str = f"val={self.value}" if self.value is not None else "val=None"
        return f"Node({self.node_id}, {type_str}, depth={self.depth}, {val_str})"
