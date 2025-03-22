from dataclasses import dataclass, field
from models import Node, Path, Graph
from datetime import time, timedelta
import heapq
from itertools import count
from collections import defaultdict
from models import Node, Path, LineStep, CommunicationStep, NoPathFoundError, Graph, OptimizationCriterion
from path_utils import distance_heuristic, transfer_heuristic, generate_path, clear_caches
from utils import time_to_seconds, seconds_to_time
from datetime import datetime
import time as t

@dataclass(order=True)
class QueueEntry:
    priority: float
    counter: int
    current_stop_name: str = field(compare=False)
    path_taken: list[CommunicationStep] = field(compare=False)
    current_time_sec: int = field(compare=False)
    transfer_count: int = field(compare=False)

def a_star_search(start: str, end: str, start_time: time, graph: Graph, optimization_criterion: OptimizationCriterion) -> Path:
    if start not in graph.nodes:
        raise ValueError("Start stop does not exist in the graph.")
    if end not in graph.nodes:
        raise ValueError("End stop does not exist in the graph.")
           
    start_node: Node = graph.nodes[start]
    end_node: Node = graph.nodes[end]
    
    start_time_sec: int = time_to_seconds(start_time)

    queue: list[QueueEntry] = []
    counter = count()
    initial_heuristic: float = distance_heuristic(start_node, end_node)
    heapq.heappush(queue, QueueEntry(initial_heuristic, next(counter), start_node.name, [], start_time_sec, 0))
    
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
            clear_caches()
            
            return path
        
        current_node: Node = graph.nodes[entry.current_stop_name]

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
                    
                    neighbor_node: Node = graph.nodes[end_name]
                    
                    cost_so_far: float = entry.priority - distance_heuristic(current_node, end_node) + travel_time
                    estimated_remaining: float = distance_heuristic(neighbor_node, end_node)
                    
                    transfer_penalty: float = 0
                    new_transfer_count: int = 0
                    
                    if optimization_criterion == OptimizationCriterion.TRANSFERS:
                        transfer_penalty = transfer_heuristic(entry.transfer_count)                       
                        if entry.path_taken:
                            previous_step: CommunicationStep = entry.path_taken[-1]
                            is_transfer: bool = previous_step.line != step.line
                            new_transfer_count = entry.transfer_count + (1 if is_transfer else 0)
                            
                    total_priority: float = cost_so_far + estimated_remaining + transfer_penalty
                    
                    new_queue_entry = QueueEntry(
                        total_priority,
                        next(counter),
                        end_name,
                        entry.path_taken + [step],
                        arrival_seconds,
                        new_transfer_count
                    )
                    heapq.heappush(queue, new_queue_entry)

    clear_caches()
    raise NoPathFoundError(f"No path found from {start} to {end}")