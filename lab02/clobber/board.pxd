cdef class Board:
    cdef public int n
    cdef public int m
    cdef public int turn
    cdef public list state

    cpdef get_piece_at(self, tuple position)
    cpdef replace_piece_at(self, tuple position, object new_piece)
    cpdef list get_neighbours_positions_filtered(self, tuple position, object piece_filter)
    cpdef list get_all_pieces(self, object piece)
    cpdef bint has_moves(self, bint white)