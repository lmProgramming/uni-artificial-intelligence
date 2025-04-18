from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import time

from clobber.board import Board
from clobber.types import piece_type, move
from heuristics import Heuristic


class Agent(ABC):
    def __init__(self, color: piece_type) -> None:
        self.color: piece_type = color
        self.opponent_color: piece_type = "B" if color == "W" else "W"
        self.total_time: float = 0
        self._total_nodes: float = 0

    @staticmethod
    def add_total_time(func):
        def wrapper(self, *args, **kwargs):
            start = time.time()
            result = func(self, *args, **kwargs)
            end = time.time()
            self.total_time += end - start
            return result
        return wrapper

    @abstractmethod
    @add_total_time
    def generate_move(self, board: Board) -> move:
        ...

    @property
    def get_total_nodes(self):
        return self._total_nodes


class Human(Agent):
    def generate_move(self, board: Board) -> move:
        print(board.pretty())
        print(f"your move, {self.color}")
        while True:
            try:
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

                if (x2, y2) not in board.get_neighbours_positions_filtered((x, y), lambda p: p == self.opponent_color):
                    print(
                        f"illegal move! {x2},{y2} not in {x},{y} {self.opponent_color} neighbours")
                    continue

                return ((x, y), (x2, y2))
            except Exception as e:
                print("invalid move! exception handled: ")
                print(e)


class MiniMax(Agent):
    def __init__(self, color: piece_type, heuristic: Heuristic, max_depth: int = 10) -> None:
        super().__init__(color)

        self.heuristic: Heuristic = heuristic
        self.max_depth: int = max_depth

    def minimax(self, board: Board, depth, is_maximizing) -> float:
        self._total_nodes += 1

        if depth >= self.max_depth:
            return self.heuristic.calculate(board, is_maximizing)

        if is_maximizing:
            best_score: float = float("-inf")
            for position_from, moves in board.generate_moves(True).items():
                for position_to in moves:
                    new_board: Board = board.copy()
                    new_board.move_assuming_correct(
                        'W', (position_from, position_to))

                    score: float = self.minimax(new_board, depth + 1, False)
                    best_score = max(score, best_score)
            return best_score

        best_score = float("inf")
        for position_from, moves in board.generate_moves(False).items():
            for position_to in moves:
                new_board = board.copy()
                new_board.move_assuming_correct(
                    'B', (position_from, position_to))

                score = self.minimax(new_board, depth + 1, True)
                best_score = min(score, best_score)

        return best_score

    @Agent.add_total_time
    def generate_move(self, board: Board) -> move:
        if self.color == 'W':
            best_score: float = float("-inf")
            best_move: move
            for position_from, moves in board.generate_moves(True).items():
                for position_to in moves:
                    new_board: Board = board.copy()
                    new_board.move_assuming_correct(
                        'W', (position_from, position_to))

                    score: float = self.minimax(new_board, 0, False)
                    if score >= best_score:
                        best_score = score
                        best_move = (
                            position_from, position_to)
            return best_move

        best_score = float("inf")
        for position_from, moves in board.generate_moves(False).items():
            for position_to in moves:
                new_board = board.copy()
                new_board.move_assuming_correct(
                    'B', (position_from, position_to))

                score = self.minimax(new_board, 0, True)
                if score <= best_score:
                    best_score = score
                    best_move = (
                        position_from, position_to)

        return best_move


class AlphaBeta(Agent):
    def __init__(self, color: piece_type, heuristic: Heuristic, max_depth: int = 10) -> None:
        super().__init__(color)

        self.heuristic: Heuristic = heuristic
        self.max_depth: int = max_depth

    def minimax(self, board: Board, depth, is_maximizing: bool, alpha: float, beta: float) -> float:
        self._total_nodes += 1

        if depth >= self.max_depth:
            return self.heuristic.calculate(board, is_maximizing)

        if is_maximizing:
            best_score: float = float("-inf")
            for position_from, moves in board.generate_moves(True).items():
                for position_to in moves:
                    new_board: Board = board.copy()
                    new_board.move_assuming_correct(
                        'W', (position_from, position_to))

                    score: float = self.minimax(
                        new_board, depth + 1, False, alpha, beta)
                    best_score = max(score, best_score)
                    alpha = max(alpha, best_score)

                    if beta <= alpha:
                        return best_score

            return best_score

        best_score = float("inf")
        for position_from, moves in board.generate_moves(False).items():
            for position_to in moves:
                new_board = board.copy()
                new_board.move_assuming_correct(
                    'B', (position_from, position_to))

                score = self.minimax(new_board, depth + 1, True, alpha, beta)
                best_score = min(score, best_score)
                beta = min(beta, best_score)

                if beta <= alpha:
                    return best_score

        return best_score

    @Agent.add_total_time
    def generate_move(self, board: Board) -> move:
        if self.color == 'W':
            best_score: float = float("-inf")
            best_move: move
            for position_from, moves in board.generate_moves(True).items():
                for position_to in moves:
                    new_board: Board = board.copy()
                    new_board.move_assuming_correct(
                        'W', (position_from, position_to))

                    score: float = self.minimax(
                        new_board, 0, False, float("-inf"), float("inf"))
                    if score >= best_score:
                        best_score = score
                        best_move = (
                            position_from, position_to)
            logging.debug(f"white heuristic: {best_score}")
            return best_move

        best_score = float("inf")
        for position_from, moves in board.generate_moves(False).items():
            for position_to in moves:
                new_board = board.copy()
                new_board.move_assuming_correct(
                    'B', (position_from, position_to))

                score = self.minimax(new_board, 0, True,
                                     float("-inf"), float("inf"))
                if score <= best_score:
                    best_score = score
                    best_move = (
                        position_from, position_to)

        logging.debug(f"black heuristic: {best_score}")
        return best_move


@dataclass(frozen=True)
class MinTurnRule():
    min_turn: int
    heuristic: Heuristic
    max_depth: int


class Dynamic(Agent):
    def __init__(self, color: piece_type, rules: list[MinTurnRule]) -> None:
        super().__init__(color)

        self.rules: list[MinTurnRule] = rules
        self.agent = AlphaBeta(color, rules[0].heuristic, rules[0].max_depth)

    @Agent.add_total_time
    def generate_move(self, board) -> move:
        current_turn: int = board.turn
        index = 0
        for rule in self.rules[1:]:
            if rule.min_turn > current_turn:
                break
            index += 1

        self.agent.heuristic = self.rules[index].heuristic
        self.agent.max_depth = self.rules[index].max_depth

        return self.agent.generate_move(board)

    @property
    def get_total_nodes(self) -> float:
        return self.agent.get_total_nodes()
