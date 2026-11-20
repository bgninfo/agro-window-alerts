"""Live data from Embrapa's AgroAPI (Agritec and ClimAPI).

STATUS: only the HTTP helper exists. The public documentation does not give the
Agritec endpoint, nor the JSON returned by Agritec or ClimAPI, so the fetching and
parsing code must be written against real responses. Use ``agro-alerts probe``
with your own token to see them, then implement ``planting_windows``,
``forecast``, ``parse_agritec_windows`` and ``parse_climapi_forecast``.
See the open issues.

Configuration (environment variables, never committed):
    AGROAPI_TOKEN          access token generated in the AgroAPI store
    AGROAPI_AGRITEC_URL    base URL of the Agritec API, as shown in the store
    AGROAPI_CLIMAPI_URL    base URL of the ClimAPI, as shown in the store
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import date

from ..models import ForecastDay, PlantingWindow, Watch


def get_json(url: str, token: str, timeout: float = 30.0):
    """GET ``url`` with a bearer token and return the decoded JSON."""
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return json.loads(response.read().decode("utf-8"))


def parse_agritec_windows(payload, watch: Watch) -> list[PlantingWindow]:
    raise NotImplementedError(
        "Agritec response parsing is not implemented yet: run `agro-alerts probe` "
        "with a real token and implement this against the actual JSON."
    )


def parse_climapi_forecast(payload, watch: Watch) -> list[ForecastDay]:
    raise NotImplementedError(
        "ClimAPI response parsing is not implemented yet: run `agro-alerts probe` "
        "with a real token and implement this against the actual JSON."
    )


class EmbrapaSource:
    """Reads planting windows from Agritec and forecasts from ClimAPI."""

    def __init__(self, token: str | None = None):
        self._token = token or os.environ.get("AGROAPI_TOKEN", "")
        self._agritec_url = os.environ.get("AGROAPI_AGRITEC_URL", "").rstrip("/")
        self._climapi_url = os.environ.get("AGROAPI_CLIMAPI_URL", "").rstrip("/")
        if not (self._token and self._agritec_url and self._climapi_url):
            raise RuntimeError(
                "Set AGROAPI_TOKEN, AGROAPI_AGRITEC_URL and AGROAPI_CLIMAPI_URL "
                "(see .env.example), or run with --demo."
            )

    def planting_windows(self, watch: Watch) -> list[PlantingWindow]:
        if watch.agritec_crop_id is None:
            raise RuntimeError(f"watch '{watch.id}' needs agritec_crop_id")
        # The Agritec endpoint path and parameter names are not in the public
        # documentation. Find them in the Swagger page of the AgroAPI store,
        # check them with `agro-alerts probe`, then build the URL here and pass
        # the response to parse_agritec_windows().
        raise NotImplementedError(
            "Fetching Agritec planting windows is not implemented yet: confirm "
            "the endpoint and parameters in the AgroAPI store."
        )

    def forecast(self, watch: Watch, today: date) -> list[ForecastDay]:
        # Endpoint shape from the ClimAPI documentation:
        # /ncep-gfs/{variavel}/{data}/{longitude}/{latitude}
        # The variable name and date format must be confirmed with a real token.
        raise NotImplementedError(
            "Fetching the forecast is not implemented yet: confirm the variable "
            "name and date format with `agro-alerts probe`."
        )
