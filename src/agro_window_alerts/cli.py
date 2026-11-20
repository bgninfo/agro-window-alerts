"""Command line entry point: ``agro-alerts``."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

from .config import ConfigError, load_config
from .notifiers.console import ConsoleNotifier
from .runner import run_check
from .sources.embrapa import EmbrapaSource, get_json
from .sources.sample import SampleSource
from .state import SentStore


def _check(args: argparse.Namespace) -> int:
    try:
        config = load_config(args.config)
    except (ConfigError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        if args.demo:
            source = SampleSource()
            notifier = ConsoleNotifier()
            store = SentStore(None)  # demo never remembers anything
        else:
            source = EmbrapaSource()
            if config.notifier == "whatsapp":
                from .notifiers.whatsapp import WhatsAppNotifier

                notifier = WhatsAppNotifier()
            else:
                notifier = ConsoleNotifier()
            store = SentStore(config.state_file)

        today = date.fromisoformat(args.today) if args.today else date.today()
        alerts = run_check(config, source, notifier, store, today, dry_run=args.dry_run)
    except (RuntimeError, NotImplementedError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.dry_run:
        for alert in alerts:
            print(f"[dry-run] {alert.message}")
    print(f"{len(alerts)} new alert(s) on {today.isoformat()}.")
    return 0


def _probe(args: argparse.Namespace) -> int:
    """Fetch a URL with your AgroAPI token and print the raw JSON.

    Use this to learn the real response format before writing a parser.
    """
    token = os.environ.get("AGROAPI_TOKEN", "")
    if not token:
        print("error: set AGROAPI_TOKEN first", file=sys.stderr)
        return 2
    print(json.dumps(get_json(args.url, token), indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="agro-alerts", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="run one monitoring pass")
    check.add_argument("--config", required=True, help="path to the TOML config")
    check.add_argument("--demo", action="store_true", help="use made-up sample data")
    check.add_argument("--dry-run", action="store_true", help="print alerts, send nothing")
    check.add_argument("--today", help="pretend today is YYYY-MM-DD (for testing)")
    check.set_defaults(func=_check)

    probe = sub.add_parser("probe", help="print the raw JSON of an AgroAPI URL")
    probe.add_argument("url", help="full URL, copied from the AgroAPI store")
    probe.set_defaults(func=_probe)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
