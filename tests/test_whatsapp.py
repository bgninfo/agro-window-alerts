import pytest

from agro_window_alerts.notifiers.whatsapp import (
    WhatsAppNotifier,
    build_payload,
    clean_template_text,
)


def test_clean_template_text_removes_newlines_tabs_and_long_spaces():
    assert clean_template_text("a\nb\t\tc   d") == "a b c d"


def test_build_payload_shape():
    payload = build_payload("5511900000000", "Olá\nmundo", "alerta_plantio", "pt_BR")
    assert payload["to"] == "5511900000000"
    assert payload["type"] == "template"
    assert payload["template"]["name"] == "alerta_plantio"
    assert payload["template"]["language"] == {"code": "pt_BR"}
    param = payload["template"]["components"][0]["parameters"][0]
    assert param == {"type": "text", "text": "Olá mundo"}


def test_notifier_requires_credentials(monkeypatch):
    for name in ("WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_TEMPLATE_NAME"):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError):
        WhatsAppNotifier()


def test_notifier_posts_to_graph_api(monkeypatch):
    monkeypatch.setenv("WHATSAPP_TOKEN", "secret-token")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "12345")
    monkeypatch.setenv("WHATSAPP_TEMPLATE_NAME", "alerta_plantio")
    monkeypatch.setenv("WHATSAPP_API_VERSION", "v21.0")

    calls = []
    notifier = WhatsAppNotifier(post=lambda url, headers, payload: calls.append((url, headers, payload)))
    notifier.send("5511900000000", "teste")

    url, headers, payload = calls[0]
    assert url == "https://graph.facebook.com/v21.0/12345/messages"
    assert headers == {"Authorization": "Bearer secret-token"}
    assert payload["template"]["components"][0]["parameters"][0]["text"] == "teste"
