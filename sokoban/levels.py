from typing import Tuple, Set
from .model import Level

LEGEND = {
    "#": "wall",
    "@": "player",
    "+": "player_on_goal",
    "$": "box",
    "*": "box_on_goal",
    ".": "goal",
    " ": "floor",
}


def load_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().rstrip("\n")


def parse_ascii(text: str) -> Level:
    lines = text.splitlines()
    width = max(len(line) for line in lines)
    height = len(lines)

    walls: Set[Tuple[int, int]] = set()
    goals: Set[Tuple[int, int]] = set()
    boxes: Set[Tuple[int, int]] = set()
    player = None

    for y, line in enumerate(lines):
        for x, ch in enumerate(line.ljust(width, " ")):
            if ch == "#":
                walls.add((x, y))
            elif ch == ".":
                goals.add((x, y))
            elif ch == "$":
                boxes.add((x, y))
            elif ch == "*":
                boxes.add((x, y))
                goals.add((x, y))
            elif ch == "@":
                player = (x, y)
            elif ch == "+":
                player = (x, y)
                goals.add((x, y))
            else:
                pass

    if player is None:
        raise ValueError("No player '@' or '+' found.")
    if len(boxes) == 0:
        raise ValueError("No boxes found.")
    if len(goals) < len(boxes):
        raise ValueError("Not enough goals for boxes.")

    return Level(
        width=width,
        height=height,
        walls=frozenset(walls),
        goals=frozenset(goals),
        start_player=player,
        start_boxes=frozenset(boxes),
    )
