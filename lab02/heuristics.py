import random
from abc import ABC, abstractmethod

from clobber.board import Board
from clobber.types import piece_type
from heuristic_helpers import get_subgames


class Heuristic(ABC):
    @abstractmethod
    def calculate(self, board: Board, for_white: bool) -> float:
        ...


class Random(Heuristic):
    def calculate(self, board: Board, for_white: bool) -> float:
        return random.uniform(-10000, 10000)


class PieceSafetyHeuristic(Heuristic):
    '''
    Measures how many of your pieces can be captured by the opponent versus how many opponent pieces can be captured by you
    '''

    def calculate(self, board: Board, for_white: bool) -> float:
        my_player: piece_type = 'W' if for_white else 'B'
        opponent_player: piece_type = 'B' if for_white else 'W'

        my_pieces: list[tuple[int, int]] = board.get_all_pieces(my_player)
        opponent_pieces: list[tuple[int, int]
                              ] = board.get_all_pieces(opponent_player)

        my_vulnerable_count = 0
        for my_pos in my_pieces:
            my_vulnerable_count += 1 if board.get_neighbours_positions_filtered(
                my_pos, lambda p: p == opponent_player) else 0

        opponent_vulnerable_count = 0
        for opp_pos in opponent_pieces:
            opponent_vulnerable_count += 1 if board.get_neighbours_positions_filtered(
                opp_pos, lambda p: p == my_player) else 0

        score = float(opponent_vulnerable_count - my_vulnerable_count)
        return score * (1 if for_white else -1)


class CenterControlHeuristic(Heuristic):
    '''
    Heuristic assumes pieces should move towards center
    '''

    def calculate(self, board: Board, for_white: bool) -> float:
        my_player: piece_type = 'W' if for_white else 'B'
        opponent_player: piece_type = 'B' if for_white else 'W'

        center_x: float = (board.m - 1) / 2.0
        center_y: float = (board.n - 1) / 2.0

        my_score = 0.0
        for x, y in board.get_all_pieces(my_player):
            dist_sq: float = (x - center_x)**2 + (y - center_y)**2
            # Add small epsilon to avoid division by zero if piece is exactly center
            my_score += 1.0 / (1.0 + dist_sq + 1e-6)

        opponent_score = 0.0
        for x, y in board.get_all_pieces(opponent_player):
            dist_sq = (x - center_x)**2 + (y - center_y)**2
            opponent_score += 1.0 / (1.0 + dist_sq + 1e-6)

        score: float = my_score - opponent_score
        return score * (1 if for_white else -1)


class SubgameControlHeuristic(Heuristic):
    """
    Evaluates board state based on the piece difference (own - opponent)
    summed across all active subgames (subgames with both colors).
    """

    def calculate(self, board: Board, for_white: bool) -> float:
        my_player: piece_type = 'W' if for_white else 'B'
        opponent_player: piece_type = 'B' if for_white else 'W'

        active_subgames = get_subgames(board)
        total_score = 0.0

        if not active_subgames:
            return 0.0

        for sub_game in active_subgames:
            my_pieces = 0
            opponent_pieces = 0
            for _, piece in sub_game:
                if piece == my_player:
                    my_pieces += 1
                elif piece == opponent_player:
                    opponent_pieces += 1
            total_score += (my_pieces - opponent_pieces)

        return float(total_score) * (1 if for_white else -1)


class LocalActivityHeuristic(Heuristic):
    """
    Evaluates board state based on the number of opponent pieces adjacent
    to *our* pieces. More adjacent opponents means more potential future captures.
    """

    def calculate(self, board: Board, for_white: bool) -> float:
        my_player: piece_type = 'W' if for_white else 'B'
        opponent_player: piece_type = 'B' if for_white else 'W'

        total_activity_score = 0.0
        my_piece_positions: list[tuple[int, int]] = board.get_all_pieces(
            my_player)

        for my_pos in my_piece_positions:
            adjacent_opponents: int = len(board.get_neighbours_positions_filtered(
                my_pos, lambda p: p == opponent_player))
            total_activity_score += adjacent_opponents

        return float(total_activity_score) * (1 if for_white else -1)
