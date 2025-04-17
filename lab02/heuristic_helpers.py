import random
from typing import Optional
from clobber.board import Board
from lab02.clobber.types import piece_type, move


def get_subgames(board: Board) -> list[list[tuple[tuple[int, int], piece_type]]]:
    """
    Identifies independent connected components (subgames/blocks) on the board.
    Returns a list of subgame representations (list of (Point, piece_type)).
    """
    rows: int = board.n
    cols: int = board.m
    visited = set()
    subgames: list[list[tuple[tuple[int, int], piece_type]]] = []

    for r in range(rows):
        for c in range(cols):
            start_point: tuple[int, int] = (r, c)
            piece: piece_type = board.get_piece_at(start_point)
            if piece != 0 and start_point not in visited:
                current_subgame_points: list[tuple[tuple[int, int], piece_type]] = [
                ]
                queue: list[tuple[int, int]] = [start_point]
                visited.add(start_point)
                has_black = False
                has_white = False

                while queue:
                    point: tuple[int, int] = queue.pop(0)
                    current_piece: piece_type = board.get_piece_at(point)
                    current_subgame_points.append((point, current_piece))
                    if current_piece == 'B':
                        has_black = True
                    if current_piece == 'W':
                        has_white = True

                    for neighbor in board.get_neighbours_positions(point):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                if has_black and has_white:
                    subgames.append(current_subgame_points)

    return subgames


def strategy_mobility(board: Board, player: piece_type) -> Optional[tuple[tuple[int, int], tuple[int, int]]]:
    """
    Chooses a move that minimizes the opponent's subsequent number of legal moves.
    """
    legal_moves = board.generate_moves(player == "W")
    if not legal_moves:
        return None

    opponent = 'W' if player == 'B' else 'B'
    move_options = []

    for move in legal_moves:
        next_board = board.copy()
        next_board.move_assuming_correct(move)
        opponent_moves_count = len(next_board.get_legal_moves(opponent))
        move_options.append((move, opponent_moves_count))

    # Separate moves that leave opponent with options vs. winning moves
    non_winning_moves = [(m, c) for m, c in move_options if c > 0]
    winning_moves = [(m, c) for m, c in move_options if c == 0]

    if winning_moves:
        # If there's a winning move, take any one
        return random.choice(winning_moves)[0]
    elif non_winning_moves:
        # Find the minimum number of opponent options among non-winning moves
        min_opponent_options = min(c for m, c in non_winning_moves)
        # Get all moves that achieve this minimum
        best_moves = [m for m, c in non_winning_moves if c ==
                      min_opponent_options]
        return random.choice(best_moves)
    else:
        # This case should ideally not happen if legal_moves is not empty,
        # but as a fallback, return any legal move.
        return random.choice(legal_moves)

# --- Strategy 2: Subgame Piece Control ---


def strategy_subgame_control(board: Board, player: piece_type) -> Optional[move]:
    """
    Chooses a move that maximizes the piece difference (own - opponent)
    summed across all active subgames in the resulting position.
    """
    legal_moves = board.generate_moves(player == 'W')
    if not legal_moves:
        return None

    opponent = 'W' if player == 'B' else 'B'
    best_score = -float('inf')
    best_moves = []

    for move in legal_moves:
        next_board = board.apply_move(move)
        active_subgames = get_subgames(next_board)  # Use the provided function
        current_board_score: float = 0

        if not active_subgames:
            # If move leads to no active subgames (e.g., game ends or separates completely)
            # This could be a win. Give it a high score. Or check if opponent has moves.
            if not next_board.get_legal_moves(opponent):
                current_board_score = float('inf')  # Likely a winning move
            else:
                # Neutral state? Or opponent only has moves in isolated blocks.
                current_board_score = 0
        else:
            for sg in active_subgames:
                my_pieces = 0
                opponent_pieces = 0
                for _point, piece in sg:
                    if piece == player:
                        my_pieces += 1
                    elif piece == opponent:
                        opponent_pieces += 1
                current_board_score += (my_pieces - opponent_pieces)

        if current_board_score > best_score:
            best_score = current_board_score
            best_moves = [move]
        elif current_board_score == best_score:
            best_moves.append(move)

    # If no moves improved the score (e.g., all scores negative or zero),
    # best_moves might be empty or contain non-optimal moves.
    # Fallback to choosing one randomly from the initial set if necessary.
    if not best_moves:
        return random.choice(legal_moves)

    return random.choice(best_moves)


# --- Strategy 3: Local Activity Focus ---
def strategy_local_activity(board: Board, player: piece_type) -> Optional[move]:
    """
    Chooses a move where the moving piece lands adjacent to the
    maximum number of opponent stones.
    """
    legal_moves = board.generate_moves(player == 'W')
    if not legal_moves:
        return None

    opponent = 'W' if player == 'B' else 'B'
    best_score = -1  # Minimum possible adjacency is 0
    best_moves = []

    for move in legal_moves:
        next_board = board.apply_move(move)
        landing_point = move.to_pos
        adjacent_opponents = 0

        # Check orthogonal neighbors of the landing spot on the *new* board
        for neighbor_pos in next_board.get_orthogonal_neighbours_positions(landing_point):
            if next_board.get_piece_at(neighbor_pos) == opponent:
                adjacent_opponents += 1

        current_score = adjacent_opponents

        if current_score > best_score:
            best_score = current_score
            best_moves = [move]
        elif current_score == best_score:
            best_moves.append(move)

    # If all moves result in 0 adjacent opponents, best_moves will contain all moves.
    if not best_moves:  # Should not happen if legal_moves exist
        return random.choice(legal_moves)

    # Tie-breaking: could choose randomly, or prefer moves in larger subgames (more complex)
    return random.choice(best_moves)

# --- Example Usage ---
# my_board = Board(...) # Initialize your board
# current_player = 'W'
#
# move1 = strategy_mobility(my_board, current_player)
# move2 = strategy_subgame_control(my_board, current_player)
# move3 = strategy_local_activity(my_board, current_player)
#
# print(f"Mobility Strategy suggests: {move1}")
# print(f"Subgame Control Strategy suggests: {move2}")
# print(f"Local Activity Strategy suggests: {move3}")
