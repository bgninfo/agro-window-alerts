from datetime import date

import pytest

from agro_window_alerts.config import ConfigError, load_config
from agro_window_alerts.runner import run_check
from agro_window_alerts.sources.sample import SampleSource
from agro_window_alerts.state import SentStore

CONFIG = """
[settings]
notifier = "{notifier}"
lead_days = 7

[[watch]]
id = "w1"
name = "Fazenda Teste"
crop = "soja"
municipality_ibge = 5107925
latitude = -12.5
longitude = -55.7
{recipients}
"""


class FakeNotifier:
    def __init__(self):
        self.sent = []

    def send(self, recipient, text):
        self.sent.append((recipient, text))


def write_config(tmp_path, notifier="console", recipients=""):
    path = tmp_path / "config.toml"
    path.write_text(CONFIG.format(notifier=notifier, recipients=recipients), encoding="utf-8")
    return path


def test_load_config_reads_watch_and_rules(tmp_path):
    config = load_config(write_config(tmp_path))
    assert config.rules.lead_days == 7
    assert config.watches[0].municipality_ibge == 5107925
    assert config.notifier == "console"


def test_load_config_requires_a_watch(tmp_path):
    path = tmp_path / "empty.toml"
    path.write_text("[settings]\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_config(path)


def test_load_config_reports_missing_field(tmp_path):
    path = tmp_path / "bad.toml"
    path.write_text('[[watch]]\nid = "x"\n', encoding="utf-8")
    with pytest.raises(ConfigError, match="missing"):
        load_config(path)


def test_whatsapp_requires_recipients(tmp_path):
    with pytest.raises(ConfigError, match="recipients"):
        load_config(write_config(tmp_path, notifier="whatsapp"))


def test_unknown_notifier_is_rejected(tmp_path):
    with pytest.raises(ConfigError, match="unknown notifier"):
        load_config(write_config(tmp_path, notifier="sms"))


def test_run_check_sends_once_and_remembers(tmp_path):
    config = load_config(write_config(tmp_path, recipients='recipients = ["5511900000000"]'))
    notifier = FakeNotifier()
    state_path = tmp_path / "sent.json"
    today = date(2026, 10, 12)  # inside the sample window

    first = run_check(config, SampleSource(), notifier, SentStore(state_path), today)
    sent_after_first = len(notifier.sent)
    assert first and sent_after_first == len(first)
    assert all(r == "5511900000000" for r, _ in notifier.sent)

    second = run_check(config, SampleSource(), notifier, SentStore(state_path), today)
    assert second == []  # nothing new, nothing sent again
    assert len(notifier.sent) == sent_after_first


def test_dry_run_sends_nothing_and_remembers_nothing(tmp_path):
    config = load_config(write_config(tmp_path, recipients='recipients = ["5511900000000"]'))
    notifier = FakeNotifier()
    state_path = tmp_path / "sent.json"

    alerts = run_check(
        config, SampleSource(), notifier, SentStore(state_path), date(2026, 10, 12), dry_run=True
    )
    assert alerts
    assert notifier.sent == []
    assert not state_path.exists()


def test_store_round_trip(tmp_path):
    path = tmp_path / "nested" / "sent.json"
    store = SentStore(path)
    assert not store.was_sent("a")
    store.mark_sent("a")
    store.save()
    assert SentStore(path).was_sent("a")
