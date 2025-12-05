"""Game-logic helpers for Sokoban planning and pruning."""

from .deadlocks import is_simple_deadlock
from .plan import build_plan_segments, flatten_segments
from .successors import MOVES, generate_push_successors

__all__ = [
    "is_simple_deadlock",
    "build_plan_segments",
    "flatten_segments",
    "MOVES",
    "generate_push_successors",
]
