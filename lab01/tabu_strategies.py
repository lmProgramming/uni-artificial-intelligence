from random import randint
from abc import ABC, abstractmethod


class TabuSizeStrategy(ABC):
    @abstractmethod
    def get_tabu_size(self, required_stops: list[str]) -> int:
        pass


class FixedTabuSizeStrategy(TabuSizeStrategy):
    def __init__(self, size: int = 10) -> None:
        self.size: int = size

    def get_tabu_size(self, required_stops: list[str]) -> int:
        return self.size


class DynamicTabuSizeStrategy(TabuSizeStrategy):
    def __init__(self, k: float = 5.0, min_size: int = 10) -> None:
        self.k: float = k
        self.min_size: int = min_size

    def get_tabu_size(self, required_stops: list[str]) -> int:
        return max(self.min_size, int(self.k * len(required_stops)))


class NeighborhoodSamplingStrategy(ABC):
    @abstractmethod
    def generate_swaps(self, num_stops: int) -> list[tuple[int, int]]:
        pass


class FullSamplingStrategy(NeighborhoodSamplingStrategy):
    def generate_swaps(self, num_stops: int) -> list[tuple[int, int]]:
        swaps: list[tuple[int, int]] = []
        for i in range(1, num_stops):
            for j in range(i+1, num_stops+1):
                swaps.append((i, j))
        return swaps


class RandomSamplingStrategy(NeighborhoodSamplingStrategy):
    def __init__(self, sample_size: int = 10) -> None:
        self.sample_size: int = sample_size

    def generate_swaps(self, num_stops: int) -> list[tuple[int, int]]:
        swaps: set[tuple[int, int]] = set()
        while len(swaps) < min(self.sample_size, (num_stops * (num_stops - 1)) // 2):
            i: int = randint(1, num_stops - 1)
            j: int = randint(i+1, num_stops)
            swaps.add((i, j))
        return list(swaps)
