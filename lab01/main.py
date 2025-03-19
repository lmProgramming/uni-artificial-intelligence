import pandas as pd
import sys
from dijkstra import dijkstra
from a_star import a_star_search
from models import Graph, CommunicationStep, Path    
    
df: pd.DataFrame = pd.read_csv("data/connection_graph.csv", dtype={"line": str}, skipfooter=950000, engine="python")
#df: pd.DataFrame = pd.read_csv("data/connection_graph.csv", dtype={"line": str})
        
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

def algorithm_a_to_b(a, b, optimization_criterium, start_time) -> None:
    path: Path = dijkstra(a, b, start_time, graph, "t")
    #path: Path = a_star_search(a, b, start_time, graph, optimization_criterion="t")
    
    print("Schedule:")
    for step in path.steps:
        print(f"Line {step.line} | {step.start_node_name} {step.start_time} -> {step.end_node_name} {step.end_time}")
    print(f"Total time: {path.cost // 60} minutes and {path.cost % 60} seconds", file=sys.stderr)
    print(f"Execution time: {path.calculation_time:.4f} seconds", file=sys.stderr)
    
a = "Zajezdnia Obornicka"
b = "Syrokomli"
optimization_criterium = "t"
start_time = "15:20:00"

# a = input("podaj przystanek początkowy A: ")
# b = input("podaj przystanek końcowy B: ")
# optimization_criterium = input("podaj kryterium optymalizacyjne: wartość t oznacza minimalizację czasu dojazdu, wartość p oznacza minimalizację liczby zmian linii")
# start_time = input("czas pojawienia się na przystanku początkowym")
    
algorithm_a_to_b(a, b, optimization_criterium, start_time)
