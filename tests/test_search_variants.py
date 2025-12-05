from textwrap import dedent

from sokoban.core.levels import parse_ascii
from sokoban.search.hill_climbing import run as run_hill
from sokoban.search.rbfs import run as run_rbfs


def make_level(text: str):
    return parse_ascii(dedent(text).strip("\n"))


def test_rbfs_solves_tiny():
    level = make_level(
        """
        #####
        #@$.#
        #####
        """
    )
    result = run_rbfs(level)
    assert result["status"] == "success"
    assert result["cost"] == 1


def test_rbfs_respects_expansion_limit():
    level = make_level(
        """
        #####
        #@$.#
        #####
        """
    )
    result = run_rbfs(level, max_expansions=0)
    assert result["status"] == "failure"


def test_hill_climbing_solves_tiny():
    level = make_level(
        """
        #####
        #@$.#
        #####
        """
    )
    result = run_hill(level)
    assert result["status"] == "success"
    assert result["cost"] == 1
