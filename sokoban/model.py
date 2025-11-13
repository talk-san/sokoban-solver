from dataclasses import dataclass
from typing import Set, Tuple, FrozenSet

Coord = Tuple[int, int]


@dataclass(frozen=True)
class Level:
    width: int
    height: int
    walls: FrozenSet[Coord]
    goals: FrozenSet[Coord]
    start_player: Coord
    start_boxes: FrozenSet[Coord]


@dataclass(frozen=True)
class State:
    player: Coord
    boxes: FrozenSet[Coord]

    def is_goal(self, level: Level) -> bool:
        return self.boxes.issubset(level.goals) and len(self.boxes) == len(level.start_boxes)
