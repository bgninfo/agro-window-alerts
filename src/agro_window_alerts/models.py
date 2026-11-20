"""Plain data types shared by the whole package."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Watch:
    """One crop in one municipality that should be monitored."""

    id: str
    name: str
    crop: str
    municipality_ibge: int
    latitude: float
    longitude: float
    agritec_crop_id: int | None = None
    recipients: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlantingWindow:
    """A period in which planting is recommended at a given risk level.

    ``decendios`` holds indices 1..36 (three ten-day periods per month):
    index = (month - 1) * 3 + part, with part 1 = days 1-10,
    2 = days 11-20 and 3 = day 21 to the end of the month.
    """

    crop: str
    risk_level: int  # accepted loss risk in percent: 20, 30 or 40
    decendios: frozenset[int]


@dataclass(frozen=True)
class DateInterval:
    """A concrete, inclusive date range."""

    start: date
    end: date

    def contains(self, day: date) -> bool:
        return self.start <= day <= self.end


@dataclass(frozen=True)
class ForecastDay:
    """Daily weather forecast for one location."""

    day: date
    precipitation_mm: float
    tmax_c: float | None = None
    tmin_c: float | None = None


@dataclass(frozen=True)
class Alert:
    """Something worth telling the user about.

    ``key`` identifies the occurrence (for example the date a window opens),
    so the same alert is not sent twice.
    """

    watch_id: str
    kind: str
    key: str
    message: str
    details: dict = field(default_factory=dict)

    @property
    def dedupe_id(self) -> str:
        return f"{self.watch_id}:{self.kind}:{self.key}"
