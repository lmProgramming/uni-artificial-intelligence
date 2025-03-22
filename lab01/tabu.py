from dataclasses import dataclass
from random import sample
from itertools import permutations
from utils import time_to_seconds
from datetime import datetime, time
import time as t
from models import Node, Path, CommunicationStep, NoPathFoundError, Graph
from path_utils import generate_path
from dijkstra import dijkstra  # zakładam, że możesz wywołać swój własny algorytm

@dataclass
class TabuSolution:
    route: list[str]
    cost: int
    steps: list[CommunicationStep]

def build_cost_matrix(stops: list[str], start_time: time, graph: Graph):
    """Precompute shortest paths and costs between all pairs using Dijkstra."""
    cost_matrix = {}
    path_matrix = {}

    for i, start in enumerate(stops):
        for j, end in enumerate(stops):
            if start == end:
                continue
            path: Path = dijkstra(start, end, start_time, graph)
            cost_matrix[(start, end)] = path.cost
            path_matrix[(start, end)] = path.steps
            start_time = path.steps[-1].end_time

    return cost_matrix, path_matrix

def calculate_total_cost(route: list[str], cost_matrix: dict):
    total_cost = 0
    for i in range(len(route) - 1):
        start = route[i]
        end = route[i+1]
        total_cost += cost_matrix.get((start, end), float('inf'))
    return total_cost

def assemble_steps(route: list[str], path_matrix: dict):
    steps = []
    for i in range(len(route) - 1):
        start = route[i]
        end = route[i+1]
        steps += path_matrix.get((start, end), [])
    return steps

def tabu_search(start: str, required_stops: list[str], start_time: time, graph: Graph, max_iterations=100, tabu_size=10):
    stops: list[str] = [start] + required_stops + [start]
    cost_matrix, path_matrix = build_cost_matrix(stops, start_time, graph)

    # Initial random solution
    middle: list[str] = sample(required_stops, len(required_stops))
    current_route: list[str] = [start] + middle + [start]
    best_route: list[str] = current_route.copy()

    best_cost = calculate_total_cost(best_route, cost_matrix)
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
                    cost = calculate_total_cost(new_route, cost_matrix)
                    if cost < float('inf'):  # skip impossible paths
                        neighborhood.append(TabuSolution(new_route, cost, []))

        if not neighborhood:
            break  # No valid neighbors found

        neighborhood.sort(key=lambda x: x.cost)
        best_neighbor = neighborhood[0]

        if best_neighbor.cost < best_cost:
            best_cost = best_neighbor.cost
            best_route = best_neighbor.route

        current_route = best_neighbor.route
        tabu_list.append(current_route)
        if len(tabu_list) > tabu_size:
            tabu_list.pop(0)

    elapsed: float = t.perf_counter() - start_time_perf
    final_steps = assemble_steps(best_route, path_matrix)
    
    print(start)
    print(final_steps)

    return Path(final_steps, best_cost, elapsed)
