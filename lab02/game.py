from agent import *
from clobber.board import Board


def main() -> None:
    white: Agent = Human('W')
    black: Agent = Human('B')
    board: Board = Board.initialize_board(2, 2)

    current_color: piece_type = 'W'
    while True:
        current_player: Agent = white if current_color == 'W' else black
        move_from, move_to = current_player.generate_move(board)
        board.move_assuming_correct(current_color, move_from, move_to)

        if not board.has_moves(current_color != 'W'):
            print(board.pretty())
            print(current_color + " won this game!")
            return

        current_color = 'B' if current_color == 'W' else "W"


if __name__ == "__main__":
    main()
