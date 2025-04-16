from agent import *
from clobber.board import Board


def main() -> None:
    white: Agent = Human('W')
    black: Agent = Human('B')
    board: Board = Board.initialize_board(5, 6)

    current_color: piece_type = 'B'
    while True:
        current_player: Agent = white if current_color == 'W' else black
        move_from, move_to = current_player.generate_move(board)
        current_color = 'B' if current_color == 'W' else "W"


if __name__ == "__main__":
    main()
