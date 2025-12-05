"""Simple heuristic hill-climbing solver for Sokoban."""

from __future__ import annotations

import time
from typing import List, Optional, Tuple

from .astar import heuristic
from ..core.model import Level, State
from ..logic.plan import build_plan_segments, flatten_segments
from ..logic.successors import generate_push_successors


def run(
    level: Level,
    weight: float = 1.0,
    max_steps: int = 2000,
    allow_sideways: bool = False,
) -> dict:
    """Perform greedy hill climbing guided by the Sokoban heuristic.

    ``weight`` scales the heuristic (similar to weighted A*). ``allow_sideways``
    permits moves that keep the heuristic equal but never increases it. Because
    hill climbing is a local method it easily gets stuck; the function returns a
    failure dictionary when that happens.
    """

    if weight <= 0:
        raise ValueError("weight must be > 0 for hill climbing")

    start_time = time.time()
    current = State(player=level.start_player, boxes=level.start_boxes)
    current_h = weight * heuristic(level, current)
    expansions = 0

    pushes: List[str] = []
    states: List[State] = [current]
    visited = {current}

    for _ in range(max_steps):
        if current.is_goal(level):
            break

        best_action: Optional[str] = None
        best_state: Optional[State] = None
        best_score = float("inf")

        for action, successor in generate_push_successors(level, current):
            expansions += 1
            if successor in visited:
                continue
            h_val = weight * heuristic(level, successor)
            if h_val < best_score or (allow_sideways and h_val == best_score and best_state is None):
                best_score = h_val
                best_action = action
                best_state = successor

        if best_state is None:
            break

        if best_score > current_h or (best_score == current_h and not allow_sideways):
            break

        pushes.append(best_action or "")
        states.append(best_state)
        visited.add(best_state)
        current = best_state
        current_h = best_score

        if current.is_goal(level):
            break
    else:
        # Reached max_steps without success
        current = states[-1]

    elapsed = time.time() - start_time

    if not current.is_goal(level):
        return {
            "status": "failure",
            "cost": None,
            "path_length": len(pushes),
            "actions": [],
            "pushes": [],
            "segments": [],
            "expansions": expansions,
            "time_s": round(elapsed, 6),
        }

    segments = build_plan_segments(level, states, pushes)
    move_sequence = flatten_segments(segments)

    return {
        "status": "success",
        "cost": len(pushes),
        "path_length": len(pushes),
        "actions": move_sequence,
        "pushes": pushes,
        "segments": segments,
        "expansions": expansions,
        "time_s": round(elapsed, 6),
    }
