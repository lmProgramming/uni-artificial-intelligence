from abc import ABC, abstractmethod
from dataclasses import dataclass

from clobber.board import Board
from heuristics import Heuristic


@dataclass(frozen=True)
class MinTurnRule():
    min_turn: int
    heuristic: Heuristic
    max_depth: int


class Strategy(ABC):
    @abstractmethod
    def get_heuristic(self, board: Board, turn: int) -> Heuristic:
        ...
