"""Turn planting windows and forecasts into alerts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .models import Alert, ForecastDay, PlantingWindow, Watch
from .windows import current_and_next_interval, days_between


@dataclass(frozen=True)
class Rules:
    """Thresholds that decide when an alert is raised.

    The defaults are conservative examples, not agronomic advice.
    Tune them per crop and region.
    """

    lead_days: int = 7  # warn this many days before a window opens or closes
    risk_level: int = 20  # which risk level of the window to follow (20, 30, 40)
    forecast_days: int = 5  # how many days ahead to look for weather alerts
    dry_spell_mm: float = 10.0  # total rain below this over the period = dry
    heavy_rain_mm: float = 50.0  # one day above this = heavy rain


def _fmt(day: date) -> str:
    return day.strftime("%d/%m/%Y")


def window_alerts(
    watch: Watch, windows: list[PlantingWindow], today: date, rules: Rules
) -> list[Alert]:
    """Alerts about a planting window opening, being open or closing."""
    window = next((w for w in windows if w.risk_level == rules.risk_level), None)
    if window is None:
        return []

    current, upcoming = current_and_next_interval(window.decendios, today)
    label = f"{watch.name} ({watch.crop})"
    alerts: list[Alert] = []

    if current is not None:
        alerts.append(
            Alert(
                watch_id=watch.id,
                kind="window_open",
                key=current.start.isoformat(),
                message=(
                    f"Janela de plantio ABERTA para {label}: "
                    f"de {_fmt(current.start)} a {_fmt(current.end)} "
                    f"(risco de perda de {window.risk_level}%)."
                ),
                details={"start": current.start.isoformat(), "end": current.end.isoformat()},
            )
        )
        days_left = days_between(current.end, today)
        if days_left <= rules.lead_days:
            alerts.append(
                Alert(
                    watch_id=watch.id,
                    kind="window_closing",
                    key=current.end.isoformat(),
                    message=(
                        f"A janela de plantio de {label} fecha em {days_left} dia(s), "
                        f"em {_fmt(current.end)}."
                    ),
                    details={"days_left": days_left},
                )
            )
    elif upcoming is not None:
        days_until = days_between(upcoming.start, today)
        if days_until <= rules.lead_days:
            alerts.append(
                Alert(
                    watch_id=watch.id,
                    kind="window_opening",
                    key=upcoming.start.isoformat(),
                    message=(
                        f"A janela de plantio de {label} abre em {days_until} dia(s), "
                        f"em {_fmt(upcoming.start)} (risco de perda de {window.risk_level}%)."
                    ),
                    details={"days_until": days_until},
                )
            )
    return alerts


def weather_alerts(
    watch: Watch,
    forecast: list[ForecastDay],
    today: date,
    rules: Rules,
    window_is_open: bool,
) -> list[Alert]:
    """Weather alerts for the next few days.

    Dry-spell alerts only make sense while planting is possible, so they are
    raised only when the window is open. Heavy-rain alerts are always raised.
    """
    upcoming = sorted(
        (f for f in forecast if f.day >= today), key=lambda f: f.day
    )[: rules.forecast_days]
    if not upcoming:
        return []

    label = f"{watch.name} ({watch.crop})"
    alerts: list[Alert] = []

    heavy = [f for f in upcoming if f.precipitation_mm >= rules.heavy_rain_mm]
    for f in heavy:
        alerts.append(
            Alert(
                watch_id=watch.id,
                kind="heavy_rain",
                key=f.day.isoformat(),
                message=(
                    f"Previsão de chuva forte em {label} no dia {_fmt(f.day)}: "
                    f"{f.precipitation_mm:.0f} mm."
                ),
                details={"mm": f.precipitation_mm},
            )
        )

    total = sum(f.precipitation_mm for f in upcoming)
    if window_is_open and total < rules.dry_spell_mm:
        alerts.append(
            Alert(
                watch_id=watch.id,
                kind="dry_spell",
                key=upcoming[0].day.isoformat(),
                message=(
                    f"Previsão de pouca chuva em {label}: {total:.0f} mm nos próximos "
                    f"{len(upcoming)} dias, com a janela de plantio aberta."
                ),
                details={"total_mm": total, "days": len(upcoming)},
            )
        )
    return alerts


def build_alerts(
    watch: Watch,
    windows: list[PlantingWindow],
    forecast: list[ForecastDay],
    today: date,
    rules: Rules,
) -> list[Alert]:
    """All alerts for one watch on ``today``."""
    alerts = window_alerts(watch, windows, today, rules)
    window_is_open = any(a.kind == "window_open" for a in alerts)
    alerts += weather_alerts(watch, forecast, today, rules, window_is_open)
    return alerts
