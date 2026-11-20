"""Send alerts through the official WhatsApp Business Cloud API (Meta).

Messages that a business starts must use a template approved by Meta, so this
notifier sends a template with the alert text as its single body variable.
Create a template with one {{1}} variable in the Meta Business Manager and put
its name in WHATSAPP_TEMPLATE_NAME.

Environment variables (never committed):
    WHATSAPP_TOKEN             access token
    WHATSAPP_PHONE_NUMBER_ID   id of the sending phone number
    WHATSAPP_TEMPLATE_NAME     approved template name
    WHATSAPP_TEMPLATE_LANG     template language code, default pt_BR
    WHATSAPP_API_VERSION       Graph API version, default v21.0 (update as Meta retires versions)
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from collections.abc import Callable

PostFn = Callable[[str, dict, dict], None]


def clean_template_text(text: str) -> str:
    """Meta rejects newlines, tabs and long runs of spaces in template variables."""
    text = re.sub(r"[\r\n\t]+", " ", text)
    return re.sub(r" {2,}", " ", text).strip()


def build_payload(recipient: str, text: str, template: str, language: str) -> dict:
    return {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "template",
        "template": {
            "name": template,
            "language": {"code": language},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": clean_template_text(text)}],
                }
            ],
        },
    }


def _post_json(url: str, headers: dict, payload: dict) -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30):  # noqa: S310
        pass


class WhatsAppNotifier:
    def __init__(self, post: PostFn = _post_json):
        self._token = os.environ.get("WHATSAPP_TOKEN", "")
        self._phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
        self._template = os.environ.get("WHATSAPP_TEMPLATE_NAME", "")
        self._language = os.environ.get("WHATSAPP_TEMPLATE_LANG", "pt_BR")
        self._version = os.environ.get("WHATSAPP_API_VERSION", "v21.0")
        self._post = post
        if not (self._token and self._phone_number_id and self._template):
            raise RuntimeError(
                "Set WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID and "
                "WHATSAPP_TEMPLATE_NAME (see .env.example)."
            )

    def send(self, recipient: str, text: str) -> None:
        url = f"https://graph.facebook.com/{self._version}/{self._phone_number_id}/messages"
        payload = build_payload(recipient, text, self._template, self._language)
        self._post(url, {"Authorization": f"Bearer {self._token}"}, payload)
