"""
Trace Module
Defines event structures used to record and replay algorithm execution steps
in the interactive Tkinter GUI simulator.
"""

from typing import List, Optional, Any, Dict
from dataclasses import dataclass, field


@dataclass
class SearchEvent:
    """
    Represents a discrete algorithmic action during tree search.

    Attributes:
        step_number (int): Sequential index of this step.
        event_type (str): Type of event:
            - 'VISIT': Visiting a node on the downward DFS traversal.
            - 'EVAL_LEAF': Inspecting and evaluating a terminal leaf node.
            - 'UPDATE_VAL': Updating an internal node's tentative minimax value or alpha/beta.
            - 'PRUNE': Triggering an alpha-beta cutoff and pruning remaining subtrees.
            - 'FINISH_NODE': Finalizing a node's value and returning to parent.
            - 'DECISION': Final root choice selected.
        node_id (str): Identifier of the active node.
        depth (int): Depth of the active node.
        is_max (bool): Player turn at this node.
        value: Current minimax value at this node (numeric or None).
        alpha (float): Current alpha bound at this step.
        beta (float): Current beta bound at this step.
        description (str): Educational step-by-step description of the action.
        pruned_node_ids (List[str]): List of node IDs eliminated if this is a PRUNE event.
        best_child_id (Optional[str]): The child node providing the optimal value.
    """
    step_number: int
    event_type: str
    node_id: str
    depth: int
    is_max: bool
    value: Optional[float]
    alpha: float
    beta: float
    description: str
    pruned_node_ids: List[str] = field(default_factory=list)
    best_child_id: Optional[str] = None


@dataclass
class SearchResult:
    """
    Aggregated output from a tree search run.

    Attributes:
        root_value (float): The final minimax utility value achieved at the root.
        best_move_node_id (Optional[str]): The child node representing the optimal root action.
        nodes_visited (int): Total number of nodes traversed/expanded.
        leaf_evaluations (int): Total number of static leaf nodes evaluated.
        pruned_nodes (int): Total count of nodes bypassed due to cutoffs.
        execution_time_ms (float): Measured wall-clock time in milliseconds.
        trace (List[SearchEvent]): Chronological event log for GUI animation.
    """
    root_value: float
    best_move_node_id: Optional[str]
    nodes_visited: int
    leaf_evaluations: int
    pruned_nodes: int
    execution_time_ms: float
    trace: List[SearchEvent] = field(default_factory=list)
