from dataclasses import dataclass
from random import sample
from utils import time_to_seconds
from datetime import datetime, time, timedelta
import time as t
from models import OptimizationCriterion, Path, CommunicationStep, Graph, LineStep
from a_star import a_star_search
from functools import lru_cache
from typing import Optional
from abc import ABC, abstractmethod


class TabuSizeStrategy(ABC):
    @abstractmethod
    def get_tabu_size(self, required_stops: list[str]) -> int:
        pass


class FixedTabuSizeStrategy(TabuSizeStrategy):
    def __init__(self, size: int = 10):
        self.size = size

    def get_tabu_size(self, required_stops: list[str]) -> int:
        return self.size


class DynamicTabuSizeStrategy(TabuSizeStrategy):
    def __init__(self, k: float = 1.0, min_size: int = 10):
        self.k = k
        self.min_size = min_size

    def get_tabu_size(self, required_stops: list[str]) -> int:
        return max(self.min_size, int(self.k * len(required_stops)))


@lru_cache(maxsize=None)
def get_shortest_path(start: str, end: str, start_time_sec: int, graph: Graph) -> Path:
    """Wrapper na Dijkstrę z cache'owaniem."""
    start_time_obj: time = (
        datetime.min + timedelta(seconds=start_time_sec)).time()
    path: Path = (start, end, start_time_obj, graph)
    return path


@dataclass
class TabuSolution:
    route: list[str]
    cost: int
    steps: list[CommunicationStep]


def calculate_total_cost_and_steps(route: list[str], start_time: time, graph: Graph, optimization_criterion: OptimizationCriterion):
    total_cost: float = 0
    steps = []
    current_time: time = start_time

    for i in range(len(route) - 1):
        start: str = route[i]
        end: str = route[i+1]

        path: Path = a_star_search(
            start, end, current_time, graph, optimization_criterion)
        total_cost += path.cost
        steps += path.steps

        current_time = path.steps[-1].end_time if path.steps else current_time

    return total_cost, steps


def assemble_steps(route: list[str], start_time: time, graph: Graph) -> list[LineStep]:
    steps: list[LineStep] = []
    current_time_sec: int = time_to_seconds(start_time)
    for i in range(len(route) - 1):
        start: str = route[i]
        end: str = route[i+1]
        path: Path = get_shortest_path(start, end, current_time_sec, graph)
        steps += path.steps
        last_step_end_time_sec = time_to_seconds(path.steps[-1].end_time)
        if last_step_end_time_sec < current_time_sec:
            last_step_end_time_sec += 86400
        current_time_sec = last_step_end_time_sec
    return steps


def tabu_search(start: str, required_stops: list[str], start_time: time, graph: Graph,
                optimization_criterion: OptimizationCriterion, max_iterations=100,
                tabu_size_strategy: TabuSizeStrategy = FixedTabuSizeStrategy()) -> Path:

    middle: list[str] = sample(required_stops, len(required_stops))
    current_route: list[str] = [start] + middle + [start]
    best_route: list[str] = current_route.copy()

    best_cost, best_steps = calculate_total_cost_and_steps(
        best_route, start_time, graph, optimization_criterion)
    tabu_size = tabu_size_strategy.get_tabu_size(required_stops)
    tabu_list = []

    start_time_perf: float = t.perf_counter()

    for iteration in range(max_iterations):
        neighborhood = []

        # Neighborhood generation...
        for i in range(1, len(required_stops)):
            for j in range(i+1, len(required_stops)+1):
                new_route = current_route.copy()
                new_route[i], new_route[j] = new_route[j], new_route[i]
                if new_route not in tabu_list:
                    cost, steps = calculate_total_cost_and_steps(
                        new_route, start_time, graph, optimization_criterion)
                    if cost < float('inf'):
                        neighborhood.append(
                            TabuSolution(new_route, cost, steps))

        if not neighborhood:
            break

        neighborhood.sort(key=lambda x: x.cost)
        best_neighbor = neighborhood[0]

        if best_neighbor.cost < best_cost:
            best_cost = best_neighbor.cost
            best_route = best_neighbor.route
            best_steps = best_neighbor.steps

        current_route = best_neighbor.route
        tabu_list.append(current_route)
        if len(tabu_list) > tabu_size:
            tabu_list.pop(0)

    elapsed: float = t.perf_counter() - start_time_perf

    return Path(best_steps, best_cost, elapsed)
