"""Load the TOML configuration file."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .engine import Rules
from .models import Watch


class ConfigError(ValueError):
    """The configuration file is missing something required."""


@dataclass(frozen=True)
class Config:
    rules: Rules
    watches: list[Watch]
    state_file: str | None = None
    notifier: str = "console"
    extra: dict = field(default_factory=dict)


def load_config(path: str | Path) -> Config:
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))

    settings = data.get("settings", {})
    rules = Rules(
        **{
            key: settings[key]
            for key in Rules.__dataclass_fields__
            if key in settings
        }
    )

    watches: list[Watch] = []
    for i, raw in enumerate(data.get("watch", []), start=1):
        missing = [
            k
            for k in ("id", "name", "crop", "municipality_ibge", "latitude", "longitude")
            if k not in raw
        ]
        if missing:
            raise ConfigError(f"[[watch]] #{i} is missing: {', '.join(missing)}")
        watches.append(
            Watch(
                id=raw["id"],
                name=raw["name"],
                crop=raw["crop"],
                municipality_ibge=int(raw["municipality_ibge"]),
                latitude=float(raw["latitude"]),
                longitude=float(raw["longitude"]),
                agritec_crop_id=raw.get("agritec_crop_id"),
                recipients=tuple(raw.get("recipients", [])),
            )
        )
    if not watches:
        raise ConfigError("define at least one [[watch]] block")

    notifier = settings.get("notifier", "console")
    if notifier not in ("console", "whatsapp"):
        raise ConfigError(f"unknown notifier '{notifier}' (use 'console' or 'whatsapp')")
    if notifier == "whatsapp":
        silent = [w.id for w in watches if not w.recipients]
        if silent:
            raise ConfigError(f"watch(es) without recipients: {', '.join(silent)}")

    return Config(
        rules=rules,
        watches=watches,
        state_file=settings.get("state_file"),
        notifier=notifier,
    )
