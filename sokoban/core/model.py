from dataclasses import dataclass
from typing import FrozenSet, Tuple

Coord = Tuple[int, int]


@dataclass(frozen=True)
class Level:
    width: int
    height: int
    walls: FrozenSet[Coord]
    goals: FrozenSet[Coord]
    start_player: Coord
    start_boxes: FrozenSet[Coord]

    def in_bounds(self, coord: Coord) -> bool:
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height

    def is_wall(self, coord: Coord) -> bool:
        return coord in self.walls

    def is_goal(self, coord: Coord) -> bool:
        return coord in self.goals

    def is_free(self, coord: Coord, boxes: FrozenSet[Coord]) -> bool:
        return self.in_bounds(coord) and not self.is_wall(coord) and coord not in boxes


@dataclass(frozen=True)
class State:
    player: Coord
    boxes: FrozenSet[Coord]

    def is_goal(self, level: Level) -> bool:
        return self.boxes.issubset(level.goals) and len(self.boxes) == len(level.start_boxes)
