from textwrap import dedent

from sokoban.search.astar import run
from sokoban.logic.deadlocks import is_simple_deadlock
from sokoban.core.levels import parse_ascii
from sokoban.core.model import State
from sokoban.logic.successors import generate_push_successors


def make_level(text: str):
    return parse_ascii(dedent(text).strip("\n"))


def test_corner_deadlock_vs_goal():
    corner_level = make_level(
        """
        #####
        #$  #
        #@ .#
        #####
        """
    )
    assert is_simple_deadlock(corner_level, corner_level.start_boxes)

    goal_corner_level = make_level(
        """
        #####
        #*  #
        #@ .#
        #####
        """
    )
    assert not is_simple_deadlock(goal_corner_level, goal_corner_level.start_boxes)


def test_wall_line_deadlock_detects_missing_goals():
    level = make_level(
        """
        #####
        #   #
        ##$ #
        # @.#
        #####
        """
    )
    assert is_simple_deadlock(level, level.start_boxes)

    safe_level = make_level(
        """
        #####
        # . #
        ##$ #
        # @ #
        #####
        """
    )
    assert not is_simple_deadlock(safe_level, safe_level.start_boxes)


def test_corridor_two_box_deadlock_detected():
    corridor_level = make_level(
        """
        #########
        #@     .#
        # ##### #
        # #$$# .#
        # ##### #
        #########
        """
    )
    assert is_simple_deadlock(corridor_level, corridor_level.start_boxes)


def test_two_by_two_block_deadlock():
    level = make_level(
        """
        ######
        #@   #
        #$$  #
        #$$  #
        #....#
        ######
        """
    )
    assert is_simple_deadlock(level, level.start_boxes)


def test_two_by_two_block_ignored_if_goal_present():
    level = make_level(
        """
        ######
        #@ . #
        #*$  #
        #$$  #
        #....#
        ######
        """
    )
    assert not is_simple_deadlock(level, level.start_boxes)


def test_generate_push_successors_single_action():
    level = make_level(
        """
        #####
        #@$.#
        #####
        """
    )
    state = State(level.start_player, level.start_boxes)
    successors = generate_push_successors(level, state)

    assert len(successors) == 1
    action, next_state = successors[0]
    assert action == "RIGHT"
    assert next_state.player == (2, 1)
    assert (3, 1) in next_state.boxes


def test_generate_push_successors_prunes_deadlock_push():
    level = make_level(
        """
        ######
        #@ $ #
        # .  #
        ######
        """
    )
    state = State(level.start_player, level.start_boxes)
    successors = generate_push_successors(level, state)

    assert successors == []


def test_microban_two_plan_includes_walks():
    level = make_level(
        """
        ######
        #    #
        # #@ #
        # $* #
        # .* #
        #    #
        ######
        """
    )
    result = run(level)
    assert result["status"] == "success"
    assert result["pushes"] == ["LEFT", "DOWN", "RIGHT"]
    first_segment = result["segments"][0]
    assert first_segment["walk"] == ["RIGHT", "DOWN", "DOWN"]
    # Full action list now includes the walk + push sequence.
    assert result["actions"][:4] == ["RIGHT", "DOWN", "DOWN", "LEFT"]
