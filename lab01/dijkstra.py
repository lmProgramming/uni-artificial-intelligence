from dataclasses import dataclass, field
from datetime import time
from utils import time_to_seconds
from datetime import datetime
import heapq
from itertools import count
import time as t
from models import Node, Path, PathStep, CommunicationStep, NoPathFoundError, Graph

@dataclass(order=True)
class QueueEntry:
    priority: int
    counter: int
    current_stop_name: str = field(compare=False)
    path_taken: list[CommunicationStep] = field(compare=False)
    current_time_sec: int = field(compare=False)

def dijkstra(start: str, end: str, start_time_str: str, graph: Graph, optimization_criterion: str) -> Path:
    start_node: Node = graph.nodes[start]
    end_node: Node = graph.nodes[end]
    
    start_time_obj: time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    start_time_sec: int = time_to_seconds(start_time_obj)

    queue: list[QueueEntry] = []
    counter = count()
    heapq.heappush(queue, QueueEntry(0, next(counter), start_node.name, [], start_time_sec))
    
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
                dep_sec: int = time_to_seconds(step.departure_time)
                arr_sec: int = time_to_seconds(step.arrival_time)
                
                if dep_sec >= entry.current_time_sec:
                    travel_time: int = arr_sec - entry.current_time_sec
                    if travel_time < 0:
                        travel_time += 86400  # handle crossing midnight
                    
                    new_priority: int = entry.priority + travel_time
                    new_queue_entry = QueueEntry(
                        new_priority,
                        next(counter),
                        end_name,
                        entry.path_taken + [step],
                        arr_sec
                    )
                    heapq.heappush(queue, new_queue_entry)

    raise NoPathFoundError(f"No path found from {start} to {end}")