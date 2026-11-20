from datetime import date

import pytest

from agro_window_alerts.windows import (
    current_and_next_interval,
    decendio_index,
    decendio_range,
    window_intervals,
)


@pytest.mark.parametrize(
    "day, expected",
    [
        (date(2026, 1, 1), 1),
        (date(2026, 1, 10), 1),
        (date(2026, 1, 11), 2),
        (date(2026, 1, 20), 2),
        (date(2026, 1, 21), 3),
        (date(2026, 1, 31), 3),
        (date(2026, 10, 15), 29),
        (date(2026, 12, 31), 36),
    ],
)
def test_decendio_index(day, expected):
    assert decendio_index(day) == expected


def test_decendio_range_third_part_uses_month_length():
    assert decendio_range(2026, 6).end == date(2026, 2, 28)
    assert decendio_range(2028, 6).end == date(2028, 2, 29)  # leap year


def test_decendio_range_rejects_bad_index():
    with pytest.raises(ValueError):
        decendio_range(2026, 37)


def test_simple_window_becomes_one_interval_per_year():
    intervals = window_intervals(frozenset({28, 29, 30}), 2026, 2026)
    assert len(intervals) == 1
    assert intervals[0].start == date(2026, 10, 1)
    assert intervals[0].end == date(2026, 10, 31)


def test_window_crossing_new_year_is_one_interval():
    # 35, 36 = Dec 11-31 ; 1, 2 = Jan 1-20
    intervals = window_intervals(frozenset({35, 36, 1, 2}), 2026, 2026)
    assert len(intervals) == 1
    assert intervals[0].start == date(2026, 12, 11)
    assert intervals[0].end == date(2027, 1, 20)


def test_split_windows_stay_separate():
    intervals = window_intervals(frozenset({3, 4, 20, 21}), 2026, 2026)
    assert [(i.start.month, i.end.month) for i in intervals] == [(1, 2), (7, 7)]


def test_current_and_next_inside_window():
    current, upcoming = current_and_next_interval(frozenset({28, 29, 30}), date(2026, 10, 15))
    assert current is not None and current.start == date(2026, 10, 1)
    assert upcoming is not None and upcoming.start == date(2027, 10, 1)


def test_current_and_next_outside_window():
    current, upcoming = current_and_next_interval(frozenset({28, 29, 30}), date(2026, 9, 1))
    assert current is None
    assert upcoming is not None and upcoming.start == date(2026, 10, 1)


def test_inside_window_that_crosses_new_year_in_january():
    current, _ = current_and_next_interval(frozenset({35, 36, 1, 2}), date(2027, 1, 5))
    assert current is not None
    assert current.start == date(2026, 12, 11)


def test_empty_window_has_no_intervals():
    assert window_intervals(frozenset(), 2026, 2027) == []
    assert current_and_next_interval(frozenset(), date(2026, 5, 1)) == (None, None)
