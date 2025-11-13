from sokoban.levels import parse_ascii


def test_parse_tiny():
    txt = "#####\n#@$.#\n#####"
    lvl = parse_ascii(txt)
    assert lvl.width == 5 and lvl.height == 3
    assert len(lvl.walls) > 0
    assert len(lvl.start_boxes) == 1
    assert len(lvl.goals) == 1
    assert lvl.start_player is not None
