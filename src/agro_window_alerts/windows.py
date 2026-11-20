"""Ten-day period ("decêndio") arithmetic for planting windows."""

from __future__ import annotations

import calendar
from datetime import date, timedelta

from .models import DateInterval

DECENDIOS_PER_YEAR = 36


def decendio_index(day: date) -> int:
    """Return the decêndio index (1..36) that contains ``day``."""
    part = 1 if day.day <= 10 else 2 if day.day <= 20 else 3
    return (day.month - 1) * 3 + part


def decendio_range(year: int, index: int) -> DateInterval:
    """Return the first and last day of decêndio ``index`` in ``year``."""
    if not 1 <= index <= DECENDIOS_PER_YEAR:
        raise ValueError(f"decendio index must be 1..36, got {index}")
    month = (index - 1) // 3 + 1
    part = (index - 1) % 3 + 1
    last_day = calendar.monthrange(year, month)[1]
    start_day, end_day = {1: (1, 10), 2: (11, 20), 3: (21, last_day)}[part]
    return DateInterval(date(year, month, start_day), date(year, month, end_day))


def _runs(indices: frozenset[int]) -> list[list[int]]:
    """Split indices into runs of consecutive decêndios, joining across New Year."""
    if not indices:
        return []
    if len(indices) == DECENDIOS_PER_YEAR:
        return [list(range(1, DECENDIOS_PER_YEAR + 1))]

    ordered = sorted(indices)
    runs: list[list[int]] = [[ordered[0]]]
    for idx in ordered[1:]:
        if idx == runs[-1][-1] + 1:
            runs[-1].append(idx)
        else:
            runs.append([idx])

    # A window such as Nov-Jan is stored as 31..36 and 1..3: join the two runs.
    if len(runs) > 1 and runs[0][0] == 1 and runs[-1][-1] == DECENDIOS_PER_YEAR:
        runs[-1].extend(runs.pop(0))
    return runs


def window_intervals(
    indices: frozenset[int], first_year: int, last_year: int
) -> list[DateInterval]:
    """Turn decêndio indices into concrete date intervals for a range of years.

    Runs that cross New Year are returned as a single interval starting in
    one year and ending in the next.
    """
    intervals: list[DateInterval] = []
    for run in _runs(indices):
        crosses_new_year = run[0] > run[-1] or any(
            b < a for a, b in zip(run, run[1:])
        )
        for year in range(first_year, last_year + 1):
            start = decendio_range(year, run[0]).start
            end_year = year + 1 if crosses_new_year else year
            end = decendio_range(end_year, run[-1]).end
            intervals.append(DateInterval(start, end))
    return sorted(intervals, key=lambda i: i.start)


def current_and_next_interval(
    indices: frozenset[int], today: date
) -> tuple[DateInterval | None, DateInterval | None]:
    """Return (interval containing today, next interval starting after today)."""
    candidates = window_intervals(indices, today.year - 1, today.year + 1)
    current = next((i for i in candidates if i.contains(today)), None)
    upcoming = next((i for i in candidates if i.start > today), None)
    return current, upcoming


def days_between(later: date, earlier: date) -> int:
    return (later - earlier) // timedelta(days=1)
