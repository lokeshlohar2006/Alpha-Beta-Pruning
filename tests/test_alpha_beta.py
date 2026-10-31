"""
Unit Tests for Alpha-Beta Pruning Algorithm
Tests correctness, optimality preservation relative to Minimax, pruning behavior,
edge cases (negative values, uniform values, single children), and event tracing.
"""

import unittest
from core.game_tree import Node
from core.tree_generator import create_predefined_tree, create_random_tree
from algorithms.minimax import Minimax
from algorithms.alpha_beta import AlphaBetaPruning


class TestAlphaBetaPruning(unittest.TestCase):
    """Test suite evaluating the correctness and efficiency of Alpha-Beta Pruning."""

    def setUp(self):
        self.minimax = Minimax(record_trace=False)
        self.ab = AlphaBetaPruning(record_trace=True)

    def test_classic_textbook_tree_pruning(self):
        """
        In the classic textbook tree:
        - Root value must equal 3.0
        - Best move must be 'A'
        - At least 2 leaf nodes in branch B must be pruned
        - Total visited nodes should be strictly fewer than Minimax
        """
        tree_mm = create_predefined_tree("classic_textbook")
        tree_ab = create_predefined_tree("classic_textbook")

        res_mm = self.minimax.search(tree_mm)
        res_ab = self.ab.search(tree_ab)

        self.assertEqual(res_ab.root_value, 3.0)
        self.assertEqual(res_ab.best_move_node_id, "A")
        self.assertEqual(res_mm.root_value, res_ab.root_value)
        self.assertEqual(res_mm.best_move_node_id, res_ab.best_move_node_id)
        self.assertEqual(res_ab.pruned_nodes, 2)
        self.assertLess(res_ab.nodes_visited, res_mm.nodes_visited)

    def test_value_equivalence_on_random_trees(self):
        """
        Theorem: Alpha-Beta Pruning produces the mathematically identical optimal root value
        as Minimax for any valid zero-sum game tree.
        We verify this across 15 distinct random tree configurations (varying seeds, branching factors, depths).
        """
        for seed in range(101, 116):
            b = 2 + (seed % 3)  # b in {2, 3, 4}
            d = 2 + (seed % 3)  # d in {2, 3, 4}
            tree = create_random_tree(branching_factor=b, depth=d, min_val=-25, max_val=50, seed=seed)
            tree_clone = tree.clone()

            res_mm = self.minimax.search(tree)
            res_ab = self.ab.search(tree_clone)

            self.assertEqual(
                res_ab.root_value,
                res_mm.root_value,
                f"Discrepancy at seed={seed}, b={b}, d={d}: Minimax={res_mm.root_value}, AB={res_ab.root_value}",
            )
            self.assertLessEqual(
                res_ab.nodes_visited,
                res_mm.nodes_visited,
                f"Alpha-Beta visited more nodes than Minimax at seed={seed}",
            )

    def test_single_node_tree(self):
        """Single leaf root tree."""
        root = Node("Root", is_max=True, value=15.0)
        res = self.ab.search(root)
        self.assertEqual(res.root_value, 15.0)
        self.assertEqual(res.nodes_visited, 1)
        self.assertEqual(res.pruned_nodes, 0)

    def test_all_negative_values(self):
        """Tree with purely negative utilities."""
        root = Node("Root", is_max=True)
        c1 = Node("MIN_1", depth=1, is_max=False)
        c1.add_child(Node("L1", depth=2, is_max=True, value=-10.0))
        c1.add_child(Node("L2", depth=2, is_max=True, value=-2.0))
        root.add_child(c1)

        c2 = Node("MIN_2", depth=1, is_max=False)
        c2.add_child(Node("L3", depth=2, is_max=True, value=-15.0))
        c2.add_child(Node("L4", depth=2, is_max=True, value=-20.0))
        root.add_child(c2)

        tree_mm = root.clone()
        res_ab = self.ab.search(root)
        res_mm = self.minimax.search(tree_mm)

        self.assertEqual(res_ab.root_value, res_mm.root_value)
        self.assertEqual(res_ab.best_move_node_id, res_mm.best_move_node_id)

    def test_identical_leaf_values_no_discrepancy(self):
        """All leaves equal."""
        tree = create_random_tree(branching_factor=2, depth=3, min_val=5, max_val=5, seed=1)
        tree_clone = tree.clone()

        res_mm = self.minimax.search(tree)
        res_ab = self.ab.search(tree_clone)

        self.assertEqual(res_ab.root_value, 5.0)
        self.assertEqual(res_mm.root_value, 5.0)

    def test_best_case_ordering_high_pruning(self):
        """
        Construct a tree where children are ordered optimally:
        MAX explores its highest value child first; MIN explores its lowest value child first.
        Significant pruning must occur.
        """
        root = Node("Root", is_max=True)
        # Child 1: MIN with good values for MAX [10, 15] -> min=10 -> alpha becomes 10
        min1 = Node("M1", depth=1, is_max=False)
        min1.add_child(Node("A1", depth=2, is_max=True, value=10.0))
        min1.add_child(Node("A2", depth=2, is_max=True, value=15.0))
        root.add_child(min1)

        # Child 2: MIN with worse values for MAX. First leaf is 3 <= alpha(10) -> cutoff!
        min2 = Node("M2", depth=1, is_max=False)
        min2.add_child(Node("B1", depth=2, is_max=True, value=3.0))
        min2.add_child(Node("B2", depth=2, is_max=True, value=1.0))
        min2.add_child(Node("B3", depth=2, is_max=True, value=0.0))
        root.add_child(min2)

        res = self.ab.search(root)
        self.assertEqual(res.root_value, 10.0)
        self.assertEqual(res.pruned_nodes, 2)  # B2 and B3 should be pruned

    def test_trace_contains_prune_event(self):
        """Check that search trace logs explicit PRUNE events with pruned node IDs."""
        tree = create_predefined_tree("classic_textbook")
        res = self.ab.search(tree)

        prune_events = [e for e in res.trace if e.event_type == "PRUNE"]
        self.assertGreaterEqual(len(prune_events), 1)
        # Should record pruned node IDs
        self.assertTrue(any(len(e.pruned_node_ids) > 0 for e in prune_events))


if __name__ == "__main__":
    unittest.main()
