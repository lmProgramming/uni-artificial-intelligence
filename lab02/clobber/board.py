class Board:
    def __init__(self, n: int, m: int, state: list[str]) -> None:
        self.n: int = n
        self.m: int = m
        self.state: list[str] = state

    @staticmethod
    def initialize_board(n: int, m: int) -> "Board":
        state: list[str] = []

        for y in range(n):
            line: list[str] = []
            white: bool = y % 2 == 0
            for _ in range(m):
                line.append("W" if white else "B")
                white = not white

            state.append("_".join(line))

        board = Board(n, m, state)
        return board

    def __str__(self) -> str:
        result = []
        for y in range(self.n):
            result.append(self.state[y])

        return "\n".join(result)
