from agent import *
from heuristics import *
from clobber.board import Board
from clobber.types import move


def main() -> None:
    rules: list[MinTurnRule] = [MinTurnRule(0, Random(), 1), MinTurnRule(
        10, SubgameControlHeuristic(), 10), MinTurnRule(20, LocalActivityHeuristic(), 10)]
    white: Agent = Dynamic('W', rules)
    black: Agent = AlphaBeta('B', SubgameControlHeuristic(), 3)
    board: Board = Board.initialize_board(5, 6)

    print("board initialized")
    print(board.pretty())

    current_color: piece_type = 'W'
    while True:
        current_player: Agent = white if current_color == 'W' else black
        chosen_move: move = current_player.generate_move(board)
        board.move_assuming_correct(current_color, chosen_move)
        print(
            f"{current_color} moved from {chosen_move[0]} to {chosen_move[1]}")
        print(board.pretty())

        if not board.has_moves(current_color != 'W'):
            print(current_color + " won this game!")
            return

        current_color = 'B' if current_color == 'W' else "W"


if __name__ == "__main__":
    main()
