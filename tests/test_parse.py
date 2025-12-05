from pathlib import Path

from sokoban.search.astar import run
from sokoban.core.levels import load_txt, parse_ascii, split_levels


def test_parse_tiny():
    txt = "#####\n#@$.#\n#####"
    lvl = parse_ascii(txt)
    assert lvl.width == 5 and lvl.height == 3
    assert len(lvl.walls) > 0
    assert len(lvl.start_boxes) == 1
    assert len(lvl.goals) == 1
    assert lvl.start_player is not None


def test_astar_solves_tiny_file():
    level_path = Path(__file__).resolve().parents[1] / "data" / "tiny.txt"
    txt = load_txt(str(level_path))
    lvl_text = split_levels(txt)[0]
    lvl = parse_ascii(lvl_text)
    result = run(lvl)
    assert result["status"] == "success"
    assert result["cost"] == 1
