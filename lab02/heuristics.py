from _collections_abc import dict_items
from abc import ABC, abstractmethod
from clobber.board import Board
import random


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
