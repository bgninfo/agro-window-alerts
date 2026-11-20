"""Print alerts to the terminal. The default, safe for trying things out."""

from __future__ import annotations


class ConsoleNotifier:
    def send(self, recipient: str, text: str) -> None:
        print(f"[to {recipient or 'console'}] {text}")
