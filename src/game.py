from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.bitboard import MAX_TILE, Move, empty_cells, execute_move, max_rank, set_cell


@dataclass
class Game2048:
    seed: int | None = None
    board: int = 0
    score: int = 0
    moves: int = 0
    rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        if self.board == 0:
            self.add_random_tile()
            self.add_random_tile()

    @property
    def max_tile(self) -> int:
        rank = max_rank(self.board)
        return 0 if rank == 0 else 1 << rank

    @property
    def is_over(self) -> bool:
        return self.max_tile >= MAX_TILE or not any(
            execute_move(self.board, move)[2] for move in Move
        )

    def move(self, move: Move) -> bool:
        new_board, gained, moved = execute_move(self.board, move)
        if not moved:
            return False
        self.board = new_board
        self.score += gained
        self.moves += 1
        self.add_random_tile()
        return True

    def add_random_tile(self) -> None:
        cells = empty_cells(self.board)
        if not cells:
            return
        index = self.rng.choice(cells)
        rank = 1 if self.rng.random() < 0.9 else 2
        self.board = set_cell(self.board, index, rank)
