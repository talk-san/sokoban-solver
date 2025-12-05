import json
import click
from .core.levels import load_txt, parse_ascii
from .search.astar import run as run_astar
from .search.hill_climbing import run as run_hill
from .search.ida import run as run_ida
from .search.rbfs import run as run_rbfs


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
@click.option("--weight", type=float, default=1.0, show_default=True,
              help="Weighted A* factor (1.0 = standard A*)")
def run_astar_cmd(level_path, weight):
    """Loads a level and runs push-based (Weighted) A*."""
    txt = load_txt(level_path)
    lvl = parse_ascii(txt)
    result = run_astar(lvl, weight=weight)
    click.echo(json.dumps(result, indent=2))


@main.command("run-ida")
@click.argument("level_path", type=click.Path(exists=True))
@click.option("--weight", type=float, default=1.0, show_default=True,
              help="Weighted IDA* factor (1.0 = standard IDA*)")
def run_ida_cmd(level_path, weight):
    """Loads a level and runs (Weighted) IDA*."""
    txt = load_txt(level_path)
    lvl = parse_ascii(txt)
    result = run_ida(lvl, weight=weight)
    click.echo(json.dumps(result, indent=2))


@main.command("run-rbfs")
@click.argument("level_path", type=click.Path(exists=True))
@click.option("--weight", type=float, default=1.0, show_default=True,
              help="Weight applied to the heuristic")
@click.option("--max-expansions", type=int, default=25000, show_default=True,
              help="Stop after exploring this many push states")
def run_rbfs_cmd(level_path, weight, max_expansions):
    """Loads a level and runs Recursive Best-First Search."""
    txt = load_txt(level_path)
    lvl = parse_ascii(txt)
    result = run_rbfs(lvl, weight=weight, max_expansions=max_expansions)
    click.echo(json.dumps(result, indent=2))


@main.command("run-hill")
@click.argument("level_path", type=click.Path(exists=True))
@click.option("--weight", type=float, default=1.0, show_default=True,
              help="Weight applied to the heuristic")
@click.option("--max-steps", type=int, default=2000, show_default=True,
              help="Maximum pushes to explore")
@click.option("--allow-sideways/--no-sideways", default=False, show_default=True,
              help="Allow moves that keep heuristic equal (can cause loops)")
def run_hill_cmd(level_path, weight, max_steps, allow_sideways):
    """Loads a level and runs greedy hill climbing."""
    txt = load_txt(level_path)
    lvl = parse_ascii(txt)
    result = run_hill(lvl, weight=weight, max_steps=max_steps, allow_sideways=allow_sideways)
    click.echo(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
