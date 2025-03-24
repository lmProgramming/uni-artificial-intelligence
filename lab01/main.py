from datetime import datetime, time
import pandas as pd
from dijkstra import dijkstra
from a_star import a_star_search
from tabu import tabu_search
from models import Graph, CommunicationStep, Path, OptimizationCriterion
import pickle
import os

csv_filename = "connection_graph"
separator = ","
skipfooter = 0

if os.path.exists(f"data/{csv_filename}.pkl"):
    with open(f"data/{csv_filename}.pkl", "rb") as f:
        graph: Graph = pickle.load(f)
    print("Graph loaded from graph.pkl.")
if os.path.exists(f"lab01/data/{csv_filename}.pkl"):
    with open(f"lab01/data/{csv_filename}.pkl", "rb") as f:
        graph: Graph = pickle.load(f)
    print("Graph loaded from graph.pkl.")
else:
    df: pd.DataFrame
    try:
        df = pd.read_csv(f"data/{csv_filename}.csv", encoding="utf-8",
                         sep=separator, skipfooter=skipfooter, engine="python")
    except FileNotFoundError:
        df = pd.read_csv(f"lab01/data/{csv_filename}.csv", encoding="utf-8",
                         sep=separator, skipfooter=skipfooter, engine="python")

    # df: pd.DataFrame = pd.read_csv("data/connection_graph.csv", dtype={"line": str})

    graph = Graph()

    for _, row in df.iterrows():
        step: CommunicationStep = CommunicationStep.from_parsed_csv_line(
            list(row))

        for stop in [step.start_stop, step.end_stop]:
            if stop.name not in graph.nodes:
                graph.nodes[stop.name] = stop
                graph.adjacency_list[stop.name] = set()

        key: tuple[str, str] = (step.start_stop.name, step.end_stop.name)
        if step not in graph.edges[key]:
            graph.edges[key].add(step)
            graph.adjacency_list[step.start_stop.name].add(step)

    with open(f"data/{csv_filename}.pkl", "wb") as f2:
        pickle.dump(graph, f2)

    print("Done parsing .csv")

r'''
Wykorzystując udostępniony plik connection_graph.csv zaimplementuj
algorytm, który dla przystanku początkowe A oraz listy przystanków L=
A2, . . . , An wyszuka najkrótszą trasę rozpoczynającą a A, przebiegającą
przez wszystkie przystanki z L i wracającą do A. Jako funkcję kosztu trasy
przyjmij, zależnie od decyzji użytkownika, łączny czas przejazdu lub liczbę
przesiadek koniecznych do wykonania.
Program powinien przyjmować na wejściu 4 linie:
(a) przystanek początkowy A
(b) listę oddzielonych średnikiem przystanków do odwiedzenia
(c) kryterium optymalizacyjne: wartość t oznacza minimalizację czasu
dojazdu, wartość p oznacza minimalizację liczby zmian linii
(d) czas pojawienia się na przystanku początkowym
Program powinien zwracać na standardowym wyjściu harmonogram prze-
jazdu, wypisując w kolejnych liniach informacje o kolejno wykorzystanych
liniach komunikacyjnych (nazwa linii, czas i przystanek, na którym wsia-
damy do danej linii komunikacyjnej oraz czas i przystanek, na którym
kończymy korzystać z danej linii). Na standardowym wyjściu błędów po-
winien wypisywać wartość funkcji kosztu znalezionego rozwiązania oraz
czas obliczeń liczony od wczytania danych do uzyskania rozwiązania.
Punktacja:
(a) algorytm rozwiązujący problem odwiedzenia wierzchołków oparty na
przeszukiwaniu Tabu bez ograniczenia na rozmiar tablicy T (10 punk-
tów)
(b) modyfikacja (a) o dobór długości tablicy T w zależności od długości
listy L w celu minimalizacji funkcji kosztu (5 punktów)
(c) modyfikacja (a) o aspirację w celu minimalizacji funkcji kosztu (5
punktów)
9
(d) rozszerzenie (a) poprzez dobór strategii próbkowania sąsiedztwa bie-
żącego rozwiązania, które pozwoli na minimalizację funkcji kosztu i
skrócenie czasu działania algorytmu (10 punktów)
'''


def algorithm_a_to_b(a: str, b: str, optimization_criterion: OptimizationCriterion, start_time: time) -> None:
    path: Path

    try:
        print("Dijkstra")
        path = dijkstra(a, b, start_time, graph)
        path.pretty_print()
    except TypeError as e:
        print(e)

    try:
        print("Start A*")
        path = a_star_search(a, b, start_time, graph,
                             OptimizationCriterion.TIME)
        path.pretty_print()
    except TypeError as e:
        print(e)

    try:
        print("Start A* 2")
        path = a_star_search(a, b, start_time, graph,
                             OptimizationCriterion.TRANSFERS)
        path.pretty_print()
    except TypeError as e:
        print(e)


def algorithm_a_through_stops(a, stops, optimization_criterion, start_time: time) -> None:
    path: Path

    try:
        print("Tabu")
        path = tabu_search(a, stops, start_time, graph, optimization_criterion)
        path.pretty_print()
    except TypeError as e:
        print(e)


a = "Prusa"
# b = "DWORZEC GŁÓWNY"
b = "PORT LOTNICZY"
optimization_criterion_str = "p"
start_time = "08:00:00"

# a = input("podaj przystanek początkowy A: ")
# b = input("podaj przystanek końcowy B: ")
# optimization_criterium = input("podaj kryterium optymalizacyjne: wartość t oznacza minimalizację czasu dojazdu, wartość p oznacza minimalizację liczby zmian linii")
# start_time = input("czas pojawienia się na przystanku początkowym")

start_time_obj: time = datetime.strptime(start_time, "%H:%M:%S").time()
optimization_criterion: OptimizationCriterion = OptimizationCriterion.TIME if optimization_criterion_str == "t" else OptimizationCriterion.TRANSFERS

algorithm_a_to_b(a, b, optimization_criterion, start_time_obj)
algorithm_a_to_b(a, "pl. Orląt Lwowskich",
                 optimization_criterion, start_time_obj)
algorithm_a_to_b("pl. Orląt Lwowskich", b,
                 optimization_criterion, start_time_obj)
algorithm_a_through_stops(
    a, ["pl. Orląt Lwowskich", "PORT LOTNICZY"], optimization_criterion, start_time_obj)
