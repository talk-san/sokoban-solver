# Sokoban Solver

Scaffolding for a Sokoban Solver project

## Quick start
```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m sokoban parse data/tiny.txt
python -m sokoban run-astar data/tiny.txt
```

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
