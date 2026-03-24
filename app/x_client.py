from __future__ import annotations

from dataclasses import dataclass

import requests
from requests_oauthlib import OAuth1


class XPostError(RuntimeError):
    """Raised when posting to X fails."""


@dataclass(frozen=True)
class XCredentials:
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str


class XClient:
    def __init__(self, credentials: XCredentials) -> None:
        self._auth = OAuth1(
            credentials.api_key,
            credentials.api_secret,
            credentials.access_token,
            credentials.access_token_secret,
        )

    def post(self, text: str) -> dict:
        response = requests.post(
            "https://api.x.com/2/tweets",
            auth=self._auth,
            json={"text": text},
            timeout=20,
        )
        if response.status_code not in (200, 201):
            raise XPostError(
                f"X API failed with {response.status_code}: {response.text.strip()}"
            )
        return response.json()
