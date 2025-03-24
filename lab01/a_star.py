from dataclasses import dataclass, field
from models import Node, Path, Graph, CommunicationStep, NoPathFoundError, OptimizationCriterion
from path_utils import distance_heuristic, transfer_heuristic, generate_path, post_clear_cache
from utils import time_to_seconds
from datetime import time
import heapq
from itertools import count
import time as t


@dataclass(order=True)
class QueueEntry:
    priority: float
    counter: int
    current_stop_name: str = field(compare=False)
    path_taken: list[CommunicationStep] = field(compare=False)
    current_time_sec: int = field(compare=False)
    transfer_count: int = field(compare=False)


def should_skip(entry: QueueEntry, best_state: dict[str, tuple[int, int]]) -> bool:
    current_state: tuple[int, int] | None = best_state.get(
        entry.current_stop_name)
    if current_state is None:
        return False
    best_transfers, best_arrival = current_state
    return (entry.transfer_count > best_transfers) or \
           (entry.transfer_count ==
            best_transfers and entry.current_time_sec >= best_arrival)


def update_best_state(entry: QueueEntry, best_state: dict[str, tuple[int, int]]) -> None:
    best_state[entry.current_stop_name] = (
        entry.transfer_count, entry.current_time_sec)


def calculate_priority(entry: QueueEntry, current_node: Node, neighbor_node: Node, step: CommunicationStep,
                       travel_time: int, optimization_criterion: OptimizationCriterion) -> tuple[float, int]:
    cost_so_far: float = entry.priority + travel_time
    estimated_remaining: float = 0
    new_transfer_count: int = entry.transfer_count

    if optimization_criterion == OptimizationCriterion.TIME:
        cost_so_far -= distance_heuristic(current_node, neighbor_node)
        estimated_remaining = distance_heuristic(neighbor_node, neighbor_node)

    if optimization_criterion == OptimizationCriterion.TRANSFERS:
        cost_so_far += transfer_heuristic(entry.transfer_count)
        if entry.path_taken:
            previous_step: CommunicationStep = entry.path_taken[-1]
            is_transfer: bool = previous_step.line != step.line
            new_transfer_count += 1 if is_transfer else 0

    total_priority: float = cost_so_far + estimated_remaining
    return total_priority, new_transfer_count


@post_clear_cache
def a_star_search(start: str, end: str, start_time: time, graph: Graph, optimization_criterion: OptimizationCriterion) -> Path:
    if start not in graph.nodes or end not in graph.nodes:
        raise ValueError("Start or end stop does not exist in the graph.")

    start_node: Node = graph.nodes[start]
    end_node: Node = graph.nodes[end]
    start_time_sec: int = time_to_seconds(start_time)

    queue: list[QueueEntry] = []
    counter = count()
    initial_heuristic: float = distance_heuristic(
        start_node, end_node) if optimization_criterion == OptimizationCriterion.TIME else 0

    heapq.heappush(queue, QueueEntry(initial_heuristic, next(
        counter), start_node.name, [], start_time_sec, 0))
    best_state: dict[str, tuple[int, int]] = {}
    start_time_perf: float = t.perf_counter()

    while queue:
        entry: QueueEntry = heapq.heappop(queue)
        if should_skip(entry, best_state):
            continue
        update_best_state(entry, best_state)
        if entry.current_stop_name == end_node.name:
            elapsed: float = t.perf_counter() - start_time_perf
            return generate_path(start, entry.path_taken, elapsed, entry.priority)

        current_node: Node = graph.nodes[entry.current_stop_name]
        for (start_name, end_name), steps in graph.edges.items():
            if start_name != entry.current_stop_name:
                continue
            for step in steps:
                departure_seconds: int = time_to_seconds(step.departure_time)
                arrival_seconds: int = time_to_seconds(step.arrival_time)

                if departure_seconds >= entry.current_time_sec:
                    # handle midnight wrap
                    travel_time: int = (
                        arrival_seconds - entry.current_time_sec) % 86400
                    neighbor_node: Node = graph.nodes[end_name]
                    total_priority, new_transfer_count = calculate_priority(
                        entry, current_node, neighbor_node, step, travel_time, optimization_criterion
                    )
                    new_entry = QueueEntry(
                        total_priority,
                        next(counter),
                        end_name,
                        entry.path_taken + [step],
                        arrival_seconds,
                        new_transfer_count
                    )
                    heapq.heappush(queue, new_entry)

    raise NoPathFoundError(f"No path found from {start} to {end}")
