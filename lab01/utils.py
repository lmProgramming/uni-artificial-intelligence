from datetime import time
import re
from geopy.distance import geodesic
import models

def time_to_seconds(t: time) -> int:
    return t.hour * 3600 + t.minute * 60 + t.second

def seconds_to_time(s: int) -> time:
    h, remainder = divmod(s, 3600)
    m, s = divmod(remainder, 60)
    return time(h % 24, m, s)

def convert_to_24_hour_time(time_to_normalize: str) -> time:
    match: re.Match[str] | None = re.match(r"(\d{2}):(\d{2}):(\d{2})", time_to_normalize)
    if not match:
        raise ValueError(f"Invalid time format: {time_to_normalize}")
    
    hour, minute, second = map(int, match.groups())
    
    if hour >= 24:
        hour -= 24
    
    return time(hour, minute, second)

def heuristic(node1: models.Node, node2: models.Node) -> float:
    return geodesic(node1.location, node2.location).kilometers

def generate_path(start: str, path_taken: list[models.CommunicationStep], elapsed: float, cost: float) -> models.Path:
    path_steps: list[models.PathStep] = []
            
    step: models.CommunicationStep = path_taken[0]
    last_line: str = step.line            
    path_steps.append(models.PathStep(start, "", step.line, str(step.departure_time), ""))
            
    for i, step in enumerate(path_taken[:-1]):
        if step.line == last_line:
            continue
        last_line = step.line    
                
        path_steps[-1].end_time = str(path_taken[i - 1].arrival_time)
        path_steps[-1].end_node_name = step.start_stop.name
                
        path_steps.append(models.PathStep(step.start_stop.name, "", last_line, str(step.departure_time), ""))   
                            
                
    step = path_taken[-1]
    path_steps[-1].end_time = str(step.arrival_time)
    path_steps[-1].end_node_name = step.end_stop.name
            
    path: models.Path = models.Path(path_steps, cost, elapsed)
    return path