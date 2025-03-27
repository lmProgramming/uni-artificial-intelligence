import pandas as pd
from models import Graph, CommunicationStep
import pickle
import os

csv_filename = "connection_graph"
separator = ","
skipfooter = 0
graph: Graph


def try_load_from_pickle() -> Graph | None:
    graph: Graph | None = None

    if os.path.exists(f"data/{csv_filename}.pkl"):
        with open(f"data/{csv_filename}.pkl", "rb") as f:
            graph = pickle.load(f)
        print("Graph loaded from graph.pkl.")
    if os.path.exists(f"lab01/data/{csv_filename}.pkl"):
        with open(f"lab01/data/{csv_filename}.pkl", "rb") as f:
            graph = pickle.load(f)
        print("Graph loaded from graph.pkl.")

    return graph


def load_from_csv() -> Graph:
    graph: Graph

    df: pd.DataFrame
    if os.path.exists(f"data/{csv_filename}.csv"):
        df = pd.read_csv(f"data/{csv_filename}.csv", encoding="utf-8",
                         sep=separator, skipfooter=skipfooter, engine="python")
    else:
        df = pd.read_csv(f"lab01/data/{csv_filename}.csv", encoding="utf-8",
                         sep=separator, skipfooter=skipfooter, engine="python")

    graph = Graph()

    for _, row in df.iterrows():
        step: CommunicationStep = CommunicationStep.from_parsed_csv_line(
            list(row))

        for stop in [step.start_stop, step.end_stop]:
            if stop.name not in graph.nodes:
                graph.nodes[stop.name] = stop
                graph.adjacency_list[stop.name] = list()

        key: tuple[str, str] = (step.start_stop.name, step.end_stop.name)
        if step not in graph.edges[key]:
            graph.add_edge(step.start_stop.name, step.end_stop.name, step)

    graph.sort_adjacency_list()

    with open(f"data/{csv_filename}.pkl", "wb") as f2:
        pickle.dump(graph, f2)

    print("Done parsing .csv")

    return graph


def load_from_pickle_fallback_csv() -> Graph:
    graph: Graph | None = try_load_from_pickle()

    if graph is not None:
        return graph

    graph = load_from_csv()

    return graph
