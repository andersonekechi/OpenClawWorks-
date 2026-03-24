from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    post_mode: str
    log_level: str
    timezone: str
    schedule_times: List[str]
    posts_file: Path
    posts_json: str
    selection_mode: str
    state_file: Path
    max_post_length: int
    run_once_on_start: bool
    exit_after_run_once: bool
    x_api_key: str
    x_api_key_secret: str
    x_access_token: str
    x_access_token_secret: str

    @property
    def is_live_mode(self) -> bool:
        return self.post_mode.lower() == "live"


def _parse_bool(raw: str, var_name: str) -> bool:
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"{var_name} must be a boolean-like value (true/false).")


def _parse_schedule_times(raw: str) -> List[str]:
    times = [item.strip() for item in raw.split(",") if item.strip()]
    for t in times:
        parts = t.split(":")
        if len(parts) != 2:
            raise ValueError(f"Invalid schedule time '{t}'. Use HH:MM format.")
        hour, minute = parts
        if not hour.isdigit() or not minute.isdigit():
            raise ValueError(f"Invalid schedule time '{t}'. Use HH:MM format.")
        h = int(hour)
        m = int(minute)
        if h < 0 or h > 23 or m < 0 or m > 59:
            raise ValueError(f"Invalid schedule time '{t}'. Use 24-hour HH:MM format.")
    if not times:
        raise ValueError(
            "ASSISTANT_SCHEDULE_TIMES is empty. Add at least one HH:MM value."
        )
    return times


def _validate_json_posts(raw_json: str) -> None:
    if not raw_json.strip():
        return
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError("ASSISTANT_POSTS_JSON must be valid JSON.") from exc
    if not isinstance(parsed, list) or not all(isinstance(i, str) for i in parsed):
        raise ValueError("ASSISTANT_POSTS_JSON must be a JSON array of strings.")


def load_settings() -> Settings:
    load_dotenv()

    schedule_times = _parse_schedule_times(
        os.getenv("ASSISTANT_SCHEDULE_TIMES", "09:00,13:00,18:00")
    )

    post_mode = os.getenv("ASSISTANT_POST_MODE", "dry-run").strip().lower()
    if post_mode not in {"dry-run", "live"}:
        raise ValueError("ASSISTANT_POST_MODE must be either 'dry-run' or 'live'.")

    selection_mode = os.getenv("ASSISTANT_POST_SELECTION", "sequential").strip().lower()
    if selection_mode not in {"sequential", "random"}:
        raise ValueError("ASSISTANT_POST_SELECTION must be 'sequential' or 'random'.")

    posts_json = os.getenv("ASSISTANT_POSTS_JSON", "").strip()
    _validate_json_posts(posts_json)

    settings = Settings(
        post_mode=post_mode,
        log_level=os.getenv("ASSISTANT_LOG_LEVEL", "INFO").strip(),
        timezone=os.getenv("ASSISTANT_TIMEZONE", "UTC").strip(),
        schedule_times=schedule_times,
        posts_file=Path(os.getenv("ASSISTANT_POSTS_FILE", "posts.txt")).expanduser(),
        posts_json=posts_json,
        selection_mode=selection_mode,
        state_file=Path(os.getenv("ASSISTANT_STATE_FILE", ".assistant_state.json")).expanduser(),
        max_post_length=int(os.getenv("ASSISTANT_MAX_POST_LENGTH", "280")),
        run_once_on_start=_parse_bool(
            os.getenv("ASSISTANT_RUN_ONCE_ON_START", "false"),
            "ASSISTANT_RUN_ONCE_ON_START",
        ),
        exit_after_run_once=_parse_bool(
            os.getenv("ASSISTANT_EXIT_AFTER_RUN_ONCE", "false"),
            "ASSISTANT_EXIT_AFTER_RUN_ONCE",
        ),
        x_api_key=os.getenv("X_API_KEY", "").strip(),
        x_api_key_secret=os.getenv("X_API_KEY_SECRET", "").strip(),
        x_access_token=os.getenv("X_ACCESS_TOKEN", "").strip(),
        x_access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET", "").strip(),
    )

    if settings.max_post_length < 1:
        raise ValueError("ASSISTANT_MAX_POST_LENGTH must be greater than 0.")

    if settings.is_live_mode:
        required = {
            "X_API_KEY": settings.x_api_key,
            "X_API_KEY_SECRET": settings.x_api_key_secret,
            "X_ACCESS_TOKEN": settings.x_access_token,
            "X_ACCESS_TOKEN_SECRET": settings.x_access_token_secret,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            missing_display = ", ".join(missing)
            raise ValueError(
                f"Live mode requires credentials. Missing: {missing_display}"
            )

    return settings
