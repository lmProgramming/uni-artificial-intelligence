from dataclasses import dataclass
from datetime import time
from geopy.point import Point
from utils import convert_to_24_hour_time
from collections import defaultdict


@dataclass 
class Node:
    name: str
    location: Point
     

@dataclass
class CommunicationStep:
    company: str
    line: str
    departure_time: time
    arrival_time: time
    start_stop: Node
    end_stop: Node
    
    @staticmethod
    def from_parsed_csv_line(row: list[str]) -> "CommunicationStep":
        start_stop_point: Point = Point(latitude=row[7], longitude=row[8])
        start_stop = Node(row[5], start_stop_point)
        
        end_stop_point: Point = Point(latitude=row[9], longitude=row[10])
        end_stop = Node(row[6], end_stop_point)
        
        company, line, departure_str, arrival_str = row[1:5]
        
        departure_time: time = convert_to_24_hour_time(departure_str)
        arrival_time: time = convert_to_24_hour_time(arrival_str)
        
        new_communication_step = CommunicationStep(company, line, departure_time, arrival_time, start_stop, end_stop)
        
        return new_communication_step
    
    def __str__(self):
        return f"line {self.line} | {self.start_stop} {self.departure_time} -> {self.end_stop} {self.arrival_time}"
    

class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: dict[tuple[str, str], list] = defaultdict(list)
        # self.adjacency_list = defaultdict(list)

@dataclass
class PathStep:
    start_node_name: str
    end_node_name: str
    line: str
    start_time: str
    end_time: str

@dataclass
class Path:
    steps: list[PathStep]
    cost: float
    calculation_time: float
    
    
class NoPathFoundError(Exception):
    """Raised when no path is found between the start and end nodes."""
    pass