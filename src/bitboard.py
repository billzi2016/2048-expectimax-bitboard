from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Move(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


ROW_MASK = 0xFFFF
CELL_MASK = 0xF
BOARD_SIZE = 4
CELL_COUNT = 16
MAX_RANK = 15
MAX_TILE = 1 << MAX_RANK


@dataclass(frozen=True)
class RowResult:
    row: int
    score: int
    moved: bool


def row_to_cells(row: int) -> list[int]:
    return [(row >> (4 * i)) & CELL_MASK for i in range(BOARD_SIZE)]


def cells_to_row(cells: list[int] | tuple[int, ...]) -> int:
    row = 0
    for index, value in enumerate(cells):
        row |= int(value) << (4 * index)
    return row


def reverse_row(row: int) -> int:
    return (
        ((row & 0xF000) >> 12)
        | ((row & 0x0F00) >> 4)
        | ((row & 0x00F0) << 4)
        | ((row & 0x000F) << 12)
    )


def execute_row_left(row: int) -> RowResult:
    original = row_to_cells(row)
    tiles = [value for value in original if value]
    merged: list[int] = []
    score = 0
    index = 0

    while index < len(tiles):
        if index + 1 < len(tiles) and tiles[index] == tiles[index + 1]:
            value = min(tiles[index] + 1, MAX_RANK)
            merged.append(value)
            score += 1 << value
            index += 2
        else:
            merged.append(tiles[index])
            index += 1

    merged.extend([0] * (BOARD_SIZE - len(merged)))
    new_row = cells_to_row(merged)
    return RowResult(row=new_row, score=score, moved=new_row != row)


ROW_LEFT = [execute_row_left(row) for row in range(1 << 16)]
ROW_RIGHT = [
    RowResult(
        row=reverse_row(ROW_LEFT[reverse_row(row)].row),
        score=ROW_LEFT[reverse_row(row)].score,
        moved=reverse_row(ROW_LEFT[reverse_row(row)].row) != row,
    )
    for row in range(1 << 16)
]


def get_cell(board: int, index: int) -> int:
    return (board >> (4 * index)) & CELL_MASK


def set_cell(board: int, index: int, value: int) -> int:
    shift = 4 * index
    board &= ~(CELL_MASK << shift)
    board |= min(value, MAX_RANK) << shift
    return board


def get_row(board: int, row_index: int) -> int:
    return (board >> (16 * row_index)) & ROW_MASK


def set_row(board: int, row_index: int, row: int) -> int:
    shift = 16 * row_index
    board &= ~(ROW_MASK << shift)
    board |= (row & ROW_MASK) << shift
    return board


def transpose(board: int) -> int:
    result = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            value = get_cell(board, row * BOARD_SIZE + col)
            result = set_cell(result, col * BOARD_SIZE + row, value)
    return result


def move_left(board: int) -> tuple[int, int, bool]:
    result = board
    score = 0
    moved = False
    for row_index in range(BOARD_SIZE):
        row = get_row(board, row_index)
        row_result = ROW_LEFT[row]
        result = set_row(result, row_index, row_result.row)
        score += row_result.score
        moved = moved or row_result.moved
    return result, score, moved


def move_right(board: int) -> tuple[int, int, bool]:
    result = board
    score = 0
    moved = False
    for row_index in range(BOARD_SIZE):
        row = get_row(board, row_index)
        row_result = ROW_RIGHT[row]
        result = set_row(result, row_index, row_result.row)
        score += row_result.score
        moved = moved or row_result.moved
    return result, score, moved


def execute_move(board: int, move: Move) -> tuple[int, int, bool]:
    if move == Move.LEFT:
        return move_left(board)
    if move == Move.RIGHT:
        return move_right(board)

    transposed = transpose(board)
    if move == Move.UP:
        moved_board, score, moved = move_left(transposed)
    else:
        moved_board, score, moved = move_right(transposed)
    return transpose(moved_board), score, moved


def empty_cells(board: int) -> list[int]:
    return [index for index in range(CELL_COUNT) if get_cell(board, index) == 0]


def count_empty(board: int) -> int:
    total = 0
    for index in range(CELL_COUNT):
        total += get_cell(board, index) == 0
    return total


def max_rank(board: int) -> int:
    return max(get_cell(board, index) for index in range(CELL_COUNT))


def board_to_matrix(board: int) -> list[list[int]]:
    matrix: list[list[int]] = []
    for row in range(BOARD_SIZE):
        matrix_row = []
        for col in range(BOARD_SIZE):
            rank = get_cell(board, row * BOARD_SIZE + col)
            matrix_row.append(0 if rank == 0 else 1 << rank)
        matrix.append(matrix_row)
    return matrix


def matrix_to_board(matrix: list[list[int]]) -> int:
    board = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            value = matrix[row][col]
            rank = 0 if value == 0 else value.bit_length() - 1
            board = set_cell(board, row * BOARD_SIZE + col, rank)
    return board
