from agent import *
from heuristics import *
from clobber.board import Board


def main() -> None:
    white: Agent = MiniMax('W', Dumb(), 1)
    black: Agent = MiniMax('B', Dumb(), 1)
    board: Board = Board.initialize_board(10, 10)

    current_color: piece_type = 'W'
    while True:
        current_player: Agent = white if current_color == 'W' else black
        move_from, move_to = current_player.generate_move(board)
        board.move_assuming_correct(current_color, move_from, move_to)
        print(f"{current_color} moved from {move_from} to {move_to}")
        print(board.pretty())

        if not board.has_moves(current_color != 'W'):
            print(board.pretty())
            print(current_color + " won this game!")
            return

        current_color = 'B' if current_color == 'W' else "W"


if __name__ == "__main__":
    main()
