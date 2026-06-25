from __future__ import annotations

import math
import time
from dataclasses import dataclass

from src.bitboard import (
    BOARD_SIZE,
    CELL_COUNT,
    Move,
    count_empty,
    empty_cells,
    execute_move,
    get_cell,
    max_rank,
    set_cell,
)


MOVE_ORDER = (Move.UP, Move.LEFT, Move.RIGHT, Move.DOWN)
SNAKE_WEIGHTS = (
    65536,
    32768,
    16384,
    8192,
    512,
    1024,
    2048,
    4096,
    256,
    128,
    64,
    32,
    2,
    4,
    8,
    16,
)


class SearchTimeout(Exception):
    pass


@dataclass
class ExpectimaxAI:
    max_depth: int = 6
    time_limit: float = 0.08
    chance_sample_limit: int = 8

    def choose_move(self, board: int) -> Move | None:
        legal_moves = []
        for move in MOVE_ORDER:
            child, score, moved = execute_move(board, move)
            if moved:
                legal_moves.append((move, child, score))

        if not legal_moves:
            return None

        deadline = time.perf_counter() + self.time_limit
        best_move = legal_moves[0][0]
        best_value = -math.inf

        try:
            for depth in range(2, self.max_depth + 1):
                current_move = best_move
                current_value = -math.inf
                for move, child, score in legal_moves:
                    self._check_time(deadline)
                    value = score + self._chance_value(child, depth - 1, deadline)
                    if value > current_value:
                        current_value = value
                        current_move = move
                best_move = current_move
                best_value = current_value
        except SearchTimeout:
            return best_move

        return best_move if best_value > -math.inf else legal_moves[0][0]

    def _max_value(self, board: int, depth: int, deadline: float) -> float:
        self._check_time(deadline)
        if depth <= 0:
            return evaluate(board)

        best = -math.inf
        moved_any = False
        for move in MOVE_ORDER:
            child, score, moved = execute_move(board, move)
            if not moved:
                continue
            moved_any = True
            best = max(best, score + self._chance_value(child, depth - 1, deadline))

        return best if moved_any else evaluate(board) - 1_000_000

    def _chance_value(self, board: int, depth: int, deadline: float) -> float:
        self._check_time(deadline)
        cells = empty_cells(board)
        if depth <= 0 or not cells:
            return evaluate(board)

        cells = self._important_cells(board, cells)
        probability = 1.0 / len(cells)
        expected = 0.0

        for index in cells:
            board_with_2 = set_cell(board, index, 1)
            board_with_4 = set_cell(board, index, 2)
            expected += probability * (
                0.9 * self._max_value(board_with_2, depth - 1, deadline)
                + 0.1 * self._max_value(board_with_4, depth - 1, deadline)
            )

        return expected

    def _important_cells(self, board: int, cells: list[int]) -> list[int]:
        if len(cells) <= self.chance_sample_limit:
            return cells

        scored = []
        for index in cells:
            with_2 = set_cell(board, index, 1)
            scored.append((evaluate(with_2), index))
        scored.sort()
        return [index for _, index in scored[: self.chance_sample_limit]]

    @staticmethod
    def _check_time(deadline: float) -> None:
        if time.perf_counter() >= deadline:
            raise SearchTimeout


def evaluate(board: int) -> float:
    empty = count_empty(board)
    max_tile_rank = max_rank(board)
    smoothness = _smoothness(board)
    monotonicity = _monotonicity(board)
    corner = _corner_bonus(board, max_tile_rank)
    snake = _snake_score(board)

    return (
        empty * empty * 2600.0
        + monotonicity * 1200.0
        + smoothness * 110.0
        + corner * 9500.0
        + snake * 1.15
        + (1 << max_tile_rank) * 2.0
    )


def _smoothness(board: int) -> float:
    penalty = 0.0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            index = row * BOARD_SIZE + col
            value = get_cell(board, index)
            if value == 0:
                continue
            if col + 1 < BOARD_SIZE:
                right = get_cell(board, index + 1)
                if right:
                    penalty -= abs(value - right)
            if row + 1 < BOARD_SIZE:
                down = get_cell(board, index + BOARD_SIZE)
                if down:
                    penalty -= abs(value - down)
    return penalty


def _monotonicity(board: int) -> float:
    totals = [0.0, 0.0, 0.0, 0.0]

    for row in range(BOARD_SIZE):
        values = [get_cell(board, row * BOARD_SIZE + col) for col in range(BOARD_SIZE)]
        for left, right in zip(values, values[1:]):
            if left > right:
                totals[0] += right - left
            elif right > left:
                totals[1] += left - right

    for col in range(BOARD_SIZE):
        values = [get_cell(board, row * BOARD_SIZE + col) for row in range(BOARD_SIZE)]
        for top, bottom in zip(values, values[1:]):
            if top > bottom:
                totals[2] += bottom - top
            elif bottom > top:
                totals[3] += top - bottom

    return max(totals[0], totals[1]) + max(totals[2], totals[3])


def _corner_bonus(board: int, rank: int) -> float:
    corners = (0, 3, 12, 15)
    if any(get_cell(board, index) == rank for index in corners):
        return float(1 << rank)
    return -float(1 << rank)


def _snake_score(board: int) -> float:
    score = 0.0
    for index in range(CELL_COUNT):
        rank = get_cell(board, index)
        if rank:
            score += SNAKE_WEIGHTS[index] * rank
    return score
