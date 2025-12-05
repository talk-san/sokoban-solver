"""Iterative Deepening A* (IDA*) solver for Sokoban."""

import time
from typing import List, Tuple

from .astar import heuristic
from ..core.model import Level, State
from ..logic.plan import build_plan_segments, flatten_segments
from ..logic.successors import generate_push_successors


class SearchResult(Exception):
    """Internal signal to unwind recursion when a solution is found."""

    def __init__(self, actions: List[str], states: List[State], cost: int):
        super().__init__("solution found")
        self.actions = actions
        self.states = states
        self.cost = cost


def run(level: Level, weight: float = 1.0) -> dict:
    if weight < 1.0:
        raise ValueError("weight must be >= 1.0 for IDA*")

    start_time = time.time()
    start_state = State(player=level.start_player, boxes=level.start_boxes)

    threshold = heuristic(level, start_state) * weight
    path: List[Tuple[str, State]] = [("", start_state)]
    expansions = 0

    def search(bound: float, g_cost: int) -> float:
        """Depth-first search bounded by ``bound`` on f = g + w*h.

        Returns the smallest f-cost that exceeded ``bound`` (for the next
        iteration) or raises ``SearchResult`` when the goal is reached.
        """
        nonlocal expansions

        _, state = path[-1]
        f_cost = g_cost + weight * heuristic(level, state)
        if f_cost > bound:
            return f_cost

        if state.is_goal(level):
            actions = [action for action, _ in path[1:]]
            states = [st for _, st in path]
            raise SearchResult(actions, states, g_cost)

        min_exceeded = float("inf")
        for action, successor in generate_push_successors(level, state):
            expansions += 1
            path.append((action, successor))
            t = search(bound, g_cost + 1)
            path.pop()
            if isinstance(t, float) and t < min_exceeded:
                min_exceeded = t
        return min_exceeded

    while True:
        try:
            # Depth-first iteration bounded by the current f-cost threshold.
            next_threshold = search(threshold, 0)
        except SearchResult as result:
            elapsed = time.time() - start_time
            segments = build_plan_segments(level, result.states, result.actions)
            move_sequence = flatten_segments(segments)
            return {
                "status": "success",
                "cost": result.cost,
                "path_length": len(result.actions),
                "actions": move_sequence,
                "pushes": result.actions,
                "segments": segments,
                "expansions": expansions,
                "time_s": round(elapsed, 6),
            }

        if next_threshold == float("inf"):
            elapsed = time.time() - start_time
            return {
                "status": "failure",
                "cost": None,
                "path_length": 0,
                "actions": [],
                "pushes": [],
                "segments": [],
                "expansions": expansions,
                "time_s": round(elapsed, 6),
            }

        # Increase threshold to the minimum f-cost that exceeded the previous bound.
        threshold = next_threshold
