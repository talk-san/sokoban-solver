"""Push-based successor generation for Sokoban states."""

from collections import deque
from typing import List, Set, Tuple

from .deadlocks import is_simple_deadlock
from ..core.model import Coord, Level, State


Direction = Tuple[int, int]

MOVES = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}


def _reachable(level: Level, boxes: Set[Coord], start: Coord) -> Set[Coord]:
    """Flood-fill the cells the player can reach without pushing boxes."""

    frontier = deque([start])
    seen = {start}

    while frontier:
        x, y = frontier.popleft()
        for dx, dy in MOVES.values():
            nxt = (x + dx, y + dy)
            if nxt in seen:
                continue
            if not level.in_bounds(nxt) or level.is_wall(nxt) or nxt in boxes:
                continue
            seen.add(nxt)
            frontier.append(nxt)
    return seen


def generate_push_successors(level: Level, state: State) -> List[Tuple[str, State]]:
    """Enumerate push actions (cost 1) reachable after arbitrary walking."""

    boxes = set(state.boxes)
    reachable = _reachable(level, boxes, state.player)
    successors: List[Tuple[str, State]] = []

    for box in state.boxes:
        bx, by = box
        for action, (dx, dy) in MOVES.items():
            player_pos = (bx - dx, by - dy)
            target = (bx + dx, by + dy)

            if player_pos not in reachable:
                continue
            if not level.is_free(target, state.boxes):
                continue

            new_boxes = set(state.boxes)
            new_boxes.remove(box)
            new_boxes.add(target)
            new_state = State(player=box, boxes=frozenset(new_boxes))

            if is_simple_deadlock(level, new_state.boxes):
                continue

            successors.append((action, new_state))

    return successors
