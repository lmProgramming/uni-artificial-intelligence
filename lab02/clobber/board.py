from .piece_type import piece_type
from typing import cast


class Board:
    def __init__(self, n: int, m: int, state: list[str]) -> None:
        # height
        self.n: int = n
        # width
        self.m: int = m
        self.state: list[str] = state

    @staticmethod
    def initialize_board(n: int, m: int) -> "Board":
        state: list[str] = []

        for y in range(n):
            line: list[str] = []
            white: bool = y % 2 == 0
            for _ in range(m):
                line.append("W" if white else "B")
                white = not white

            state.append("_".join(line))

        board = Board(n, m, state)
        return board

    def __str__(self) -> str:
        result = []
        for y in range(self.n):
            result.append(self.state[y])

        return "\n".join(result)

    def get_neighbours_positions_filtered(self, position: tuple[int, int], piece_filter: piece_type) -> list[tuple[int, int]]:
        x, y = position

        neighbours_positions: list[tuple[int, int]] = []

        positions: list[tuple[int, int]] = [
            (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for position in positions:
            piece: piece_type = self.get_piece_at(position)
            if piece != piece_filter:
                continue

            neighbours_positions.append(position)

        return neighbours_positions

    def get_piece_at(self, position: tuple[int, int]) -> piece_type:
        x, y = position
        if x < 0 or y < 0 or y >= self.n or x >= self.m:
            return 'outside'
        piece: str = self.state[y][x * 2]
        return cast(piece_type, piece)

    def generate_moves(self, for_white: bool) -> dict[tuple[int, int], list[tuple[int, int]]]:
        opponent: piece_type = 'B' if for_white else 'W'
        current_piece: piece_type = 'W' if for_white else 'B'

        possible_moves = {}

        for y in range(self.n):
            for x in range(self.m):
                if self.get_piece_at((x, y)) != current_piece:
                    continue

                neighbouring_opponents: list[tuple[int, int]] = self.get_neighbours_positions_filtered(
                    (x, y), opponent)

                if not neighbouring_opponents:
                    continue

                possible_moves[(x, y)] = neighbouring_opponents

        return possible_moves
