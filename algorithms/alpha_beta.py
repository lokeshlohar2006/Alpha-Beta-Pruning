"""
Alpha-Beta Pruning Algorithm Module
Implements adversarial minimax search enhanced with alpha-beta bounding and cutoffs.
Maintains an execution trace for step-by-step replay in the graphical simulator.
"""

import time
import math
from typing import List, Optional, Set
from core.game_tree import Node
from algorithms.trace import SearchEvent, SearchResult


class AlphaBetaPruning:
    """
    Alpha-Beta Pruning search algorithm for two-player zero-sum games.

    Maintains two parameters:
    - alpha (α): The best value (highest) that the MAX player is guaranteed along the current path.
                 Initialized to -infinity.
    - beta  (β): The best value (lowest) that the MIN player is guaranteed along the current path.
                 Initialized to +infinity.

    Whenever alpha >= beta at any node, further exploration of that branch is pruned because
    the parent or an ancestor already has a better alternative that will prevent this branch
    from ever being chosen in rational play.
    """

    def __init__(self, record_trace: bool = True):
        self.record_trace = record_trace
        self.nodes_visited = 0
        self.leaf_evaluations = 0
        self.pruned_nodes_count = 0
        self.trace: List[SearchEvent] = []
        self._step_counter = 0

    def _log_event(
        self,
        event_type: str,
        node: Node,
        alpha: float,
        beta: float,
        description: str,
        pruned_node_ids: Optional[List[str]] = None,
        best_child_id: Optional[str] = None,
    ) -> None:
        """Records an educational step for simulation replay."""
        if not self.record_trace:
            return
        self._step_counter += 1
        event = SearchEvent(
            step_number=self._step_counter,
            event_type=event_type,
            node_id=node.node_id,
            depth=node.depth,
            is_max=node.is_max,
            value=node.value,
            alpha=alpha,
            beta=beta,
            description=description,
            pruned_node_ids=pruned_node_ids or [],
            best_child_id=best_child_id,
        )
        self.trace.append(event)

    def _mark_subtree_pruned(self, node: Node) -> List[str]:
        """
        Recursively marks a bypassed subtree as 'pruned' and counts the eliminated nodes.
        Returns a list of all pruned node IDs.
        """
        pruned_ids = []
        node.status = "pruned"
        pruned_ids.append(node.node_id)
        self.pruned_nodes_count += 1

        for child in node.children:
            pruned_ids.extend(self._mark_subtree_pruned(child))
        return pruned_ids

    def search(self, root: Node) -> SearchResult:
        """
        Executes Alpha-Beta Pruning starting from the given root node with initial bounds [-inf, +inf].

        Args:
            root (Node): Root of the game tree.

        Returns:
            SearchResult: Object containing optimal root value, best child move,
                          node visit counts, pruned count, timing, and trace.
        """
        self.nodes_visited = 0
        self.leaf_evaluations = 0
        self.pruned_nodes_count = 0
        self.trace = []
        self._step_counter = 0

        root.reset_state()

        start_time = time.perf_counter()
        optimal_value = self._alpha_beta(
            node=root,
            alpha=-math.inf,
            beta=math.inf,
        )
        end_time = time.perf_counter()

        elapsed_ms = (end_time - start_time) * 1000.0
        best_move_id = root.best_child.node_id if root.best_child else None

        if self.record_trace:
            self._log_event(
                event_type="DECISION",
                node=root,
                alpha=root.alpha,
                beta=root.beta,
                description=f"Alpha-Beta Pruning completed. Optimal root utility is {optimal_value} "
                            f"(via child action {best_move_id}). Bypassed {self.pruned_nodes_count} nodes.",
                best_child_id=best_move_id,
            )

        return SearchResult(
            root_value=optimal_value,
            best_move_node_id=best_move_id,
            nodes_visited=self.nodes_visited,
            leaf_evaluations=self.leaf_evaluations,
            pruned_nodes=self.pruned_nodes_count,
            execution_time_ms=elapsed_ms,
            trace=self.trace,
        )

    def _alpha_beta(self, node: Node, alpha: float, beta: float) -> float:
        """
        Recursive helper implementing alpha-beta minimax search.

        Args:
            node (Node): Current state in the game tree.
            alpha (float): Best value achievable by MAX along path to root.
            beta (float): Best value achievable by MIN along path to root.

        Returns:
            float: Backed-up minimax utility value for this node.
        """
        self.nodes_visited += 1
        node.status = "evaluating"
        node.alpha = alpha
        node.beta = beta

        # Base case: Terminal leaf node
        if node.is_leaf:
            self.leaf_evaluations += 1
            node.status = "evaluated"
            val = float(node.value) if node.value is not None else 0.0
            self._log_event(
                event_type="EVAL_LEAF",
                node=node,
                alpha=alpha,
                beta=beta,
                description=f"Leaf {node.name} evaluated. Utility = {val} [α={alpha}, β={beta}].",
            )
            return val

        # Recursive case 1: MAX player's turn
        if node.is_max:
            self._log_event(
                event_type="VISIT",
                node=node,
                alpha=alpha,
                beta=beta,
                description=f"Visiting MAX node {node.name} [α={alpha}, β={beta}]. Initializing value = -inf.",
            )
            max_eval = -math.inf
            best_child = None

            for idx, child in enumerate(node.children):
                child_eval = self._alpha_beta(child, alpha, beta)

                if child_eval > max_eval:
                    max_eval = child_eval
                    best_child = child
                    node.value = max_eval
                    node.best_child = best_child

                # Alpha bound update for MAX: alpha = max(alpha, max_eval)
                prev_alpha = alpha
                alpha = max(alpha, max_eval)
                node.alpha = alpha
                node.beta = beta

                self._log_event(
                    event_type="UPDATE_BOUNDS",
                    node=node,
                    alpha=alpha,
                    beta=beta,
                    description=f"MAX node {node.name}: child {child.name} returned {child_eval}. "
                                f"Value={max_eval}, α updated: {prev_alpha} -> {alpha} [β={beta}].",
                    best_child_id=child.node_id,
                )

                # Alpha-Beta cutoff condition: alpha >= beta
                if alpha >= beta:
                    remaining_children = node.children[idx + 1 :]
                    pruned_ids = []
                    for unvisited in remaining_children:
                        pruned_ids.extend(self._mark_subtree_pruned(unvisited))

                    self._log_event(
                        event_type="PRUNE",
                        node=node,
                        alpha=alpha,
                        beta=beta,
                        description=f"BETA CUTOFF at MAX node {node.name}! α ({alpha}) >= β ({beta}). "
                                    f"Pruned {len(pruned_ids)} unvisited node(s): {', '.join(pruned_ids)}.",
                        pruned_node_ids=pruned_ids,
                        best_child_id=best_child.node_id if best_child else None,
                    )
                    break  # Prune remaining sibling branches

            node.value = max_eval
            node.best_child = best_child
            node.status = "evaluated"
            self._log_event(
                event_type="FINISH_NODE",
                node=node,
                alpha=alpha,
                beta=beta,
                description=f"Finished MAX node {node.name}. Final value = {max_eval} [α={alpha}, β={beta}].",
                best_child_id=best_child.node_id if best_child else None,
            )
            return max_eval

        # Recursive case 2: MIN player's turn
        else:
            self._log_event(
                event_type="VISIT",
                node=node,
                alpha=alpha,
                beta=beta,
                description=f"Visiting MIN node {node.name} [α={alpha}, β={beta}]. Initializing value = +inf.",
            )
            min_eval = math.inf
            best_child = None

            for idx, child in enumerate(node.children):
                child_eval = self._alpha_beta(child, alpha, beta)

                if child_eval < min_eval:
                    min_eval = child_eval
                    best_child = child
                    node.value = min_eval
                    node.best_child = best_child

                # Beta bound update for MIN: beta = min(beta, min_eval)
                prev_beta = beta
                beta = min(beta, min_eval)
                node.alpha = alpha
                node.beta = beta

                self._log_event(
                    event_type="UPDATE_BOUNDS",
                    node=node,
                    alpha=alpha,
                    beta=beta,
                    description=f"MIN node {node.name}: child {child.name} returned {child_eval}. "
                                f"Value={min_eval}, β updated: {prev_beta} -> {beta} [α={alpha}].",
                    best_child_id=child.node_id,
                )

                # Alpha-Beta cutoff condition: alpha >= beta (or beta <= alpha)
                if alpha >= beta:
                    remaining_children = node.children[idx + 1 :]
                    pruned_ids = []
                    for unvisited in remaining_children:
                        pruned_ids.extend(self._mark_subtree_pruned(unvisited))

                    self._log_event(
                        event_type="PRUNE",
                        node=node,
                        alpha=alpha,
                        beta=beta,
                        description=f"ALPHA CUTOFF at MIN node {node.name}! β ({beta}) <= α ({alpha}). "
                                    f"Pruned {len(pruned_ids)} unvisited node(s): {', '.join(pruned_ids)}.",
                        pruned_node_ids=pruned_ids,
                        best_child_id=best_child.node_id if best_child else None,
                    )
                    break  # Prune remaining sibling branches

            node.value = min_eval
            node.best_child = best_child
            node.status = "evaluated"
            self._log_event(
                event_type="FINISH_NODE",
                node=node,
                alpha=alpha,
                beta=beta,
                description=f"Finished MIN node {node.name}. Final value = {min_eval} [α={alpha}, β={beta}].",
                best_child_id=best_child.node_id if best_child else None,
            )
            return min_eval
