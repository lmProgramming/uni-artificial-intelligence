from clobber.board import Board
from clobber.types import piece_type


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
