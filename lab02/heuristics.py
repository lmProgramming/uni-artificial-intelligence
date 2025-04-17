from _collections_abc import dict_items
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
        return random.randrange(-10000, 10000)


class AvailableMoves(Heuristic):
    def calculate(self, board: Board, for_white: bool) -> float:
        moves_good: dict_items[tuple[int, int], list[tuple[int, int]]
                               ] = board.generate_moves(for_white).items()

        moves_bad: dict_items[tuple[int, int], list[tuple[int, int]]
                              ] = board.generate_moves(not for_white).items()

        return (sum(len(possibilites) for _, possibilites in moves_good) + sum(len(possibilites) for _, possibilites in moves_bad)) * (1 if for_white else -1)


# --- Heuristic 1: Mobility Focus ---
class MobilityHeuristic(Heuristic):
    """
    Evaluates board state based on the difference in the number of available moves.
    Higher score = more moves for the player whose turn it is relative to opponent.
    """

    def calculate(self, board: Board, for_white: bool) -> float:
        my_player: piece_type = 'W' if for_white else 'B'
        opponent_player: piece_type = 'B' if for_white else 'W'

        # Count moves by summing lengths of possibilities lists from generate_moves
        my_moves_map: dict[tuple[int, int], list[tuple[int, int]]
                           ] = board.generate_moves(True)
        my_moves_count: int = sum(len(possibilities)
                                  for _, possibilities in my_moves_map.items())

        opponent_moves_map: dict[tuple[int, int],
                                 list[tuple[int, int]]] = board.generate_moves(False)
        opponent_moves_count: int = sum(len(possibilities)
                                        for _, possibilities in opponent_moves_map.items())

        # Simple difference
        score = float(my_moves_count - opponent_moves_count)

        # The heuristic interface doesn't specify *whose turn* it is, only who
        # the score should favor. This calculates the mobility *advantage*
        # for the player specified by `for_white`.
        return score


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
            # No active subgames - could be end game or fully separated.
            # Check who has remaining moves. If only we do, score high. If only opponent, score low.
            my_moves_map = board.generate_moves(for_white)
            my_moves_count = sum(len(p) for _, p in my_moves_map.items())
            opponent_moves_map = board.generate_moves(not for_white)
            opponent_moves_count = sum(len(p)
                                       for _, p in opponent_moves_map.items())

            if my_moves_count > 0 and opponent_moves_count == 0:
                return 10000.0  # High score, likely win
            elif my_moves_count == 0 and opponent_moves_count > 0:
                return -10000.0  # Low score, likely loss
            else:
                return 0.0  # Draw state or both have moves in isolated blocks

        for sg in active_subgames:
            my_pieces = 0
            opponent_pieces = 0
            for _point, piece in sg:
                if piece == my_player:
                    my_pieces += 1
                elif piece == opponent_player:
                    opponent_pieces += 1
            total_score += (my_pieces - opponent_pieces)

        return float(total_score)


# --- Heuristic 3: Local Activity Focus ---
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
            my_player)  # Assumes this board method exists

        for my_pos in my_piece_positions:
            adjacent_opponents: int = len(board.get_neighbours_positions_filtered(
                my_pos, lambda p: p == opponent_player))
            total_activity_score += adjacent_opponents

        # This score naturally favors the player `for_white`.
        return float(total_activity_score)
