"""X (Twitter) API v2 poster using pure OAuth 1.0a.

Free tier: 17 posts per 24 hours per developer app.
Strategy: 2 accounts x 17 = 34 posts/day FREE.

Key design decisions:
- Thread = tweet 1 posted standalone, tweets 2-N posted as replies to the
  previous tweet in the chain. This is the "reply chain" pattern that forces
  users to click "Show more" / navigate replies, maximising impressions.
- No external OAuth libraries - uses only stdlib + requests.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import time
import urllib.parse
import uuid
from dataclasses import dataclass
from typing import Optional

import requests

logger = logging.getLogger("x_poster")

TWEET_ENDPOINT = "https://api.twitter.com/2/tweets"
VERIFY_ENDPOINT = "https://api.twitter.com/2/users/me"
MAX_FREE_POSTS_PER_DAY = 17
MAX_TWEET_LEN = 280


@dataclass
class XCredentials:
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    label: str = "account_1"

    @property
    def is_configured(self) -> bool:
        return all([
            self.api_key.strip(), self.api_secret.strip(),
            self.access_token.strip(), self.access_token_secret.strip(),
        ])


def _percent_encode(s: str) -> str:
    return urllib.parse.quote(str(s), safe="")


def _oauth_header(method: str, url: str, creds: XCredentials, body_params: dict | None = None) -> str:
    """Build OAuth 1.0a Authorization header (HMAC-SHA1)."""
    oauth = {
        "oauth_consumer_key": creds.api_key,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": creds.access_token,
        "oauth_version": "1.0",
    }

    all_params = {**oauth, **(body_params or {})}
    param_str = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}"
        for k, v in sorted(all_params.items())
    )

    base_str = "&".join([
        _percent_encode(method.upper()),
        _percent_encode(url),
        _percent_encode(param_str),
    ])

    signing_key = f"{_percent_encode(creds.api_secret)}&{_percent_encode(creds.access_token_secret)}"
    sig = base64.b64encode(
        hmac.new(signing_key.encode(), base_str.encode(), "sha1").digest()
    ).decode()
    oauth["oauth_signature"] = sig

    return "OAuth " + ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"'
        for k, v in sorted(oauth.items())
    )


def verify_credentials(creds: XCredentials) -> dict:
    """Test that credentials work. Returns {success, username, error}."""
    if not creds.is_configured:
        return {"success": False, "error": "not_configured"}
    try:
        auth = _oauth_header("GET", VERIFY_ENDPOINT, creds)
        resp = requests.get(
            VERIFY_ENDPOINT,
            headers={"Authorization": auth},
            params={"user.fields": "username"},
            timeout=10,
        )
        if resp.status_code == 200:
            username = resp.json().get("data", {}).get("username", "unknown")
            return {"success": True, "username": username}
        return {"success": False, "error": f"http_{resp.status_code}", "body": resp.text[:200]}
    except Exception as e:
        return {"success": False, "error": str(e)}


def post_tweet(text: str, creds: XCredentials, reply_to_id: str | None = None) -> dict:
    """Post a single tweet. Optionally as reply to reply_to_id."""
    if not creds.is_configured:
        return {"success": False, "error": "credentials_not_configured"}

    payload: dict = {"text": text[:MAX_TWEET_LEN]}
    if reply_to_id:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to_id}

    auth = _oauth_header("POST", TWEET_ENDPOINT, creds)

    try:
        resp = requests.post(
            TWEET_ENDPOINT,
            json=payload,
            headers={"Authorization": auth, "Content-Type": "application/json"},
            timeout=15,
        )
        if resp.status_code == 201:
            tweet_id = resp.json().get("data", {}).get("id", "")
            logger.info(f"[{creds.label}] Tweet {tweet_id}: {text[:50]}...")
            return {"success": True, "tweet_id": tweet_id}
        elif resp.status_code == 429:
            reset = resp.headers.get("x-rate-limit-reset", "unknown")
            logger.warning(f"[{creds.label}] Rate limited. Resets: {reset}")
            return {"success": False, "error": "rate_limited", "reset_at": reset}
        else:
            logger.error(f"[{creds.label}] HTTP {resp.status_code}: {resp.text[:200]}")
            return {"success": False, "error": f"http_{resp.status_code}", "body": resp.text[:200]}
    except requests.RequestException as e:
        logger.error(f"[{creds.label}] Request error: {e}")
        return {"success": False, "error": str(e)}


def post_thread(tweets: list[str], creds: XCredentials) -> list[dict]:
    """Post a thread as a reply chain.

    Tweet 1 is posted standalone (appears in feed/timeline).
    Tweets 2-N are posted as replies to the previous tweet.
    This forces users to interact (click 'Show replies') which
    boosts engagement signals and drives profile visits.

    Returns list of result dicts with success/tweet_id per tweet.
    """
    if not tweets:
        return []

    results = []
    prev_id: str | None = None

    for i, text in enumerate(tweets):
        result = post_tweet(text, creds, reply_to_id=prev_id)
        result["index"] = i
        results.append(result)

        if result["success"]:
            prev_id = result["tweet_id"]
            if i < len(tweets) - 1:
                time.sleep(2)  # small gap between thread replies
        else:
            logger.error(f"Thread failed at tweet {i}: {result}")
            break  # stop posting remainder if one fails

    return results


def load_credentials(suffix: str = "1") -> XCredentials:
    return XCredentials(
        api_key=os.getenv(f"X_API_KEY_{suffix}", ""),
        api_secret=os.getenv(f"X_API_SECRET_{suffix}", ""),
        access_token=os.getenv(f"X_ACCESS_TOKEN_{suffix}", ""),
        access_token_secret=os.getenv(f"X_ACCESS_TOKEN_SECRET_{suffix}", ""),
        label=f"account_{suffix}",
    )


def get_all_credentials() -> list[XCredentials]:
    """Load all configured X accounts (checks up to 5 suffixes)."""
    return [
        load_credentials(str(i))
        for i in range(1, 6)
        if load_credentials(str(i)).is_configured
    ]
