from datetime import date, timedelta

from agro_window_alerts.engine import Rules, build_alerts, weather_alerts, window_alerts
from agro_window_alerts.models import ForecastDay, PlantingWindow, Watch

WATCH = Watch("w1", "Fazenda Teste", "soja", 5107925, -12.5, -55.7)
WINDOW = PlantingWindow("soja", 20, frozenset({28, 29, 30}))  # 1 Oct - 31 Oct
RULES = Rules(lead_days=7)


def kinds(alerts):
    return sorted(a.kind for a in alerts)


def test_no_alert_when_window_is_far_away():
    assert window_alerts(WATCH, [WINDOW], date(2026, 8, 1), RULES) == []


def test_window_opening_soon():
    alerts = window_alerts(WATCH, [WINDOW], date(2026, 9, 27), RULES)
    assert kinds(alerts) == ["window_opening"]
    assert alerts[0].key == "2026-10-01"
    assert "abre em 4 dia(s)" in alerts[0].message


def test_window_open_mid_period():
    alerts = window_alerts(WATCH, [WINDOW], date(2026, 10, 12), RULES)
    assert kinds(alerts) == ["window_open"]


def test_window_closing_soon_also_reports_open():
    alerts = window_alerts(WATCH, [WINDOW], date(2026, 10, 28), RULES)
    assert kinds(alerts) == ["window_closing", "window_open"]
    closing = next(a for a in alerts if a.kind == "window_closing")
    assert closing.details["days_left"] == 3


def test_ignores_windows_of_other_risk_levels():
    other = PlantingWindow("soja", 40, frozenset({28, 29, 30}))
    assert window_alerts(WATCH, [other], date(2026, 10, 12), RULES) == []


def test_same_occurrence_has_same_dedupe_id():
    a = window_alerts(WATCH, [WINDOW], date(2026, 10, 2), RULES)[0]
    b = window_alerts(WATCH, [WINDOW], date(2026, 10, 9), RULES)[0]
    assert a.dedupe_id == b.dedupe_id  # one alert per window, not one per day


def _forecast(today, mm_values):
    return [ForecastDay(today + timedelta(days=i), mm) for i, mm in enumerate(mm_values)]


def test_heavy_rain_alert():
    today = date(2026, 10, 12)
    alerts = weather_alerts(WATCH, _forecast(today, [0, 0, 60, 0, 0]), today, RULES, False)
    assert kinds(alerts) == ["heavy_rain"]
    assert alerts[0].key == "2026-10-14"


def test_dry_spell_only_when_window_open():
    today = date(2026, 10, 12)
    dry = _forecast(today, [0, 1, 0, 2, 0])
    assert kinds(weather_alerts(WATCH, dry, today, RULES, True)) == ["dry_spell"]
    assert weather_alerts(WATCH, dry, today, RULES, False) == []


def test_no_dry_spell_when_enough_rain():
    today = date(2026, 10, 12)
    wet = _forecast(today, [5, 5, 5, 5, 5])
    assert weather_alerts(WATCH, wet, today, RULES, True) == []


def test_forecast_limited_to_configured_days():
    today = date(2026, 10, 12)
    # heavy rain on day 6 is outside the 5-day horizon
    alerts = weather_alerts(WATCH, _forecast(today, [10, 10, 10, 10, 10, 90]), today, RULES, True)
    assert alerts == []


def test_empty_forecast_gives_no_weather_alerts():
    assert weather_alerts(WATCH, [], date(2026, 10, 12), RULES, True) == []


def test_build_alerts_combines_window_and_weather():
    today = date(2026, 10, 12)
    alerts = build_alerts(WATCH, [WINDOW], _forecast(today, [0, 0, 70, 0, 0]), today, RULES)
    # 70 mm in total is not a dry spell, but one day is above the heavy-rain limit
    assert kinds(alerts) == ["heavy_rain", "window_open"]
