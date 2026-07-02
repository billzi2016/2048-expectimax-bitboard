# 2048 Expectimax Bitboard

A pure algorithmic 2048 AI built with `Expectimax` tree search, a 64-bit `bitboard` board representation, row-move lookup tables, and heuristic evaluation. The main program can simulate multiple games in one run and save every board state after each move into directories such as `games/001/001.jpg`.

## Directory Structure

```text
main.py                 # Main entry point
src/
  ai.py                 # Expectimax and evaluation functions
  bitboard.py           # 64-bit board, move rules, lookup tables
  game.py               # 2048 random tile spawning and game loop
  render.py             # JPG board rendering
games/
  001/
    001.jpg              # Initial board
    002.jpg              # After move 1
    003.jpg              # After move 2
    ...
```

## Install Dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Run

Simulate 5 games:

```bash
python3 main.py --games 5
```

Specify the search depth and per-move time budget:

```bash
python3 main.py --games 5 --depth 7 --time-limit 0.12
```

Set a fixed random seed for reproducible experiments:

```bash
python3 main.py --games 5 --seed 2048
```

Generate a Markdown report with rendered board images:

```bash
python3 report_maker.py
```

Reports are written to `reports/`. For example, `reports/001.md` references all move images from `games/001/` in order.

## Algorithm Notes

The board is compressed into a 64-bit integer. Each of the 16 cells occupies 4 bits, and each tile stores its exponent instead of its raw value. For example, `2` is stored as `1`, `2048` is stored as `11`, and `32768` is stored as `15`. This means the maximum tile value supported by this implementation is `32768`.

Left and right moves are handled through precomputed lookup tables for all 65,536 possible row states. Up and down moves transpose the board first, then reuse the row-move tables.

The AI uses Expectimax:

- The `MAX` layer enumerates up, down, left, and right, then chooses the move with the highest expected score.
- The `CHANCE` layer enumerates empty cells and computes the expected value after random tile spawning with `2=90%` and `4=10%`.
- When many empty cells are available, the search samples a subset of the most dangerous spawn positions to reduce search explosion.

The leaf-node evaluation function includes:

- Empty cells: more free space is safer.
- Monotonicity: encourages large values to remain ordered along rows or columns.
- Smoothness: encourages adjacent tiles to have similar values, making merges easier.
- Corner control: encourages the largest tile to stay in a corner.
- Snake weights: encourages large tiles to cluster along a fixed path.

## Termination Conditions

The program does not run forever. A game ends when either of the following conditions is met:

- The board reaches the maximum tile supported by the 64-bit bitboard encoding: `32768`.
- The board has no legal moves left.

To support `65536` or larger tiles, the per-cell encoding would need to grow beyond 4 bits. The current classic layout works because it fits exactly into a single `uint64`.

## Win Rate Notes

This implementation aims for a high win rate, but 2048 includes random tile spawning, so there is no deterministic guarantee that every game will reach `32768`. Increasing `--depth` and `--time-limit` usually improves performance at the cost of slower execution.
