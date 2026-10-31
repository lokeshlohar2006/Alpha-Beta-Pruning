"""
Unit Tests for Minimax Algorithm
Covers small, medium, edge-case trees, negative values, equal values, and single-child trees.
"""

import unittest
from core.game_tree import Node
from core.tree_generator import create_predefined_tree, create_random_tree
from algorithms.minimax import Minimax


class TestMinimax(unittest.TestCase):
    """Test suite evaluating the correctness of the Minimax search implementation."""

    def setUp(self):
        self.minimax = Minimax(record_trace=True)

    def test_single_leaf_root(self):
        """A tree consisting solely of a single leaf root node."""
        root = Node("Root", is_max=True, value=42.0)
        result = self.minimax.search(root)
        self.assertEqual(result.root_value, 42.0)
        self.assertEqual(result.nodes_visited, 1)
        self.assertEqual(result.leaf_evaluations, 1)
        self.assertIsNone(result.best_move_node_id)

    def test_depth_one_max_decision(self):
        """Root MAX with direct leaf children: should pick maximum."""
        root = Node("Root", is_max=True)
        root.add_child(Node("L1", depth=1, is_max=False, value=5.0))
        root.add_child(Node("L2", depth=1, is_max=False, value=12.0))
        root.add_child(Node("L3", depth=1, is_max=False, value=-3.0))

        result = self.minimax.search(root)
        self.assertEqual(result.root_value, 12.0)
        self.assertEqual(result.best_move_node_id, "L2")
        self.assertEqual(result.nodes_visited, 4)
        self.assertEqual(result.leaf_evaluations, 3)

    def test_depth_one_min_decision(self):
        """Root MIN with direct leaf children: should pick minimum."""
        root = Node("Root", is_max=False)
        root.add_child(Node("L1", depth=1, is_max=True, value=10.0))
        root.add_child(Node("L2", depth=1, is_max=True, value=-7.0))
        root.add_child(Node("L3", depth=1, is_max=True, value=25.0))

        result = self.minimax.search(root)
        self.assertEqual(result.root_value, -7.0)
        self.assertEqual(result.best_move_node_id, "L2")
        self.assertEqual(result.nodes_visited, 4)

    def test_classic_textbook_tree(self):
        """Canonical Russell & Norvig textbook 3-branch tree."""
        tree = create_predefined_tree("classic_textbook")
        result = self.minimax.search(tree)

        self.assertEqual(result.root_value, 3.0)
        self.assertEqual(result.best_move_node_id, "A")
        self.assertEqual(result.nodes_visited, 13)
        self.assertEqual(result.leaf_evaluations, 9)

    def test_negative_utilities(self):
        """Tree with all negative values."""
        root = Node("Root", is_max=True)
        min_node = Node("MIN_1", depth=1, is_max=False)
        min_node.add_child(Node("L1", depth=2, is_max=True, value=-20.0))
        min_node.add_child(Node("L2", depth=2, is_max=True, value=-15.0))
        root.add_child(min_node)

        min_node2 = Node("MIN_2", depth=1, is_max=False)
        min_node2.add_child(Node("L3", depth=2, is_max=True, value=-50.0))
        min_node2.add_child(Node("L4", depth=2, is_max=True, value=-5.0))
        root.add_child(min_node2)

        # MIN_1 chooses min(-20, -15) = -20
        # MIN_2 chooses min(-50, -5) = -50
        # MAX chooses max(-20, -50) = -20 via MIN_1
        result = self.minimax.search(root)
        self.assertEqual(result.root_value, -20.0)
        self.assertEqual(result.best_move_node_id, "MIN_1")

    def test_identical_leaf_values(self):
        """Tree where all leaf utilities are identical."""
        root = Node("Root", is_max=True)
        for i in range(2):
            child = Node(f"C{i}", depth=1, is_max=False)
            for j in range(2):
                child.add_child(Node(f"L{i}_{j}", depth=2, is_max=True, value=7.0))
            root.add_child(child)

        result = self.minimax.search(root)
        self.assertEqual(result.root_value, 7.0)

    def test_single_child_chain(self):
        """Degenerate tree with branching factor b=1."""
        root = Node("Root", is_max=True)
        c1 = Node("C1", depth=1, is_max=False)
        c2 = Node("C2", depth=2, is_max=True)
        leaf = Node("Leaf", depth=3, is_max=False, value=99.0)
        c2.add_child(leaf)
        c1.add_child(c2)
        root.add_child(c1)

        result = self.minimax.search(root)
        self.assertEqual(result.root_value, 99.0)
        self.assertEqual(result.best_move_node_id, "C1")
        self.assertEqual(result.nodes_visited, 4)

    def test_random_reproducible_tree(self):
        """Random tree with deterministic seed."""
        tree1 = create_random_tree(branching_factor=2, depth=3, seed=12345)
        tree2 = create_random_tree(branching_factor=2, depth=3, seed=12345)

        res1 = self.minimax.search(tree1)
        res2 = self.minimax.search(tree2)

        self.assertEqual(res1.root_value, res2.root_value)
        self.assertEqual(res1.best_move_node_id, res2.best_move_node_id)
        self.assertEqual(res1.nodes_visited, res2.nodes_visited)


if __name__ == "__main__":
    unittest.main()
