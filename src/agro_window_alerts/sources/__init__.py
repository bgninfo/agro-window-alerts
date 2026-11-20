"""Where planting windows and forecasts come from."""

from __future__ import annotations

from datetime import date
from typing import Protocol

from ..models import ForecastDay, PlantingWindow, Watch


class DataSource(Protocol):
    def planting_windows(self, watch: Watch) -> list[PlantingWindow]: ...

    def forecast(self, watch: Watch, today: date) -> list[ForecastDay]: ...
