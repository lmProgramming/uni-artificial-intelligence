from random import randint
from collections import deque
from dataclasses import dataclass, field
from random import sample
from utils import time_to_seconds
from datetime import datetime, time, timedelta
import time as t
from models import OptimizationCriterion, Path, CommunicationStep, Graph, LineStep
from a_star import a_star_search
from functools import lru_cache
from tabu_strategies import FixedTabuSizeStrategy, TabuSizeStrategy, FullSamplingStrategy, NeighborhoodSamplingStrategy
import heapq
from collections import deque


@lru_cache(maxsize=None)
def get_shortest_path(start: str, end: str, start_time_sec: int, graph: Graph, optimization_criterion: OptimizationCriterion) -> Path:
    start_time_obj: time = (
        datetime.min + timedelta(seconds=start_time_sec)).time()
    path: Path = a_star_search(
        start, end, start_time_obj, graph, optimization_criterion)
    return path


@dataclass(order=True)
class TabuSolution:
    cost: int
    route: list[str] = field(compare=False)
    steps: list[CommunicationStep] = field(compare=False)


def post_clear_cache(func):
    def wrapper(*args, **kwargs) -> None:
        result = func(*args, **kwargs)
        get_shortest_path.cache_clear()
        return result
    return wrapper


def calculate_total_cost_and_steps(route: list[str], start_time: time, graph: Graph, optimization_criterion: OptimizationCriterion):
    total_cost: float = 0
    steps = []
    current_time: time = start_time

    for i in range(len(route) - 1):
        start: str = route[i]
        end: str = route[i+1]

        start_time_sec: int = time_to_seconds(current_time)
        path: Path = get_shortest_path(
            start, end, start_time_sec, graph, optimization_criterion)
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


@post_clear_cache
def tabu_search(start: str, required_stops: list[str], start_time: time, graph: Graph,
                optimization_criterion: OptimizationCriterion, max_iterations=10,
                tabu_size_strategy: TabuSizeStrategy = FixedTabuSizeStrategy(),
                sampling_strategy: NeighborhoodSamplingStrategy = FullSamplingStrategy()
                ) -> Path:

    middle: list[str] = sample(required_stops, len(required_stops))
    current_route: list[str] = [start] + middle + [start]
    best_route: list[str] = current_route.copy()

    best_cost, best_steps = calculate_total_cost_and_steps(
        best_route, start_time, graph, optimization_criterion)

    tabu_size: int = tabu_size_strategy.get_tabu_size(required_stops)

    tabu_set: set[tuple] = set()
    tabu_queue: deque[tuple] = deque()

    start_time_perf: float = t.perf_counter()

    for _ in range(max_iterations):
        neighborhood: list[TabuSolution] = []
        swaps: list[tuple[int, int]] = sampling_strategy.generate_swaps(
            len(required_stops))

        for i, j in swaps:
            new_route: list[str] = current_route.copy()
            new_route[i], new_route[j] = new_route[j], new_route[i]
            route_tuple = tuple(new_route)

            cost, steps = calculate_total_cost_and_steps(
                new_route, start_time, graph, optimization_criterion)

            if (route_tuple not in tabu_set) or (cost < best_cost):
                if cost < float('inf'):
                    heapq.heappush(neighborhood, TabuSolution(
                        cost, new_route, steps))

        if not neighborhood:
            break

        best_neighbor: TabuSolution = heapq.heappop(neighborhood)

        if best_neighbor.cost < best_cost:
            best_cost = best_neighbor.cost
            best_route = best_neighbor.route
            best_steps = best_neighbor.steps

        current_route = best_neighbor.route
        route_tuple = tuple(current_route)
        tabu_set.add(route_tuple)
        tabu_queue.append(route_tuple)

        if len(tabu_queue) > tabu_size:
            oldest = tabu_queue.popleft()
            tabu_set.remove(oldest)

    elapsed: float = t.perf_counter() - start_time_perf

    return Path(best_steps, best_cost, elapsed)
