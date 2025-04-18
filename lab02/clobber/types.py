from typing import Literal

piece_type = Literal['B'] | Literal['W'] | Literal['_'] | Literal['outside']
move = tuple[tuple[int, int], tuple[int, int]]
