from pathlib import Path

from agro_window_alerts.cli import main

EXAMPLE = str(Path(__file__).parent.parent / "examples" / "config.example.toml")


def test_demo_runs_and_reports_alerts(capsys):
    code = main(["check", "--config", EXAMPLE, "--demo", "--today", "2026-10-12"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Janela de plantio ABERTA" in out
    assert "4 new alert(s)" in out


def test_live_mode_without_credentials_fails_cleanly(monkeypatch, capsys):
    for name in ("AGROAPI_TOKEN", "AGROAPI_AGRITEC_URL", "AGROAPI_CLIMAPI_URL"):
        monkeypatch.delenv(name, raising=False)
    code = main(["check", "--config", EXAMPLE])
    err = capsys.readouterr().err
    assert code == 2
    assert "AGROAPI_TOKEN" in err


def test_missing_config_file_fails_cleanly(capsys):
    code = main(["check", "--config", "does-not-exist.toml", "--demo"])
    assert code == 2
    assert "error:" in capsys.readouterr().err
