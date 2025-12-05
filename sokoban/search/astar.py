import heapq
import itertools
import time
from typing import Dict, List, Optional, Tuple

from ..core.model import Coord, Level, State
from ..logic.plan import build_plan_segments, flatten_segments
from ..logic.successors import generate_push_successors


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def heuristic(level: Level, state: State) -> int:
    """Admissible heuristic: sum of box distances to nearest goal."""
    goals = list(level.goals)
    if not goals:
        return 0
    total = 0
    for box in state.boxes:
        total += min(manhattan(box, goal) for goal in goals)
    return total


def reconstruct_solution(
    parents: Dict[State, Tuple[Optional[State], Optional[str]]], goal: State
) -> Tuple[List[str], List[State]]:
    actions: List[str] = []
    states: List[State] = [goal]
    current = goal
    while True:
        parent, action = parents[current]
        if parent is None:
            break
        if action is not None:
            actions.append(action)
        states.append(parent)
        current = parent
    actions.reverse()
    states.reverse()
    return actions, states


def run(level: Level, weight: float = 1.0) -> dict:
    if weight < 1.0:
        raise ValueError("weight must be >= 1.0 for weighted A*")

    start_time = time.time()
    start_state = State(player=level.start_player, boxes=level.start_boxes)
    start_h = heuristic(level, start_state)

    frontier: List[Tuple[float, int, int, State]] = []
    counter = itertools.count()
    heapq.heappush(frontier, (start_h * weight, next(counter), 0, start_state))
    best_cost: Dict[State, int] = {start_state: 0}
    parents: Dict[State, Tuple[Optional[State], Optional[str]]] = {start_state: (None, None)}

    expansions = 0

    while frontier:
        f_score, _, g_score, state = heapq.heappop(frontier)
        if g_score != best_cost.get(state):
            continue

        expansions += 1

        if state.is_goal(level):
            push_sequence, state_sequence = reconstruct_solution(parents, state)
            segments = build_plan_segments(level, state_sequence, push_sequence)
            move_sequence = flatten_segments(segments)
            elapsed = time.time() - start_time
            return {
                "status": "success",
                "cost": g_score,
                "path_length": len(push_sequence),
                "actions": move_sequence,
                "pushes": push_sequence,
                "segments": segments,
                "expansions": expansions,
                "time_s": round(elapsed, 6),
            }

        for action, successor in generate_push_successors(level, state):
            new_cost = g_score + 1
            if new_cost >= best_cost.get(successor, float("inf")):
                continue
            best_cost[successor] = new_cost
            parents[successor] = (state, action)
            h_val = heuristic(level, successor)
            f_val = new_cost + weight * h_val
            heapq.heappush(frontier, (f_val, next(counter), new_cost, successor))

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
