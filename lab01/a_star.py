from dataclasses import dataclass, field
from models import Node, Path, Graph
from datetime import time, timedelta
import heapq
from itertools import count
from collections import defaultdict
from utils import heuristic, time_to_seconds, seconds_to_time, generate_path

@dataclass(order=True)
class QueueEntry:
    priority: float
    counter: int
    current_stop_name: str = field(compare=False)
    path_taken: list = field(compare=False)
    current_time: time = field(compare=False)
    start_time: time = field(compare=False)
    transfers: int = field(compare=False)

def reconstruct_path(came_from, current_stop_name):
    total_path = []
    while current_stop_name in came_from:
        current_stop_name, step = came_from[current_stop_name]
        total_path.append(step)
    return total_path[::-1]

def a_star_search(start: str, end: str, start_time: str, graph: Graph, optimization_criterion: str):
    if start not in graph.nodes:
        raise ValueError("Start stop does not exist in the graph.")
    if end not in graph.nodes:
        raise ValueError("End stop does not exist in the graph.")
        
    start_node: Node = graph.nodes[start]
    end_node: Node = graph.nodes[end]

    open_set: list[QueueEntry] = []
    counter = 0
    start_time_obj = time.fromisoformat(start_time)
    heapq.heappush(open_set, QueueEntry(
        0, counter, start, [], start_time_obj, start_time_obj, 0
    ))
    
    came_from = {}
    g_score = defaultdict(lambda: float('inf'))
    g_score[start] = 0
    f_score = defaultdict(lambda: float('inf'))
    f_score[start] = heuristic(start_node, end_node)

    while open_set:
        current_entry: QueueEntry = heapq.heappop(open_set)
        current_stop_name: str = current_entry.current_stop_name
        current_time: time = current_entry.current_time
        current_transfers: int = current_entry.transfers

        # Debug
        print(f"\nAt stop: {current_stop_name}, time: {current_time}, transfers: {current_transfers}")

        if current_stop_name == end:
            total_duration: float = g_score[end]
            stops = reconstruct_path(came_from, current_stop_name)
            path = generate_path(start, stops, 0, 0)
            return path

        for step in graph.adjacency_list[current_stop_name]:
            # Debug info
            print(f"Checking edge: {step.start_stop.name} -> {step.end_stop.name}, departs at {step.departure_time}, arrives at {step.arrival_time}")

            dep_sec: int = time_to_seconds(step.departure_time)
            arr_sec: int = time_to_seconds(step.arrival_time)
            current_time_sec: int = time_to_seconds(current_time)

            # Skip if the departure time is earlier than the current time
            if dep_sec < current_time_sec:
                dep_sec += 86400  # Handle crossing midnight
                arr_sec += 86400

            tentative_g_score: float = g_score[current_stop_name]

            if optimization_criterion == 't':
                travel_time: int = arr_sec - dep_sec
                tentative_g_score += travel_time
            elif optimization_criterion == 'p':
                tentative_g_score += 1 if not current_entry.path_taken or current_entry.path_taken[-1].line != step.line else 0

            if tentative_g_score < g_score[step.end_stop.name]:
                came_from[step.end_stop.name] = (current_stop_name, step)
                g_score[step.end_stop.name] = tentative_g_score
                f_score[step.end_stop.name] = tentative_g_score + heuristic(step.end_stop, end_node)

                new_arrival_time: time = seconds_to_time(arr_sec % 86400)  # Convert back to time object

                counter += 1  # Increment counter before pushing
                heapq.heappush(open_set, QueueEntry(
                    f_score[step.end_stop.name],
                    counter,
                    step.end_stop.name,
                    current_entry.path_taken + [step],
                    new_arrival_time,
                    current_entry.start_time,
                    current_transfers + (1 if not current_entry.path_taken or current_entry.path_taken[-1].line != step.line else 0)
                ))

    raise ValueError("No path found from start to end.")