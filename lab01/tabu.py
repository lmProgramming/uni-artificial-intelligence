from dataclasses import dataclass
from random import sample
from utils import time_to_seconds
from datetime import datetime, time, timedelta
import time as t
from models import Path, CommunicationStep, Graph, LineStep
from dijkstra import dijkstra
from functools import lru_cache

@lru_cache(maxsize=None)
def get_shortest_path(start: str, end: str, start_time_sec: int, graph: Graph) -> Path:
    """Wrapper na Dijkstrę z cache'owaniem."""
    start_time_obj: time = (datetime.min + timedelta(seconds=start_time_sec)).time()
    path: Path = dijkstra(start, end, start_time_obj, graph)
    return path

@dataclass
class TabuSolution:
    route: list[str]
    cost: int
    steps: list[CommunicationStep]

def calculate_total_cost_and_steps(route: list[str], start_time: time, graph: Graph):
    total_cost: float = 0
    steps = []
    current_time = start_time

    for i in range(len(route) - 1):
        start: str = route[i]
        end: str = route[i+1]

        # Wywołujemy Dijkstra z aktualnym czasem
        path: Path = dijkstra(start, end, current_time, graph)
        total_cost += path.cost
        steps += path.steps

        # Aktualizujemy czas na koniec tej trasy
        current_time: time = path.steps[-1].end_time if path.steps else current_time

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


def tabu_search(start: str, required_stops: list[str], start_time: time, graph: Graph, max_iterations=100, tabu_size=10) -> Path:
    middle: list[str] = sample(required_stops, len(required_stops))
    current_route: list[str] = [start] + middle + [start]
    best_route: list[str] = current_route.copy()

    best_cost, best_steps = calculate_total_cost_and_steps(best_route, start_time, graph)
    tabu_list = []

    start_time_perf: float = t.perf_counter()

    for iteration in range(max_iterations):
        neighborhood = []
        
        # Generate neighborhood by swapping two stops in the middle
        for i in range(1, len(required_stops)):
            for j in range(i+1, len(required_stops)+1):
                new_route = current_route.copy()
                new_route[i], new_route[j] = new_route[j], new_route[i]
                if new_route not in tabu_list:
                    cost, steps = calculate_total_cost_and_steps(new_route, start_time, graph)
                    if cost < float('inf'):  # skip impossible paths
                        neighborhood.append(TabuSolution(new_route, cost, steps))

        if not neighborhood:
            break  # No valid neighbors found

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
