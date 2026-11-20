"""Made-up data for trying the tool without any API credentials.

Nothing here comes from Embrapa. It exists so that ``--demo`` runs end to end.
"""

from __future__ import annotations

from datetime import date, timedelta

from ..models import ForecastDay, PlantingWindow, Watch


class SampleSource:
    """Fake planting windows and a fake forecast, for demos and tests."""

    # Example only: decêndios 28-33 are 1 October to 30 November.
    _WINDOW_DECENDIOS = frozenset(range(28, 34))

    def planting_windows(self, watch: Watch) -> list[PlantingWindow]:
        return [
            PlantingWindow(watch.crop, 20, self._WINDOW_DECENDIOS),
            PlantingWindow(watch.crop, 30, self._WINDOW_DECENDIOS | {27, 34}),
            PlantingWindow(watch.crop, 40, self._WINDOW_DECENDIOS | {26, 27, 34, 35}),
        ]

    def forecast(self, watch: Watch, today: date) -> list[ForecastDay]:
        rain = [0.0, 2.0, 0.0, 55.0, 1.0, 0.0, 0.0]
        return [
            ForecastDay(today + timedelta(days=i), mm, tmax_c=31.0, tmin_c=20.0)
            for i, mm in enumerate(rain)
        ]
