"""X (Twitter) API v2 poster using OAuth 1.0a.

Free tier: 17 posts per 24 hours per app/user.
Strategy: run 2 accounts -> 34 posts/day total, all free.

Each account needs its own developer app + credentials in .env:
  X_API_KEY_1, X_API_SECRET_1, X_ACCESS_TOKEN_1, X_ACCESS_TOKEN_SECRET_1
  X_API_KEY_2, X_API_SECRET_2, X_ACCESS_TOKEN_2, X_ACCESS_TOKEN_SECRET_2
"""

from __future__ import annotations

import hashlib
import hmac
import os
import time
import urllib.parse
import uuid
import logging
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger("x_poster")

TWEET_ENDPOINT = "https://api.twitter.com/2/tweets"
MAX_FREE_POSTS_PER_DAY = 17


@dataclass
class XCredentials:
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    label: str = "account"

    @property
    def is_configured(self) -> bool:
        return all([
            self.api_key, self.api_secret,
            self.access_token, self.access_token_secret,
        ])


def _percent_encode(s: str) -> str:
    return urllib.parse.quote(str(s), safe="")


def _build_oauth_header(
    method: str,
    url: str,
    creds: XCredentials,
    extra_params: Optional[dict] = None,
) -> str:
    """Build OAuth 1.0a Authorization header (HMAC-SHA1)."""
    oauth_params = {
        "oauth_consumer_key": creds.api_key,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": creds.access_token,
        "oauth_version": "1.0",
    }

    all_params = {**oauth_params, **(extra_params or {})}
    sorted_params = sorted(all_params.items(), key=lambda x: x[0])
    param_string = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}" for k, v in sorted_params
    )

    base = "&".join([
        _percent_encode(method.upper()),
        _percent_encode(url),
        _percent_encode(param_string),
    ])

    signing_key = f"{_percent_encode(creds.api_secret)}&{_percent_encode(creds.access_token_secret)}"
    signature = hmac.new(
        signing_key.encode("utf-8"),
        base.encode("utf-8"),
        "sha1",
    ).digest()

    import base64
    sig_b64 = base64.b64encode(signature).decode()
    oauth_params["oauth_signature"] = sig_b64

    header_parts = ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )
    return f"OAuth {header_parts}"


def post_tweet(text: str, creds: XCredentials) -> dict:
    """Post a single tweet. Returns dict with success, tweet_id, error."""
    if not creds.is_configured:
        return {"success": False, "error": "credentials_not_configured"}

    auth_header = _build_oauth_header("POST", TWEET_ENDPOINT, creds)

    try:
        resp = requests.post(
            TWEET_ENDPOINT,
            json={"text": text},
            headers={
                "Authorization": auth_header,
                "Content-Type": "application/json",
            },
            timeout=15,
        )

        if resp.status_code == 201:
            data = resp.json()
            tweet_id = data.get("data", {}).get("id", "")
            logger.info(f"[{creds.label}] Posted tweet {tweet_id}: {text[:60]}...")
            return {"success": True, "tweet_id": tweet_id}

        elif resp.status_code == 429:
            reset = resp.headers.get("x-rate-limit-reset", "unknown")
            logger.warning(f"[{creds.label}] Rate limited. Resets at: {reset}")
            return {"success": False, "error": "rate_limited", "reset_at": reset}

        else:
            body = resp.text[:300]
            logger.error(f"[{creds.label}] HTTP {resp.status_code}: {body}")
            return {"success": False, "error": f"http_{resp.status_code}", "body": body}

    except requests.RequestException as e:
        logger.error(f"[{creds.label}] Request error: {e}")
        return {"success": False, "error": str(e)}


def post_thread(tweets: list[str], creds: XCredentials) -> list[dict]:
    """Post a thread (reply chain). First tweet standalone, rest reply to previous."""
    if not tweets:
        return []

    results = []
    reply_to_id: Optional[str] = None

    for i, text in enumerate(tweets):
        if reply_to_id:
            auth_header = _build_oauth_header("POST", TWEET_ENDPOINT, creds)
            payload = {"text": text, "reply": {"in_reply_to_tweet_id": reply_to_id}}
        else:
            auth_header = _build_oauth_header("POST", TWEET_ENDPOINT, creds)
            payload = {"text": text}

        try:
            resp = requests.post(
                TWEET_ENDPOINT,
                json=payload,
                headers={
                    "Authorization": auth_header,
                    "Content-Type": "application/json",
                },
                timeout=15,
            )

            if resp.status_code == 201:
                tweet_id = resp.json().get("data", {}).get("id", "")
                results.append({"success": True, "tweet_id": tweet_id, "index": i})
                reply_to_id = tweet_id
                if i < len(tweets) - 1:
                    time.sleep(2)
            elif resp.status_code == 429:
                results.append({"success": False, "error": "rate_limited", "index": i})
                break
            else:
                results.append({"success": False, "error": f"http_{resp.status_code}", "index": i})
                break

        except requests.RequestException as e:
            results.append({"success": False, "error": str(e), "index": i})
            break

    return results


def load_credentials(suffix: str = "1") -> XCredentials:
    """Load credentials from environment variables for account N."""
    return XCredentials(
        api_key=os.getenv(f"X_API_KEY_{suffix}", ""),
        api_secret=os.getenv(f"X_API_SECRET_{suffix}", ""),
        access_token=os.getenv(f"X_ACCESS_TOKEN_{suffix}", ""),
        access_token_secret=os.getenv(f"X_ACCESS_TOKEN_SECRET_{suffix}", ""),
        label=f"account_{suffix}",
    )


def get_all_credentials() -> list[XCredentials]:
    """Load all configured X accounts (up to 5). Each gets 17 posts/day free."""
    creds_list = []
    for i in range(1, 6):
        c = load_credentials(str(i))
        if c.is_configured:
            creds_list.append(c)
    return creds_list
