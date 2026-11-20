"""Remember which alerts were already sent, so nobody gets the same one twice."""

from __future__ import annotations

import json
from pathlib import Path


class SentStore:
    """A small JSON file holding the ids of alerts already delivered."""

    def __init__(self, path: str | Path | None):
        self._path = Path(path) if path else None
        self._sent: set[str] = set()
        if self._path and self._path.exists():
            self._sent = set(json.loads(self._path.read_text(encoding="utf-8")))

    def was_sent(self, dedupe_id: str) -> bool:
        return dedupe_id in self._sent

    def mark_sent(self, dedupe_id: str) -> None:
        self._sent.add(dedupe_id)

    def save(self) -> None:
        if self._path is None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(sorted(self._sent), indent=2), encoding="utf-8"
        )
