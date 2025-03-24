from datetime import time
import re


def time_to_seconds(t: time) -> int:
    return t.hour * 3600 + t.minute * 60 + t.second


def seconds_to_time(s: int) -> time:
    h, remainder = divmod(s, 3600)
    m, s = divmod(remainder, 60)
    return time(h % 24, m, s)


def convert_to_24_hour_time(time_to_normalize: str) -> time:
    match: re.Match[str] | None = re.match(
        r"(\d{2}):(\d{2}):(\d{2})", time_to_normalize)
    if not match:
        raise ValueError(f"Invalid time format: {time_to_normalize}")

    hour, minute, second = map(int, match.groups())

    if hour >= 24:
        hour -= 24

    return time(hour, minute, second)
