from __future__ import annotations

import json
import logging
import random
import signal
from dataclasses import dataclass
from pathlib import Path
from typing import List

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import Settings
from .content import build_post_text
from .x_client import XClient


LOGGER = logging.getLogger(__name__)


@dataclass
class PostContext:
    settings: Settings
    templates: List[str]
    x_client: XClient | None
    state: dict


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def load_templates(settings: Settings) -> List[str]:
    if settings.posts_json:
        loaded = json.loads(settings.posts_json)
        templates = [item.strip() for item in loaded if item.strip()]
        if templates:
            return templates

    if not settings.posts_file.exists():
        raise FileNotFoundError(
            f"Posts file not found at '{settings.posts_file}'. "
            "Create it or set ASSISTANT_POSTS_JSON."
        )

    raw_lines = settings.posts_file.read_text(encoding="utf-8").splitlines()
    templates = [line.strip() for line in raw_lines if line.strip() and not line.startswith("#")]
    if not templates:
        raise ValueError("No post templates available. Add lines in posts file.")
    return templates


def load_state(state_file: Path) -> dict:
    if not state_file.exists():
        return {"next_index": 0}
    try:
        return json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        LOGGER.warning("State file is invalid JSON. Resetting state.")
        return {"next_index": 0}


def save_state(state_file: Path, state: dict) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def pick_template(context: PostContext) -> str:
    if context.settings.selection_mode == "random":
        return random.choice(context.templates)

    # Sequential mode remembers next index in state file.
    idx = int(context.state.get("next_index", 0))
    template = context.templates[idx % len(context.templates)]
    context.state["next_index"] = (idx + 1) % len(context.templates)
    save_state(context.settings.state_file, context.state)
    return template


def run_post_job(context: PostContext) -> None:
    template = pick_template(context)
    message = build_post_text(template)

    if len(message) > context.settings.max_post_length:
        LOGGER.warning(
            "Message length %s exceeds max %s. Truncating.",
            len(message),
            context.settings.max_post_length,
        )
        cap = max(context.settings.max_post_length, 3)
        message = (message[: cap - 3] + "...") if cap > 3 else message[:cap]

    if context.settings.is_live_mode:
        assert context.x_client is not None
        response = context.x_client.post(message)
        tweet_id = response.get("data", {}).get("id")
        LOGGER.info("Posted to X successfully. tweet_id=%s", tweet_id)
        return

    LOGGER.info("DRY RUN: would post to X: %s", message)


def build_context(settings: Settings) -> PostContext:
    templates = load_templates(settings)
    state = load_state(settings.state_file)
    x_client = None
    if settings.is_live_mode:
        from .x_client import XCredentials

        x_client = XClient(
            credentials=XCredentials(
                api_key=settings.x_api_key,
                api_secret=settings.x_api_key_secret,
                access_token=settings.x_access_token,
                access_token_secret=settings.x_access_token_secret,
            )
        )
    return PostContext(settings=settings, templates=templates, x_client=x_client, state=state)


def run_scheduler(settings: Settings) -> None:
    configure_logging(settings.log_level)
    context = build_context(settings)

    scheduler = BlockingScheduler(timezone=settings.timezone)
    for item in settings.schedule_times:
        hour, minute = item.split(":")
        scheduler.add_job(
            run_post_job,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            args=[context],
            id=f"post_{hour}_{minute}",
            replace_existing=True,
        )
        LOGGER.info("Scheduled daily post at %s (%s)", item, settings.timezone)

    def handle_signal(signum: int, _frame: object) -> None:
        LOGGER.info("Received signal %s. Shutting down scheduler.", signum)
        scheduler.shutdown(wait=False)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    if settings.run_once_on_start:
        LOGGER.info("Running one immediate startup post attempt.")
        run_post_job(context)
        if settings.exit_after_run_once:
            LOGGER.info("Exiting because ASSISTANT_EXIT_AFTER_RUN_ONCE=true.")
            return

    LOGGER.info("Starting scheduler in %s mode.", settings.post_mode)
    scheduler.start()
