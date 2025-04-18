from datetime import datetime, time
from dijkstra import dijkstra
from a_star import a_star_search
from tabu import tabu_search
from tabu_strategies import (
    DynamicTabuSizeStrategy,
    FixedTabuSizeStrategy,
    RandomSamplingStrategy,
)
from models import Graph, Path, OptimizationCriterion
from graph_provider import load_from_pickle_fallback_csv


def algorithm_a_to_b(
    a: str,
    b: str,
    optimization_criterion: OptimizationCriterion,
    start_time: time,
    use_dijkstra=False,
) -> None:
    path: Path

    if use_dijkstra:
        print("Dijkstra")
        path = dijkstra(a, b, start_time, graph)
        path.pretty_print()
    else:
        print("Start A*")
        path = a_star_search(a, b, start_time, graph, optimization_criterion)
        path.pretty_print()


def algorithm_a_through_stops(
    a, stops, optimization_criterion, start_time: time
) -> None:
    path: Path

    print("Tabu")
    path = tabu_search(
        a,
        stops,
        start_time,
        graph,
        optimization_criterion,
        tabu_size_strategy=DynamicTabuSizeStrategy(k=5.0, min_size=10),
        sampling_strategy=RandomSamplingStrategy(3),
    )
    path.pretty_print()


if __name__ == "__main__":
    graph: Graph = load_from_pickle_fallback_csv()

    one_or_two: str = input("wybierz algorytm 1 lub 2: [1/2] ")

    if one_or_two == "1":
        a: str = input("podaj przystanek początkowy A: ")
        b: str = input("podaj przystanek końcowy B: ")

        optimization_criterion_str: str = input(
            "podaj kryterium optymalizacyjne: wartość t oznacza minimalizację czasu dojazdu, wartość p oznacza minimalizację liczby zmian linii: "
        )
        start_time: str = input(
            "czas pojawienia się na przystanku początkowym: ")

        start_time_obj: time = datetime.strptime(start_time, "%H:%M:%S").time()
        optimization_criterion: OptimizationCriterion = (
            OptimizationCriterion.TIME
            if optimization_criterion_str == "t"
            else OptimizationCriterion.TRANSFERS
        )

        algorithm_a_to_b(
            a, b, optimization_criterion, start_time_obj, use_dijkstra=False
        )
    else:
        a = input("podaj przystanek początkowy A: ")

        stops: list[str] = []
        while True:
            stop: str = input(
                "podaj przystanek lub wciśnij enter aby zakończyć: ")
            if stop == "" or stop == "\n":
                break
            stops.append(stop)

        optimization_criterion_str = input(
            "podaj kryterium optymalizacyjne: wartość t oznacza minimalizację czasu dojazdu, wartość p oznacza minimalizację liczby zmian linii: "
        )
        start_time = input("czas pojawienia się na przystanku początkowym: ")

        start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
        optimization_criterion = (
            OptimizationCriterion.TIME
            if optimization_criterion_str == "t"
            else OptimizationCriterion.TRANSFERS
        )

        algorithm_a_through_stops(
            a, stops, optimization_criterion, start_time_obj)
