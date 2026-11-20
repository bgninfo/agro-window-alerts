"""Run one monitoring pass: fetch data, build alerts, deliver the new ones."""

from __future__ import annotations

from datetime import date

from .config import Config
from .engine import build_alerts
from .models import Alert
from .notifiers import Notifier
from .sources import DataSource
from .state import SentStore


def run_check(
    config: Config,
    source: DataSource,
    notifier: Notifier,
    store: SentStore,
    today: date,
    dry_run: bool = False,
) -> list[Alert]:
    """Return the alerts that were new on ``today`` and (unless dry-run) send them."""
    new_alerts: list[Alert] = []

    for watch in config.watches:
        windows = source.planting_windows(watch)
        forecast = source.forecast(watch, today)
        for alert in build_alerts(watch, windows, forecast, today, config.rules):
            if store.was_sent(alert.dedupe_id):
                continue
            new_alerts.append(alert)
            if dry_run:
                continue
            # With no recipients configured, fall back to the console so nothing is lost.
            for recipient in watch.recipients or ("",):
                notifier.send(recipient, alert.message)
            store.mark_sent(alert.dedupe_id)

    if not dry_run:
        store.save()
    return new_alerts
