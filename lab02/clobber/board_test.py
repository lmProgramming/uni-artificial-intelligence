from board import Board
import pytest


@pytest.mark.parametrize(("dimensions", "expected"),
                         [
    ((5, 6), "W_B_W_B_W_B\nB_W_B_W_B_W\nW_B_W_B_W_B\nB_W_B_W_B_W\nW_B_W_B_W_B"),
    ((10, 10), "W_B_W_B_W_B_W_B_W_B\nB_W_B_W_B_W_B_W_B_W\nW_B_W_B_W_B_W_B_W_B\nB_W_B_W_B_W_B_W_B_W\nW_B_W_B_W_B_W_B_W_B\nB_W_B_W_B_W_B_W_B_W\nW_B_W_B_W_B_W_B_W_B\nB_W_B_W_B_W_B_W_B_W\nW_B_W_B_W_B_W_B_W_B\nB_W_B_W_B_W_B_W_B_W")
])
def test_board_generation(dimensions: tuple[int, int], expected: str) -> None:
    board: Board = Board.initialize_board(*dimensions)

    assert str(board) == expected


def test_neighbours() -> None:
    board: Board = Board.initialize_board(5, 6)

    black_neighbours: list[tuple[int, int]
                           ] = board.get_neighbours_positions_filtered((1, 1), 'B')
    assert (0, 1) in black_neighbours
    assert (2, 1) in black_neighbours
    assert (1, 2) in black_neighbours
    assert (1, 0) in black_neighbours
    assert len(black_neighbours) == 4
    white_neighbours: list[tuple[int, int]
                           ] = board.get_neighbours_positions_filtered((1, 1), 'W')
    assert len(white_neighbours) == 0


def test_get_piece() -> None:
    board: Board = Board.initialize_board(5, 6)

    assert board.get_piece_at((5, 4)) == 'B'
    assert board.get_piece_at((5, 5)) == 'outside'
    assert board.get_piece_at((6, 4)) == 'outside'


def test_generate_moves() -> None:
    board: Board = Board.initialize_board(2, 2)

    moves: dict[tuple[int, int], list[tuple[int, int]]
                ] = board.generate_moves(True)

    assert moves[(0, 0)] == [(1, 0), (0, 1)]
    assert moves[(1, 1)] == [(0, 1), (1, 0)]
