from dataclasses import dataclass, field
from datetime import time
from utils import time_to_seconds
import heapq
from itertools import count
import time as t
from models import Node, Path, CommunicationStep, NoPathFoundError, Graph
from path_utils import generate_path, post_clear_cache


@dataclass(order=True)
class QueueEntry:
    priority: int
    counter: int
    current_stop_name: str = field(compare=False)
    path_taken: list[CommunicationStep] = field(compare=False)
    current_time_sec: int = field(compare=False)


@post_clear_cache
def dijkstra(start: str, end: str, start_time: time, graph: Graph) -> Path:
    if start not in graph.nodes:
        raise ValueError("Start stop does not exist in the graph.")
    if end not in graph.nodes:
        raise ValueError("End stop does not exist in the graph.")

    start_node: Node = graph.nodes[start]
    end_node: Node = graph.nodes[end]

    start_time_sec: int = time_to_seconds(start_time)

    queue: list[QueueEntry] = []
    counter = count()
    heapq.heappush(
        queue, QueueEntry(0, next(counter), start_node.name, [], start_time_sec)
    )

    visited: set[str] = set()

    start_time_perf: float = t.perf_counter()

    while queue:
        entry: QueueEntry = heapq.heappop(queue)

        if entry.current_stop_name in visited:
            continue
        visited.add(entry.current_stop_name)

        if entry.current_stop_name == end_node.name:
            elapsed: float = t.perf_counter() - start_time_perf

            path: Path = generate_path(start, entry.path_taken, elapsed, entry.priority)

            return path

        for (start_name, end_name), steps in graph.edges.items():
            if start_name != entry.current_stop_name:
                continue
            for step in steps:
                departure_seconds: int = time_to_seconds(step.departure_time)
                arrival_seconds: int = time_to_seconds(step.arrival_time)

                if departure_seconds >= entry.current_time_sec:
                    travel_time: int = arrival_seconds - entry.current_time_sec
                    if travel_time < 0:
                        travel_time += 86400  # handle crossing midnight

                    new_priority: int = entry.priority + travel_time
                    new_queue_entry = QueueEntry(
                        new_priority,
                        next(counter),
                        end_name,
                        entry.path_taken + [step],
                        arrival_seconds,
                    )
                    heapq.heappush(queue, new_queue_entry)

    raise NoPathFoundError(f"No path found from {start} to {end}")
