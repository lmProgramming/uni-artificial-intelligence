import pytest

from clobber.board import Board


@pytest.mark.parametrize(("dimensions", "expected"),
                         [
    ((5, 6), "W B W B W B\nB W B W B W\nW B W B W B\nB W B W B W\nW B W B W B"),
    ((10, 10), "W B W B W B W B W B\nB W B W B W B W B W\nW B W B W B W B W B\nB W B W B W B W B W\nW B W B W B W B W B\nB W B W B W B W B W\nW B W B W B W B W B\nB W B W B W B W B W\nW B W B W B W B W B\nB W B W B W B W B W")
])
def test_board_generation(dimensions: tuple[int, int], expected: str) -> None:
    board: Board = Board.initialize_board(*dimensions)

    assert str(board) == expected


def test_neighbours() -> None:
    board: Board = Board.initialize_board(5, 6)

    black_neighbours: list[tuple[int, int]
                           ] = board.get_neighbours_positions_filtered((1, 1), lambda p: p == 'B')
    assert (0, 1) in black_neighbours
    assert (2, 1) in black_neighbours
    assert (1, 2) in black_neighbours
    assert (1, 0) in black_neighbours
    assert len(black_neighbours) == 4
    white_neighbours: list[tuple[int, int]
                           ] = board.get_neighbours_positions_filtered((1, 1), lambda p: p == 'W')
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


def test_replace_piece() -> None:
    board: Board = Board.initialize_board(2, 2)

    board.replace_piece_at((0, 0), '_')
    assert board.get_piece_at((0, 0)) == '_'

    board.replace_piece_at((1, 1), '_')
    assert board.get_piece_at((1, 1)) == '_'

    board.replace_piece_at((0, 0), 'B')
    assert board.get_piece_at((0, 0)) == 'B'

    board.replace_piece_at((1, 0), 'B')
    assert board.get_piece_at((1, 0)) == 'B'


def test_move() -> None:
    board: Board = Board.initialize_board(5, 6)

    board.move_assuming_correct('W', ((0, 0), (1, 0)))

    assert board.get_piece_at((0, 0)) == '_'
    assert board.get_piece_at((1, 0)) == 'W'


def test_get_all_pieces() -> None:
    board: Board = Board.initialize_board(3, 3)

    white_positions: list[tuple[int, int]] = board.get_all_pieces('W')
    black_positions: list[tuple[int, int]] = board.get_all_pieces('B')

    assert len(white_positions) == 5
    assert len(black_positions) == 4
    assert (0, 0) in white_positions
    assert (1, 0) in black_positions


def test_has_moves() -> None:
    board: Board = Board.initialize_board(2, 2)

    assert board.has_moves(True)
    assert board.has_moves(False)

    board.replace_piece_at((0, 0), '_')
    board.replace_piece_at((1, 0), '_')
    board.replace_piece_at((0, 1), '_')
    board.replace_piece_at((1, 1), '_')

    assert not board.has_moves(True)
    assert not board.has_moves(False)


def test_copy() -> None:
    board: Board = Board.initialize_board(2, 2)
    board_copy: Board = board.copy()

    assert str(board) == str(board_copy)

    board_copy.replace_piece_at((0, 0), '_')
    assert board.get_piece_at((0, 0)) == 'W'
    assert board_copy.get_piece_at((0, 0)) == '_'


def test_turn() -> None:
    board: Board = Board.initialize_board(5, 5)

    assert board.turn == 0
    board.move_assuming_correct('W', ((0, 0), (0, 1)))
    assert board.turn == 1
    new_board: Board = board.copy()
    assert new_board.turn == 1
    board.move_assuming_correct('W', ((0, 1), (1, 0)))
    assert new_board.turn == 1
    assert board.turn == 2
