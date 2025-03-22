from dataclasses import dataclass, field
from models import Node, Path, Graph
from datetime import time, timedelta
import heapq
from itertools import count
from collections import defaultdict
from models import Node, Path, PathStep, CommunicationStep, NoPathFoundError, Graph
from utils import heuristic, time_to_seconds, seconds_to_time, generate_path
from datetime import datetime
import time as t

@dataclass(order=True)
class QueueEntry:
    priority: float
    counter: int
    current_stop_name: str = field(compare=False)
    path_taken: list[CommunicationStep] = field(compare=False)
    current_time_sec: int = field(compare=False)

def reconstruct_path(came_from, current_stop_name):
    total_path = []
    while current_stop_name in came_from:
        current_stop_name, step = came_from[current_stop_name]
        total_path.append(step)
    return total_path[::-1]

def a_star_search(start: str, end: str, start_time_str: str, graph: Graph, optimization_criterion: str) -> Path:
    if start not in graph.nodes:
        raise ValueError("Start stop does not exist in the graph.")
    if end not in graph.nodes:
        raise ValueError("End stop does not exist in the graph.")
       
    start_node: Node = graph.nodes[start]
    end_node: Node = graph.nodes[end]
    
    start_time_obj: time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    start_time_sec: int = time_to_seconds(start_time_obj)

    queue: list[QueueEntry] = []
    counter = count()
    initial_heuristic: float = heuristic(start_node, end_node)
    heapq.heappush(queue, QueueEntry(initial_heuristic, next(counter), start_node.name, [], start_time_sec))
    
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
        
        current_node = graph.nodes[entry.current_stop_name]

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
                    
                    # Get Node objects for heuristic
                    neighbor_node = graph.nodes[end_name]
                    
                    # Adjust priority calculation
                    cost_so_far: float = entry.priority - heuristic(current_node, end_node) + travel_time
                    estimated_remaining: float = heuristic(neighbor_node, end_node)
                    total_priority: float = cost_so_far + estimated_remaining
                    
                    new_queue_entry = QueueEntry(
                        total_priority,
                        next(counter),
                        end_name,
                        entry.path_taken + [step],
                        arrival_seconds
                    )
                    heapq.heappush(queue, new_queue_entry)

    raise NoPathFoundError(f"No path found from {start} to {end}")
