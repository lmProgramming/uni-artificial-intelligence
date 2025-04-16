from abc import ABC, abstractmethod
from clobber.board import Board
from clobber.piece_type import piece_type


class Agent(ABC):
    @abstractmethod
    def generate_move(self, board: Board) -> tuple[tuple[int, int], tuple[int, int]]:
        ...


class Human(Agent):
    def __init__(self, color: piece_type) -> None:
        self.color: piece_type = color
        self.opponent_color: piece_type = "B" if color == "W" else "W"

    def generate_move(self, board: Board) -> tuple[tuple[int, int], tuple[int, int]]:
        print(board)
        while True:
            x = int(input("piece start position x: "))
            y = int(input("piece start position y: "))

            if board.get_piece_at((x, y)) == 'outside':
                print("outside board!")
                continue

            if board.get_piece_at((x, y)) != self.color:
                print("not your piece!")
                continue

            x2 = int(input("piece end position x: "))
            y2 = int(input("piece end position y: "))

            print(self.color)
            print(self.opponent_color)
            print(board.get_neighbours_positions_filtered(
                (x, y), self.opponent_color))
            if (x2, y2) not in board.get_neighbours_positions_filtered((x, y), self.opponent_color):
                print("illegal move!")
                continue

            return ((x, y), (x2, y2))
