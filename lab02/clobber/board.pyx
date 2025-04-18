from typing import Callable

from clobber.types cimport move

cdef class Board:

    def __init__(self, int n, int m, list state, int turn=0):
        self.n = n
        self.m = m
        self.state = list(state)
        self.turn = turn

    @staticmethod
    def initialize_board(int n, int m):
        state_py = []
        cdef int y
        cdef bint white_py

        for y in range(n):
            line_py = []
            white_py = (y % 2 == 0)
            for _ in range(m):
                line_py.append("W" if white_py else "B")
                white_py = not white_py
            state_py.append(" ".join(line_py))

        board = Board(n, m, state_py)
        return board

    def copy(self):
        return Board(self.n, self.m, [row for row in self.state], self.turn)

    def __str__(self):
        return "\n".join(self.state)

    def pretty(self):
        result_py = ["  " + " ".join(map(str, range(self.m)))]
        cdef int y
        for y in range(self.n):
            result_py.append(str(y) + " " + str(self.state[y]))
        return "\n".join(result_py)

    cpdef get_piece_at(self, tuple position):
        cdef int x, y
        x, y = position

        if x < 0 or y < 0 or y >= self.n or x >= self.m:
            return 'outside'

        row_str = <str>self.state[y]
        pieces = row_str.split(' ')
        return pieces[x]


    cpdef replace_piece_at(self, tuple position, object new_piece):
        cdef int x, y
        x, y = position

        if x < 0 or y < 0 or y >= self.n or x >= self.m:
            return 'outside'

        row_str = <str>self.state[y]
        pieces = row_str.split(' ')
        if x < len(pieces):
            pieces[x] = <str>new_piece
            self.state[y] = " ".join(pieces)
            return new_piece
        else:
            return 'error_index'

    def get_neighbours_positions(self, tuple position):
        return self.get_neighbours_positions_filtered(position, lambda p: p in ["B", "W"])

    cpdef list get_neighbours_positions_filtered(self, tuple position, object piece_filter):
        cdef int x, y
        cdef list neighbours_positions_py = []
        cdef tuple check_pos
        cdef object piece

        x, y = position

        positions_to_check = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        for check_pos in positions_to_check:
            piece = self.get_piece_at(check_pos)
            if piece_filter(piece):
                neighbours_positions_py.append(check_pos)

        return neighbours_positions_py

    def make_move(self, object new_color, move m):
        cdef tuple position_from, position_to
        position_from, position_to = m
        if self.get_piece_at(position_from) != new_color:
            raise Exception("make_move check failed: piece is not player's color")
        opponent_color = <object>("B" if new_color == 'W' else 'W')
        if self.get_piece_at(position_to) != opponent_color:
             raise Exception("make_move check failed: target is not opponent")

        self.replace_piece_at(position_from, '_')
        self.replace_piece_at(position_to, new_color)
        self.turn += 1

    def move_assuming_correct(self, object new_color, move m):
        cdef tuple position_from, position_to
        position_from, position_to = m
        self.replace_piece_at(position_from, '_')
        self.replace_piece_at(position_to, new_color)
        self.turn += 1

    cpdef list get_all_pieces(self, object piece):
        cdef list positions_py = []
        cdef int x, y
        for y in range(self.n):
            for x in range(self.m):
                if self.get_piece_at((x, y)) == piece:
                    positions_py.append((x, y))
        return positions_py

    def generate_moves(self, bint for_white):
        cdef dict possible_moves_py = {}
        cdef object opponent, current_piece
        cdef int x, y
        cdef list neighbouring_opponents_py

        opponent = <object>('B' if for_white else 'W')
        current_piece = <object>('W' if for_white else 'B')

        for y in range(self.n):
            for x in range(self.m):
                if self.get_piece_at((x, y)) != current_piece:
                    continue

                def opponent_filter(p):
                    return p == opponent

                neighbouring_opponents_py = self.get_neighbours_positions_filtered(
                    (x, y), opponent_filter)

                if not neighbouring_opponents_py:
                    continue

                possible_moves_py[(x, y)] = neighbouring_opponents_py

        return possible_moves_py

    cpdef bint has_moves(self, bint white):
        return len(self.generate_moves(white)) > 0