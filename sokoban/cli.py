import json
import click
from .levels import load_txt, parse_ascii
from .astar import run as run_astar


@click.group()
def main():
    pass


@main.command()
@click.argument("level_path", type=click.Path(exists=True))
def parse(level_path):
    """Prints a brief summary of a Sokoban level."""
    txt = load_txt(level_path)
    lvl = parse_ascii(txt)
    click.echo(json.dumps({
        "width": lvl.width,
        "height": lvl.height,
        "walls": len(lvl.walls),
        "goals": len(lvl.goals),
        "boxes": len(lvl.start_boxes),
        "player": lvl.start_player,
    }, indent=2))


@main.command("run-astar")
@click.argument("level_path", type=click.Path(exists=True))
def run_astar_cmd(level_path):
    """Runs a tiny placeholder A* (to be implemented)."""
    txt = load_txt(level_path)
    lvl = parse_ascii(txt)
    result = run_astar(lvl)
    click.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
