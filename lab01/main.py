import pandas as pd
import sys
from dijkstra import dijkstra
from a_star import a_star_search
from models import Graph, CommunicationStep, Path
    
csv_filename = "connection_graph.csv"
separator = ","

import pandas as pd

df: pd.DataFrame
try:
    df = pd.read_csv(f"data/{csv_filename}", encoding="utf-8", sep=separator, skipfooter=800_000, engine="python")
except FileNotFoundError:
    df = pd.read_csv(f"lab01/data/{csv_filename}", encoding="utf-8", sep=separator, skipfooter=800_000, engine="python")
    
#df: pd.DataFrame = pd.read_csv("data/connection_graph.csv", dtype={"line": str})
        
graph = Graph()

for _, row in df.iterrows():
    step: CommunicationStep = CommunicationStep.from_parsed_csv_line(list(row))
    
    for stop in [step.start_stop, step.end_stop]:
        if stop.name not in graph.nodes:
            graph.nodes[stop.name] = stop
            graph.adjacency_list[stop.name] = set()
    
    key: tuple[str, str] = (step.start_stop.name, step.end_stop.name)
    if step not in graph.edges[key]:
        graph.edges[key].add(step)
        graph.adjacency_list[step.start_stop.name].add(step)
    
print("Done parsing .csv")

def algorithm_a_to_b(a, b, optimization_criterium, start_time) -> None:
    path: Path
    
    try:
        print("Dijkstra")        
        path = dijkstra(a, b, start_time, graph, optimization_criterium)
        print(path)
    except TypeError:
        ...
    
    try:
        print("Start A*")
        path = a_star_search(a, b, start_time, graph, optimization_criterium)    
        print(path)
    except TypeError:
        ...

    
a = "Prusa"
#b = "DWORZEC GŁÓWNY"
b = "GAJ"
optimization_criterium = "t"
start_time = "08:00:00"

#print(graph.nodes)
#
#print(len(graph.adjacency_list["Zajezdnia Obornicka"]))
#for edge in graph.adjacency_list["Zajezdnia Obornicka"]:
#    print(edge)

# a = input("podaj przystanek początkowy A: ")
# b = input("podaj przystanek końcowy B: ")
# optimization_criterium = input("podaj kryterium optymalizacyjne: wartość t oznacza minimalizację czasu dojazdu, wartość p oznacza minimalizację liczby zmian linii")
# start_time = input("czas pojawienia się na przystanku początkowym")
    
algorithm_a_to_b(a, b, optimization_criterium, start_time)
