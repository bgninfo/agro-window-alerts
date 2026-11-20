"""Ways to deliver an alert."""

from __future__ import annotations

from typing import Protocol


class Notifier(Protocol):
    def send(self, recipient: str, text: str) -> None: ...
