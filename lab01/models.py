from dataclasses import dataclass
from datetime import time
from geopy.point import Point
import utils
from collections import defaultdict
import sys

@dataclass
class Node:
    name: str
    location: Point
    _hash: int = 0

    def __post_init__(self):
        self._hash = hash((self.name, self.location.format_unicode()))

    def __hash__(self):
        return self._hash
     

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
        
        departure_time: time = utils.convert_to_24_hour_time(departure_str)
        arrival_time: time = utils.convert_to_24_hour_time(arrival_str)
        
        new_communication_step = CommunicationStep(company, line, departure_time, arrival_time, start_stop, end_stop)
        
        return new_communication_step
    
    def __str__(self):
        return f"line {self.line} | {self.start_stop} {self.departure_time} -> {self.end_stop} {self.arrival_time}"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CommunicationStep):
            return False
        return (
            self.company == other.company and
            self.line == other.line and
            self.departure_time == other.departure_time and
            self.arrival_time == other.arrival_time and
            self.start_stop == other.start_stop and
            self.end_stop == other.end_stop
        )   
        
    def __hash__(self) -> int:
        return hash((self.company, self.line, self.departure_time, self.arrival_time, self.start_stop, self.end_stop))

class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: dict[tuple[str, str], set[CommunicationStep]] = defaultdict(set)
        self.adjacency_list: dict[str, set[CommunicationStep]] = defaultdict(set)

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
    
    def __str__(self):
        print("Schedule:")
        for step in self.steps:
            print(f"Line {step.line} | {step.start_node_name} {step.start_time} -> {step.end_node_name} {step.end_time}")
        print(f"Total time: {self.cost // 60} minutes and {self.cost % 60} seconds", file=sys.stderr)
        print(f"Execution time: {self.calculation_time:.4f} seconds", file=sys.stderr)
    
    
class NoPathFoundError(Exception):
    """Raised when no path is found between the start and end nodes."""
    pass