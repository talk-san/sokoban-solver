"""Simple static deadlock detection helpers."""

from functools import lru_cache
from typing import FrozenSet, Set

from ..core.model import Coord, Level


ADJACENT_PAIRS = (
    ((1, 0), (0, 1)),
    ((1, 0), (0, -1)),
    ((-1, 0), (0, 1)),
    ((-1, 0), (0, -1)),
)


@lru_cache(maxsize=None)
def corner_cells(level: Level) -> FrozenSet[Coord]:
    corners: Set[Coord] = set()
    for x in range(level.width):
        for y in range(level.height):
            coord = (x, y)
            if level.is_wall(coord):
                continue
            for (dx1, dy1), (dx2, dy2) in ADJACENT_PAIRS:
                adj1 = (x + dx1, y + dy1)
                adj2 = (x + dx2, y + dy2)
                wallish1 = not level.in_bounds(adj1) or level.is_wall(adj1)
                wallish2 = not level.in_bounds(adj2) or level.is_wall(adj2)
                if wallish1 and wallish2:
                    corners.add(coord)
                    break
    return frozenset(corners)


@lru_cache(maxsize=None)
def goal_columns(level: Level) -> FrozenSet[int]:
    return frozenset(coord[0] for coord in level.goals)


@lru_cache(maxsize=None)
def goal_rows(level: Level) -> FrozenSet[int]:
    return frozenset(coord[1] for coord in level.goals)


def _is_against_wall(level: Level, coord: Coord, delta: Coord) -> bool:
    x, y = coord
    dx, dy = delta
    adj = (x + dx, y + dy)
    return not level.in_bounds(adj) or level.is_wall(adj)


def _vertical_wall_contact(level: Level, coord: Coord) -> bool:
    return _is_against_wall(level, coord, (-1, 0)) or _is_against_wall(level, coord, (1, 0))


def _horizontal_wall_contact(level: Level, coord: Coord) -> bool:
    return _is_against_wall(level, coord, (0, -1)) or _is_against_wall(level, coord, (0, 1))


def _two_box_corridor_deadlock(level: Level, boxes: FrozenSet[Coord]) -> bool:
    """Detect two boxes glued in a 1-cell corridor.

    Pattern: two adjacent boxes occupy a hallway that is only one cell wide,
    walls (or out-of-bounds) run along the sides, and there are walls directly
    blocking the front and back. With no goals along that segment, the boxes
    cannot be separated or moved — the classic "two boxes glued in a narrow
    corridor" deadlock.
    """

    box_set = set(boxes)

    def vertical_walls(coord: Coord) -> bool:
        x, y = coord
        return _is_against_wall(level, (x, y), (0, -1)) and _is_against_wall(level, (x, y), (0, 1))

    def horizontal_walls(coord: Coord) -> bool:
        x, y = coord
        return _is_against_wall(level, (x, y), (-1, 0)) and _is_against_wall(level, (x, y), (1, 0))

    for box in boxes:
        x, y = box
        right = (x + 1, y)
        if right in box_set and not level.is_goal(box) and not level.is_goal(right):
            if vertical_walls(box) and vertical_walls(right):
                left_blocked = _is_against_wall(level, box, (-1, 0))
                right_blocked = _is_against_wall(level, right, (1, 0))
                if left_blocked and right_blocked:
                    return True

        down = (x, y + 1)
        if down in box_set and not level.is_goal(box) and not level.is_goal(down):
            if horizontal_walls(box) and horizontal_walls(down):
                up_blocked = _is_against_wall(level, box, (0, -1))
                down_blocked = _is_against_wall(level, down, (0, 1))
                if up_blocked and down_blocked:
                    return True

    return False


def _two_by_two_block_deadlock(level: Level, boxes: FrozenSet[Coord]) -> bool:
    """Detect 2x2 blocks of boxes/walls with no goals (boxes cannot exit)."""

    if level.width < 2 or level.height < 2:
        return False

    box_set = set(boxes)
    for x in range(level.width - 1):
        for y in range(level.height - 1):
            cells = [
                (x, y),
                (x + 1, y),
                (x, y + 1),
                (x + 1, y + 1),
            ]
            if any(level.is_goal(cell) for cell in cells):
                continue
            non_goal_boxes = [cell for cell in cells if cell in box_set and not level.is_goal(cell)]
            if len(non_goal_boxes) < 2:
                continue
            if all(level.is_wall(cell) or cell in box_set for cell in cells):
                return True
    return False


def is_simple_deadlock(level: Level, boxes: FrozenSet[Coord]) -> bool:
    """Detects a box stuck in a corner (unless it's a goal)."""

    corners = corner_cells(level)
    goal_cols = goal_columns(level)
    goal_rows_set = goal_rows(level)
    for box in boxes:
        if level.is_goal(box):
            continue

        if box in corners:
            return True

        x, y = box
        # Wall-line: box flush with a wall and no goal along the line parallel to it.
        if _vertical_wall_contact(level, box) and x not in goal_cols:
            return True

        if _horizontal_wall_contact(level, box) and y not in goal_rows_set:
            return True
    if _two_box_corridor_deadlock(level, boxes):
        return True
    if _two_by_two_block_deadlock(level, boxes):
        return True
    return False
