"""Helpers for reconstructing full move plans from push-based solutions."""

from collections import deque
from typing import Dict, Iterable, List, Sequence, Tuple

from ..core.model import Coord, Level, State
from .successors import MOVES


def _shortest_walk(level: Level, boxes: Iterable[Coord], start: Coord, goal: Coord) -> List[str]:
    """Return the shortest sequence of moves from ``start`` to ``goal`` avoiding boxes."""

    if start == goal:
        return []

    boxes_set = set(boxes)
    queue = deque([start])
    parents: Dict[Coord, Coord] = {start: start}
    steps: Dict[Coord, str] = {}

    while queue:
        x, y = queue.popleft()
        for move, (dx, dy) in MOVES.items():
            nxt = (x + dx, y + dy)
            if nxt in parents:
                continue
            if not level.in_bounds(nxt) or level.is_wall(nxt) or nxt in boxes_set:
                continue
            parents[nxt] = (x, y)
            steps[nxt] = move
            if nxt == goal:
                queue.clear()
                break
            queue.append(nxt)

    if goal not in parents:
        raise ValueError("Player cannot reach push position")

    path: List[str] = []
    cur = goal
    while cur != start:
        move = steps[cur]
        path.append(move)
        cur = parents[cur]
    path.reverse()
    return path


def build_plan_segments(level: Level, state_sequence: Sequence[State], actions: Sequence[str]) -> List[dict]:
    """Decorate push actions with the walking steps required before each push."""

    segments: List[dict] = []
    for idx, action in enumerate(actions):
        prev_state = state_sequence[idx]
        next_state = state_sequence[idx + 1]
        dx, dy = MOVES[action]
        # Player needs to stand one cell behind the box before pushing.
        push_origin = (next_state.player[0] - dx, next_state.player[1] - dy)
        walk = _shortest_walk(level, prev_state.boxes, prev_state.player, push_origin)
        segments.append({
            "walk": walk,
            "push": action,
            "box": next_state.player,
        })
    return segments


def flatten_segments(segments: Sequence[dict]) -> List[str]:
    """Flattens walk/push segments into a single move list (pushes included)."""

    moves: List[str] = []
    for segment in segments:
        moves.extend(segment["walk"])
        moves.append(segment["push"])
    return moves
