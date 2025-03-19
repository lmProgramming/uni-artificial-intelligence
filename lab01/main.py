from dataclasses import dataclass, field
from datetime import time
from geopy.point import Point 
from typing import Self
import re
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
import heapq
from itertools import count

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
    
    
df: pd.DataFrame = pd.read_csv("data/connection_graph.csv", dtype={"line": str}, skipfooter=950000, engine="python")
#df: pd.DataFrame = pd.read_csv("data/connection_graph.csv", dtype={"line": str})


class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.edges: dict[tuple[str, str], list] = defaultdict(list)
        # self.adjacency_list = defaultdict(list)
        
        
graph = Graph()

for index, row in df.iterrows():
    step: CommunicationStep = CommunicationStep.from_parsed_csv_line(list(row))
    
    for stop in [step.start_stop, step.end_stop]:
        if stop.name not in graph.nodes:
            graph.nodes[stop.name] = stop
    
    key: tuple[str, str] = (step.start_stop.name, step.end_stop.name)
    if key not in graph.edges:
        graph.edges[key] = []
    graph.edges[key].append(step)
    
'''
. Wykorzystując udostępniony plik connection_graph.csv zaimplementuj
algorytm wyszukiwania najkrótszych połączeń pomiędzy zadanymi przystankami A i B. Jako miarę odległości przyjmij, zależnie od decyzji użytkownika, czas dojazdu z A do B lub liczbę przesiadek koniecznych do wykonania.
Program powinien przyjmować na wejściu wyłącznie 4 zmienne:
(a) przystanek początkowy A
(b) przystanek końcowy B
(c) kryterium optymalizacyjne: wartość t oznacza minimalizację czasu
dojazdu, wartość p oznacza minimalizację liczby zmian linii
(d) czas pojawienia się na przystanku początkowym
Program powinien zwracać na standardowym wyjściu harmonogram przejazdu, wypisując w kolejnych liniach informacje o kolejno wykorzystanych
liniach komunikacyjnych (nazwa linii, czas i przystanek, na którym wsiadamy do danej linii komunikacyjnej oraz czas i przystanek, na którym
kończymy korzystać z danej linii). Na standardowym wyjściu błędów powinien wypisywać wartość funkcji kosztu znalezionego rozwiązania oraz
czas obliczeń liczony od wczytania danych do uzyskania rozwiązania.
8
Punktacja:
(a) algorytm wyszukiwania najkrótszej ścieżki z A do B za pomocą algorytmu algorytmem Dijkstry w oparciu o kryterium czasu (10 punktów)
(b) algorytm wyszukiwania najkrótszej ścieżki z A do B za pomocą algorytmu A* w oparciu o kryterium czasu (25 punktów)
(c) algorytm wyszukiwania najkrótszej ścieżki z A do B za pomocą algorytmu A* w oparciu o kryterium przesiadek (25 punktów)
(d) modyfikacja algorytmu A* z punktów (b) lub (c), który pozwoli
na zmniejszenie wartości funkcji kosztu uzyskanego rozwiązania lub
czasu obliczeń (10 punktów)

Algorytm Dijkstry to algorytm znajdowania najkrótszych ścieżek w grafie ważonym (o nieujemnych wagach) z jednym źródłem.
Algorytm działa poprzez utrzymywanie zbioru wierzchołków o najkrótszej odległości od źródła oraz aktualizację tych odległości wraz z dodawaniem kolejnych
wierzchołków do zbioru.
Niech G = (V, E) będzie grafem ważonym z jednym źródłem s, zbiorem wierzchołków V i zbiorem krawędzi E. Niech w : E → R będzie funkcją wag krawędzi.
Dla każdego wierzchołka v ∈ V , niech d(v) będzie kosztem najkrótszej ścieżki z
s do v, a p(v) będzie wierzchołkiem poprzedzającym v na najkrótszej ścieżce z
s do v.
4
Algorytm Dijkstry działa w następujący sposób:
1. Inicjalizuj d(s) = 0 oraz d(v) = ∞ dla każdego v ∈ V \ {s}.
2. Utwórz zbiór Q zawierający wszystkie wierzchołki grafu G.
3. Dopóki Q nie jest pusty, wykonuj:
(a) Wybierz wierzchołek u ∈ Q o najmniejszej wartości d(u) i usuń go ze
zbioru Q
(b) Dla każdego v takiego, że ∃(u, v)∈E d(v) > d(u) + w(u, v) zaktualizuj
d(v) = d(u) + w(u, v) oraz p(v) = u
4. Zwróć d oraz p
'''


@dataclass(order=True)
class QueueEntry:
    priority: int
    counter: int
    current_stop_name: str = field(compare=False)
    path_taken: list[CommunicationStep] = field(compare=False)
    current_time_sec: int = field(compare=False)

def dijkstra(start: str, end: str, start_time_str: str) -> None:
    start_node: Node = graph.nodes[start]
    end_node: Node = graph.nodes[end]
    
    start_time_obj: time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    start_time_sec: int = time_to_seconds(start_time_obj)

    queue: list[QueueEntry] = []
    counter = count()
    heapq.heappush(queue, QueueEntry(0, next(counter), start_node.name, [], start_time_sec))
    
    visited: set[str] = set()

    while queue:
        entry: QueueEntry = heapq.heappop(queue)
        
        if entry.current_stop_name in visited:
            continue
        visited.add(entry.current_stop_name)
        
        if entry.current_stop_name == end_node.name:
            print("Schedule:")
            for step in entry.path_taken:
                print(f"Line {step.line} | {step.start_stop.name} {step.departure_time} -> {step.end_stop.name} {step.arrival_time}")
            print(f"Total time: {entry.priority // 60} minutes {entry.priority % 60} seconds")
            return
        
        for (start_name, end_name), steps in graph.edges.items():
            if start_name != entry.current_stop_name:
                continue
            for step in steps:
                dep_sec = time_to_seconds(step.departure_time)
                arr_sec = time_to_seconds(step.arrival_time)
                
                if dep_sec >= entry.current_time_sec:
                    travel_time = arr_sec - entry.current_time_sec
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

    print("No path found.")


def algorithm_a_to_b(a, b, optimization_criterium, start_time):
    dijkstra(a, b, start_time)
    
a = "Zajezdnia Obornicka"
b = "Psie Pole"
optimization_criterium = "t"
start_time = "15:20:00"
    
print(datetime.now())
algorithm_a_to_b(a, b, optimization_criterium, start_time)
print(datetime.now())
