"""Batch experiment runner for Sokoban solvers."""

from __future__ import annotations

import argparse
import csv
import multiprocessing
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sokoban.search import astar, hill_climbing, ida, rbfs
from sokoban.core.levels import load_txt, parse_ascii, split_levels
from sokoban.core.model import Level


DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_LEVEL_FILES: List[Path] = [DATA_DIR / "tiny.txt"]
MICROBAN_PATH = DATA_DIR / "microban.txt"
_limit_env = os.environ.get("MICROBAN_LIMIT")
if _limit_env is None:
    MICROBAN_LIMIT: Optional[int] = 5
else:
    try:
        MICROBAN_LIMIT = int(_limit_env)
    except ValueError:
        MICROBAN_LIMIT = None

RESULTS_DIR = PROJECT_ROOT / "results"
DEFAULT_RESULTS_PATH = RESULTS_DIR / "summary.csv"

@dataclass(frozen=True)
class Task:
    name: str
    weight: float
    func: Callable[..., dict]
    extra: dict = field(default_factory=dict)
    timeout_s: Optional[float] = None


TASKS: List[Task] = [
    Task("astar", 1.0, astar.run),
    Task("wastar", 1.2, astar.run),
    Task("wastar", 1.5, astar.run),
    Task("wastar", 2.0, astar.run),
    Task("ida", 1.0, ida.run),
    Task("rbfs", 1.0, rbfs.run, extra={"max_expansions": 25000}, timeout_s=30.0),
    Task("hill", 1.0, hill_climbing.run, extra={"max_steps": 4000}, timeout_s=10.0),
]


class TaskTimeout(RuntimeError):
    """Raised when a solver exceeds its allotted runtime."""


def _task_worker(func: Callable[..., dict], level: Level, weight: float, extra: dict) -> dict:
    return func(level, weight=weight, **extra)


def _execute_task(level: Level, task: Task) -> dict:
    if task.timeout_s is None:
        return task.func(level, weight=task.weight, **task.extra)

    ctx = multiprocessing.get_context("spawn")
    pool = ctx.Pool(processes=1)
    async_result = pool.apply_async(_task_worker, (task.func, level, task.weight, task.extra))
    try:
        result = async_result.get(timeout=task.timeout_s)
    except multiprocessing.TimeoutError as exc:  # pragma: no cover - best effort guard
        pool.terminate()
        pool.join()
        raise TaskTimeout("solver timeout") from exc
    except Exception:
        pool.terminate()
        pool.join()
        raise
    else:
        pool.close()
        pool.join()
        return result


def _load_microban_boards(limit: Optional[int] = None) -> List[Tuple[str, str]]:
    boards: List[Tuple[str, str]] = []
    if not MICROBAN_PATH.exists():
        return boards

    allowed = set("#@$.+*$ ")
    lines = load_txt(str(MICROBAN_PATH)).splitlines()
    current_lines: List[str] = []
    pending_title: Optional[str] = None
    for line in lines:
        stripped = line.rstrip()
        if stripped.startswith("Title:"):
            pending_title = stripped.split("Title:", 1)[1].strip() or str(len(boards) + 1)
            if current_lines:
                title = pending_title or str(len(boards) + 1)
                board_text = "\n".join(current_lines).rstrip("\n")
                boards.append((f"microban_{title}", board_text))
                current_lines = []
                pending_title = None
                if limit and len(boards) >= limit:
                    break
        elif stripped and set(stripped).issubset(allowed):
            current_lines.append(stripped)

    if current_lines and (limit is None or len(boards) < limit):
        title = pending_title or str(len(boards) + 1)
        board_text = "\n".join(current_lines).rstrip("\n")
        boards.append((f"microban_{title}", board_text))

    if limit is not None:
        return boards[:limit]
    return boards


def _load_level_from_path(path: Path) -> List[Tuple[str, str]]:
    txt = load_txt(str(path))
    boards = split_levels(txt)
    prefix = path.stem or path.name
    if len(boards) == 1:
        return [(prefix, boards[0])]
    return [(f"{prefix}_{idx+1}", board) for idx, board in enumerate(boards)]


def _collect_levels(selected: Sequence[str], microban_limit: Optional[int]) -> List[Tuple[str, str]]:
    """Return (name, ascii) pairs to evaluate."""

    if not selected:
        levels = []
        for path in DEFAULT_LEVEL_FILES:
            if path.exists():
                levels.extend(_load_level_from_path(path))
        levels.extend(_load_microban_boards(microban_limit))
        return levels

    levels: List[Tuple[str, str]] = []
    microban_aliases = {"microban", "microban.txt"}
    resolved_microban = MICROBAN_PATH.resolve()
    for entry in selected:
        normalized = entry.lower()
        is_microban = normalized in microban_aliases
        path = Path(entry)
        if not path.exists():
            path = DATA_DIR / entry
        if not is_microban and path.exists():
            try:
                is_microban = path.resolve() == resolved_microban
            except FileNotFoundError:
                is_microban = False
        if is_microban:
            levels.extend(_load_microban_boards(microban_limit))
            continue
        if not path.exists():
            raise FileNotFoundError(f"Level file '{entry}' not found")
        levels.extend(_load_level_from_path(path))
    return levels


def run_all(levels: Sequence[Tuple[str, str]]) -> List[dict]:
    records: List[dict] = []
    for level_name, level_text in levels:
        level = parse_ascii(level_text)

        for task in TASKS:
            try:
                result = _execute_task(level, task)
                error_msg = ""
            except TaskTimeout:
                result = {
                    "status": "timeout",
                    "cost": None,
                    "path_length": 0,
                    "actions": [],
                    "pushes": [],
                    "segments": [],
                    "expansions": None,
                    "time_s": None,
                }
                error_msg = "timeout"
            except RecursionError:
                result = {
                    "status": "error",
                    "cost": None,
                    "path_length": 0,
                    "actions": [],
                    "pushes": [],
                    "segments": [],
                    "expansions": None,
                    "time_s": None,
                }
                error_msg = "recursion"
            except Exception as exc:  # pragma: no cover - best effort logging
                result = {
                    "status": "error",
                    "cost": None,
                    "path_length": 0,
                    "actions": [],
                    "pushes": [],
                    "segments": [],
                    "expansions": None,
                    "time_s": None,
                }
                error_msg = str(exc)
            record = {
                "level": level_name,
                "algorithm": task.name,
                "weight": task.weight,
                "status": result.get("status"),
                "cost": result.get("cost"),
                "path_length": result.get("path_length"),
                "expansions": result.get("expansions"),
                "time_s": result.get("time_s"),
                "actions": "".join(result.get("actions", [])),
                "pushes": "".join(result.get("pushes", [])),
                "error": error_msg,
            }
            records.append(record)

    return records


def save_csv(rows: Iterable[dict], path: Path) -> None:
    fieldnames = [
        "level",
        "algorithm",
        "weight",
        "status",
        "cost",
        "path_length",
        "expansions",
        "time_s",
        "actions",
        "pushes",
        "error",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _default_output_path(datasets: Sequence[str]) -> Path:
    if not datasets:
        return DEFAULT_RESULTS_PATH
    if len(datasets) == 1:
        stem = Path(datasets[0]).stem or datasets[0]
        return RESULTS_DIR / f"{stem}_summary.csv"
    joined = "_".join((Path(name).stem or name) for name in datasets)
    return RESULTS_DIR / f"{joined}_summary.csv"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Sokoban solver experiments")
    parser.add_argument(
        "datasets",
        nargs="*",
        help="Level files to evaluate (relative to data/ by default) or 'microban'",
    )
    parser.add_argument(
        "--microban-limit",
        type=int,
        default=MICROBAN_LIMIT,
        help="Maximum number of Microban boards to load",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Explicit path for the summary CSV",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    levels = _collect_levels(args.datasets, args.microban_limit)
    if not levels:
        raise SystemExit("No levels available to run")
    output_path = args.output or _default_output_path(args.datasets)
    rows = run_all(levels)
    save_csv(rows, output_path)
    print(f"Saved {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    main()
