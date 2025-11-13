import time
from .model import Level, State


def run(level: Level) -> dict:
    start = time.time()
    state = State(player=level.start_player, boxes=level.start_boxes)
    # TODO: implement real A* over push actions.
    # Mock return for now
    return {
        "status": "OK-PARSER-WIRED",
        "is_goal_at_start": state.is_goal(level),
        "boxes": len(state.boxes),
        "goals": len(level.goals),
        "time_s": round(time.time() - start, 6),
    }
