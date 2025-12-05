# Sokoban Solver

Scaffolding for a Sokoban Solver project

## Quick start
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m sokoban parse data/tiny.txt
python -m sokoban run-astar data/tiny.txt
python scripts/run_experiments.py data/tiny.txt
```

## Running experiments
Use the batch runner to evaluate every solver on all levels contained in a file.

```
python scripts/run_experiments.py data/tiny.txt
python scripts/run_experiments.py data/microban.txt
```

The first command reads every level in `data/tiny.txt` and writes
`results/tiny_summary.csv`; the second command loads `data/microban.txt` and
writes `results/microban_summary.csv`. Pass other datasets or `--output` to
customize what gets evaluated and where the CSV is written. When running
Microban, you can use the `MICROBAN_LIMIT` environment variable (defaults to 5)
to cap how many boards are included in the experiment.

## ASCII legend
```
# wall
@ player
+ player on goal
$ box
* box on goal
. goal
  floor
```

## Example level
```
#####
#@$.#
#####
```
