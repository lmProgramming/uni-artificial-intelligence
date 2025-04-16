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
