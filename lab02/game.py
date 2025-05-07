import sys
from agent import *
from heuristics import *
from clobber.board import Board
from clobber.types import move


LOG_STEPS = True


def game(white: Agent, black: Agent, board: Board) -> piece_type:
    print("board initialized")
    print(board.pretty())

    current_color: piece_type = 'B'
    while True:
        current_player: Agent = white if current_color == 'W' else black
        chosen_move: move = current_player.generate_move(board)
        board.move_assuming_correct(current_color, chosen_move)
        if LOG_STEPS:
            print(
                f"{board.turn}. {current_color} moved from {chosen_move[0]} to {chosen_move[1]}")
            print(board.pretty())

        if not board.has_moves(current_color != 'W'):
            print()
            print(board.pretty())
            print(f"{board.turn} turns taken")
            print(f"{current_color} won this game!")
            print(
                f"white: {white.total_nodes} nodes visited, {white.total_time} spent", file=sys.stderr,
                flush=True)
            print(
                f"black: {black.total_nodes} nodes visited, {black.total_time} spent", file=sys.stderr,
                flush=True)
            return current_color

        current_color = 'B' if current_color == 'W' else "W"


def main() -> None:
    rules: list[MinTurnRule] = [MinTurnRule(0, Random(), 1), MinTurnRule(
        10, SubgameControlHeuristic(), 10), MinTurnRule(20, LocalActivityHeuristic(), 10)]
    rules2: list[MinTurnRule] = [MinTurnRule(0, Random(), 1), MinTurnRule(
        3, SubgameControlHeuristic(), 5), MinTurnRule(10, LocalActivityHeuristic(), 15)]
    white: Agent = Dynamic('W', rules)
    black: Agent = Dynamic('B', rules2)
    board: Board = Board.initialize_board(5, 6)

    game(white, black, board)


if __name__ == "__main__":
    main()
