"""Recursive Best-First Search (RBFS) solver for Sokoban."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .astar import heuristic
from ..core.model import Level, State
from ..logic.plan import build_plan_segments, flatten_segments
from ..logic.successors import generate_push_successors


@dataclass
class _Node:
    state: State
    g: int
    f: float
    action: Optional[str]
    parent: Optional["_Node"]


def run(
    level: Level,
    weight: float = 1.0,
    f_limit: float | None = None,
    max_expansions: Optional[int] = None,
) -> dict:
    """Solve a level using RBFS.

    ``weight`` behaves like weighted A*: values > 1.0 bias the search toward the
    heuristic. ``f_limit`` can be used to impose an external cutoff; by default it
    starts at infinity.
    """

    if weight <= 0:
        raise ValueError("weight must be > 0 for RBFS")

    start_time = time.time()
    start_state = State(player=level.start_player, boxes=level.start_boxes)
    start_h = heuristic(level, start_state)
    start_f = weight * start_h

    start_node = _Node(state=start_state, g=0, f=start_f, action=None, parent=None)
    limit = math.inf if f_limit is None else f_limit
    expansions = 0

    path_states = {start_state}

    def recurse(node: _Node, limit_val: float) -> Tuple[Optional[_Node], float]:
        nonlocal expansions

        if max_expansions is not None and expansions >= max_expansions:
            return None, math.inf

        if node.state.is_goal(level):
            return node, node.f

        successors: List[_Node] = []
        for action, succ_state in generate_push_successors(level, node.state):
            expansions += 1
            if max_expansions is not None and expansions > max_expansions:
                return None, math.inf
            if succ_state in path_states:
                continue
            g_cost = node.g + 1
            h_val = heuristic(level, succ_state)
            f_cost = g_cost + weight * h_val
            child = _Node(state=succ_state, g=g_cost, f=max(f_cost, node.f), action=action, parent=node)
            successors.append(child)

        if not successors:
            return None, math.inf

        while True:
            successors.sort(key=lambda n: n.f)
            best = successors[0]
            if best.f > limit_val:
                return None, best.f
            alternative = successors[1].f if len(successors) > 1 else math.inf
            path_states.add(best.state)
            result, best_f = recurse(best, min(limit_val, alternative))
            path_states.remove(best.state)
            best.f = best_f
            if result is not None:
                return result, best.f

    solution, _ = recurse(start_node, limit)
    elapsed = time.time() - start_time

    if solution is None:
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

    pushes: List[str] = []
    states: List[State] = []
    node = solution
    while node is not None:
        states.append(node.state)
        if node.action is not None:
            pushes.append(node.action)
        node = node.parent
    pushes.reverse()
    states.reverse()

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
