import pytest
from unittest.mock import MagicMock
from clobber.board import Board
from heuristic_helpers import get_subgames


@pytest.fixture
def mock_board() -> Board:
    # Fixture to provide a mocked Board instance
    board = MagicMock(spec=Board)
    return board


def test_empty_board(mock_board):
    # Test case: Empty board (no pieces)
    mock_board.n = 3
    mock_board.m = 3
    mock_board.get_piece_at = MagicMock(side_effect=lambda pos: 0)
    mock_board.get_neighbours_positions = MagicMock(return_value=[])

    subgames = get_subgames(mock_board)
    assert subgames == []


def test_single_piece_board(mock_board):
    # Test case: Board with a single piece
    mock_board.n = 3
    mock_board.m = 3
    mock_board.get_piece_at = MagicMock(
        side_effect=lambda pos: 'B' if pos == (1, 1) else 0)
    mock_board.get_neighbours_positions = MagicMock(return_value=[])

    subgames = get_subgames(mock_board)
    assert subgames == []


def test_connected_subgame(mock_board):
    # Test case: A connected subgame with both 'B' and 'W'
    mock_board.n = 3
    mock_board.m = 3
    mock_board.get_piece_at = MagicMock(side_effect=lambda pos: {
        (0, 0): 'B', (0, 1): 'W', (1, 0): 'B', (1, 1): 'W'
    }.get(pos, 0))
    mock_board.get_neighbours_positions = MagicMock(side_effect=lambda pos: {
        (0, 0): [(0, 1), (1, 0)],
        (0, 1): [(0, 0), (1, 1)],
        (1, 0): [(0, 0), (1, 1)],
        (1, 1): [(0, 1), (1, 0)]
    }.get(pos, []))

    subgames = get_subgames(mock_board)
    assert len(subgames) == 1
    assert ((0, 0), 'B') in subgames[0]
    assert ((0, 1), 'W') in subgames[0]
    assert ((1, 0), 'B') in subgames[0]
    assert ((1, 1), 'W') in subgames[0]


def test_disconnected_subgames(mock_board):
    # Test case: Two disconnected subgames
    mock_board.n = 4
    mock_board.m = 4
    mock_board.get_piece_at = MagicMock(side_effect=lambda pos: {
        (0, 0): 'B', (0, 1): 'W', (3, 3): 'B', (3, 2): 'W'
    }.get(pos, 0))
    mock_board.get_neighbours_positions = MagicMock(side_effect=lambda pos: {
        (0, 0): [(0, 1)],
        (0, 1): [(0, 0)],
        (3, 3): [(3, 2)],
        (3, 2): [(3, 3)]
    }.get(pos, []))

    subgames = get_subgames(mock_board)
    assert len(subgames) == 2
    assert ((0, 0), 'B') in subgames[0]
    assert ((0, 1), 'W') in subgames[0]
    assert ((3, 3), 'B') in subgames[1]
    assert ((3, 2), 'W') in subgames[1]


def test_single_color_subgame(mock_board):
    # Test case: Subgame with only one color
    mock_board.n = 3
    mock_board.m = 3
    mock_board.get_piece_at = MagicMock(side_effect=lambda pos: {
        (0, 0): 'B', (0, 1): 'B', (1, 0): 'B'
    }.get(pos, 0))
    mock_board.get_neighbours_positions = MagicMock(side_effect=lambda pos: {
        (0, 0): [(0, 1), (1, 0)],
        (0, 1): [(0, 0)],
        (1, 0): [(0, 0)]
    }.get(pos, []))

    subgames = get_subgames(mock_board)
    assert subgames == []
