from abc import ABC, abstractmethod
from clobber.board import Board


class Heuristic(ABC):
    @abstractmethod
    def calculate(self, board: Board) -> float:
        ...


class Dumb(Heuristic):
    def calculate(self, board) -> float:
        return 0
