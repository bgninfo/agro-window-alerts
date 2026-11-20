"""AWS Lambda entry point. Trigger it daily with an Amazon EventBridge schedule.

Environment variables:
    CONFIG_PATH   path to the TOML config packaged with the function
                  (default: config.toml)
    plus the AGROAPI_* and WHATSAPP_* variables described in .env.example

Note: the "already sent" file lives in /tmp, which Lambda does not keep between
cold starts. Moving that state to S3 or DynamoDB is a good first contribution.
"""

from __future__ import annotations

import os
from datetime import date

from .config import load_config
from .notifiers.console import ConsoleNotifier
from .runner import run_check
from .sources.embrapa import EmbrapaSource
from .state import SentStore


def handler(event, context):
    config = load_config(os.environ.get("CONFIG_PATH", "config.toml"))

    if config.notifier == "whatsapp":
        from .notifiers.whatsapp import WhatsAppNotifier

        notifier = WhatsAppNotifier()
    else:
        notifier = ConsoleNotifier()

    store = SentStore("/tmp/agro-alerts-sent.json")
    alerts = run_check(config, EmbrapaSource(), notifier, store, date.today())
    return {"new_alerts": len(alerts)}
