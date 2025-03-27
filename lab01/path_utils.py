from geopy.distance import geodesic
import models
from functools import lru_cache
from datetime import time


@lru_cache(maxsize=None)
def distance_heuristic(node1: models.Node, node2: models.Node) -> float:
    return geodesic(node1.location, node2.location).kilometers ** 2


def transfer_heuristic(transfer_count: int) -> float:
    transfer_penalty_weight = 500000
    return transfer_count * transfer_penalty_weight


def clear_caches() -> None:
    distance_heuristic.cache_clear()


def post_clear_cache(func):
    def wrapper(*args, **kwargs) -> None:
        result = func(*args, **kwargs)
        clear_caches()
        return result

    return wrapper


def generate_path(
    start: str, path_taken: list[models.CommunicationStep], elapsed: float, cost: float
) -> models.Path:
    path_steps: list[models.LineStep] = []

    none_time: time = time(0, 0)

    step: models.CommunicationStep = path_taken[0]
    last_line: str = step.line
    path_steps.append(
        models.LineStep(start, "", step.line, step.departure_time, none_time)
    )

    for i, step in enumerate(path_taken[:-1]):
        if step.line == last_line:
            continue
        last_line = step.line

        path_steps[-1].end_time = path_taken[i - 1].arrival_time
        path_steps[-1].end_node_name = step.start_stop.name

        path_steps.append(
            models.LineStep(
                step.start_stop.name, "", last_line, step.departure_time, none_time
            )
        )

    step = path_taken[-1]
    path_steps[-1].end_time = step.arrival_time
    path_steps[-1].end_node_name = step.end_stop.name

    path: models.Path = models.Path(path_steps, cost, elapsed)
    return path
