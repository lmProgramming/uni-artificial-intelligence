from typing import Callable, cast

from clobber.types import piece_type, move


class Board:
    def __init__(self, n: int, m: int, state: list[str], turn: int = 0) -> None:
        # height
        self.n: int = n
        # width
        self.m: int = m
        self.state: list[str] = state
        self.turn: int = turn

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

    def copy(self) -> "Board":
        return Board(self.n, self.m, [row[:] for row in self.state], self.turn)

    def __str__(self) -> str:
        result = []
        for y in range(self.n):
            result.append(self.state[y])

        return "\n".join(result)

    def pretty(self) -> str:
        result: list[str] = ["  " + " ".join(map(str, range(self.m)))]
        for y in range(self.n):
            result.append(str(y) + " " + str(self.state[y]))

        return "\n".join(result)

    def get_neighbours_positions(self, position: tuple[int, int]) -> list[tuple[int, int]]:
        return self.get_neighbours_positions_filtered(position, lambda piece_type: piece_type in ["B", "W"])

    def get_neighbours_positions_filtered(self, position: tuple[int, int], piece_filter: Callable[[piece_type], bool]) -> list[tuple[int, int]]:
        x, y = position

        neighbours_positions: list[tuple[int, int]] = []

        positions: list[tuple[int, int]] = [
            (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for position in positions:
            piece: piece_type = self.get_piece_at(position)
            if not piece_filter(piece):
                continue

            neighbours_positions.append(position)

        return neighbours_positions

    def get_piece_at(self, position: tuple[int, int]) -> piece_type:
        x, y = position
        if x < 0 or y < 0 or y >= self.n or x >= self.m:
            return 'outside'
        piece: str = self.state[y][x * 2]
        return cast(piece_type, piece)

    def replace_piece_at(self, position: tuple[int, int], new_piece: piece_type) -> piece_type:
        x, y = position
        if x < 0 or y < 0 or y >= self.n or x >= self.m:
            return 'outside'
        str_index: int = x * 2
        self.state[y] = self.state[y][0:str_index] + \
            new_piece + self.state[y][str_index + 1:]
        return new_piece

    def make_move(self, new_color: piece_type, move: move) -> None:
        position_from, position_to = move
        if self.get_piece_at(position_from) != new_color:
            raise Exception("wrong")
        self.replace_piece_at(position_from, '_')
        if self.get_piece_at(position_to) != ("B" if new_color == 'W' else 'W'):
            raise Exception("wrong")
        self.replace_piece_at(position_to, new_color)
        self.turn += 1

    def move_assuming_correct(self, new_color: piece_type, move: move) -> None:
        position_from, position_to = move
        self.replace_piece_at(position_from, '_')
        self.replace_piece_at(position_to, new_color)
        self.turn += 1

    def get_all_pieces(self, piece: piece_type) -> list[tuple[int, int]]:
        positions: list[tuple[int, int]] = []
        for y in range(self.n):
            for x in range(self.m):
                if self.get_piece_at((x, y)) != piece:
                    continue

                positions.append((x, y))

        return positions

    def generate_moves(self, for_white: bool) -> dict[tuple[int, int], list[tuple[int, int]]]:
        opponent: piece_type = 'B' if for_white else 'W'
        current_piece: piece_type = 'W' if for_white else 'B'

        possible_moves: dict[tuple[int, int], list[tuple[int, int]]] = {}

        for y in range(self.n):
            for x in range(self.m):
                if self.get_piece_at((x, y)) != current_piece:
                    continue

                neighbouring_opponents: list[tuple[int, int]] = self.get_neighbours_positions_filtered(
                    (x, y), lambda piece_type: piece_type == opponent)

                if not neighbouring_opponents:
                    continue

                possible_moves[(x, y)] = neighbouring_opponents

        return possible_moves

    def has_moves(self, white: bool) -> bool:
        return len(self.generate_moves(white)) > 0
