"""Auto-scheduler: posts from BaceHelpr DB to X automatically.

Free tier math:
  - Each X account gets 17 posts/24h free
  - 2 accounts = 34 posts/day
  - Posts spaced every ~42 minutes (24h / 34 posts)

The scheduler pulls the highest-scored unposted content,
rotates between accounts to stay within rate limits,
and marks each post as acted_on in the DB.

Runs as an async task inside bot.py.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone

from scanner.storage import PostStore
from scanner.templates import generate_tweet
from x_poster import post_tweet, post_thread, get_all_credentials, MAX_FREE_POSTS_PER_DAY

logger = logging.getLogger("auto_scheduler")

# How many posts per day (per account)
POSTS_PER_ACCOUNT_PER_DAY = MAX_FREE_POSTS_PER_DAY  # 17

# Minimum gap between posts (seconds) — distributed across 24h
# For 2 accounts posting 17 each = 34 posts spread over 86400s = 2541s gap
# We use a slightly larger gap to stay safe
POST_INTERVAL_SECONDS = int(86400 / (POSTS_PER_ACCOUNT_PER_DAY * 2)) + 60  # ~42 min

# State file to track daily post counts per account
STATE_FILE = "auto_post_state.json"

# Control flags (modified by Telegram commands)
_auto_posting_enabled: bool = False
_notify_chat_id: str = ""


def set_auto_posting(enabled: bool, chat_id: str = "") -> None:
    global _auto_posting_enabled, _notify_chat_id
    _auto_posting_enabled = enabled
    if chat_id:
        _notify_chat_id = chat_id
    logger.info(f"Auto-posting {'ENABLED' if enabled else 'DISABLED'}")


def is_auto_posting_enabled() -> bool:
    return _auto_posting_enabled


def _load_state() -> dict:
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_state(state: dict) -> None:
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        logger.error(f"Could not save state: {e}")


def _get_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _account_posts_today(state: dict, label: str) -> int:
    today = _get_today()
    return state.get(today, {}).get(label, 0)


def _increment_account_count(state: dict, label: str) -> dict:
    today = _get_today()
    if today not in state:
        # clean up old dates
        state = {today: {}}
    state[today][label] = state[today].get(label, 0) + 1
    return state


def _pick_next_account(creds_list, state: dict):
    """Pick the account with the fewest posts today that's under the limit."""
    for creds in creds_list:
        count = _account_posts_today(state, creds.label)
        if count < POSTS_PER_ACCOUNT_PER_DAY:
            return creds
    return None


def _get_next_post(store: PostStore) -> dict | None:
    """Get the best unposted post from the DB."""
    posts = store.get_latest_posts(limit=5, exclude_posted=True)
    if posts:
        # Prefer highest match_score
        return max(posts, key=lambda p: p.get("match_score", 0))
    return None


def _get_next_article(store: PostStore) -> dict | None:
    """Get the next unposted article thread."""
    articles = store.get_latest_articles(limit=1, exclude_posted=True)
    return articles[0] if articles else None


async def run_auto_poster(bot=None) -> None:
    """Main loop: posts to X every ~42 minutes when enabled."""
    logger.info(f"Auto-poster started. Interval: {POST_INTERVAL_SECONDS}s")

    creds_list = get_all_credentials()
    if not creds_list:
        logger.warning("No X credentials configured. Auto-posting disabled.")
        return

    logger.info(f"Loaded {len(creds_list)} X account(s): {[c.label for c in creds_list]}")
    logger.info(f"Max posts/day: {len(creds_list) * POSTS_PER_ACCOUNT_PER_DAY}")

    # Alternate between single posts and article threads
    # Pattern: 3 single posts, then 1 article thread, repeat
    post_cycle = 0

    while True:
        await asyncio.sleep(POST_INTERVAL_SECONDS)

        if not _auto_posting_enabled:
            continue

        creds_list = get_all_credentials()
        if not creds_list:
            continue

        state = _load_state()
        creds = _pick_next_account(creds_list, state)

        if creds is None:
            logger.info("All accounts hit daily limit. Waiting for reset.")
            continue

        store = PostStore()
        post_cycle += 1

        # Every 4th cycle, post an article thread; otherwise single tweet
        if post_cycle % 4 == 0:
            article = _get_next_article(store)
            if article:
                try:
                    tweets = json.loads(article["thread_json"])
                    # Strip "Show more..." suffix for API
                    tweets = [t.replace("\n\nShow more...", "").strip() for t in tweets]
                    # Ensure each tweet is within 280 chars
                    tweets = [t[:277] + "..." if len(t) > 280 else t for t in tweets]

                    logger.info(f"Posting article thread: {article['title'][:60]} ({len(tweets)} tweets)")
                    results = await asyncio.to_thread(post_thread, tweets, creds)
                    success_count = sum(1 for r in results if r.get("success"))

                    if success_count > 0:
                        store.mark_article_posted(article["id"])
                        state = _increment_account_count(state, creds.label)
                        _save_state(state)
                        logger.info(f"Thread posted: {success_count}/{len(tweets)} tweets")

                        if bot and _notify_chat_id:
                            await bot.send_message(
                                chat_id=_notify_chat_id,
                                text=f"Auto-posted thread: <b>{article['title'][:80]}</b>\n{success_count}/{len(tweets)} tweets via {creds.label}",
                                parse_mode="HTML",
                                disable_web_page_preview=True,
                            )
                except Exception as e:
                    logger.error(f"Thread post error: {e}")
                continue

        # Single post
        post = _get_next_post(store)
        if not post:
            logger.info("No unposted content available. Waiting for next scan.")
            continue

        try:
            tweet_text = generate_tweet(post)
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."

            result = await asyncio.to_thread(post_tweet, tweet_text, creds)

            if result.get("success"):
                store.mark_posted(post["id"])
                state = _increment_account_count(state, creds.label)
                _save_state(state)

                today_count = _account_posts_today(state, creds.label)
                total_today = sum(_account_posts_today(state, c.label) for c in creds_list)
                logger.info(
                    f"Posted via {creds.label} ({today_count}/{POSTS_PER_ACCOUNT_PER_DAY} today) | "
                    f"Total today: {total_today}"
                )

                if bot and _notify_chat_id:
                    await bot.send_message(
                        chat_id=_notify_chat_id,
                        text=(
                            f"Auto-posted: <b>{post['title'][:80]}</b>\n"
                            f"Account: {creds.label} | Today: {total_today}/{len(creds_list)*POSTS_PER_ACCOUNT_PER_DAY}"
                        ),
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                    )

            elif result.get("error") == "rate_limited":
                logger.warning(f"Rate limited on {creds.label}")

        except Exception as e:
            logger.error(f"Auto-post error: {e}")


def get_status(creds_list=None) -> dict:
    """Return current auto-posting status for display in Telegram."""
    if creds_list is None:
        creds_list = get_all_credentials()

    state = _load_state()
    today = _get_today()

    account_status = []
    total_today = 0
    for creds in creds_list:
        count = _account_posts_today(state, creds.label)
        total_today += count
        remaining = POSTS_PER_ACCOUNT_PER_DAY - count
        account_status.append({
            "label": creds.label,
            "posted_today": count,
            "remaining_today": remaining,
        })

    max_per_day = len(creds_list) * POSTS_PER_ACCOUNT_PER_DAY

    return {
        "enabled": _auto_posting_enabled,
        "accounts_configured": len(creds_list),
        "max_posts_per_day": max_per_day,
        "posted_today": total_today,
        "remaining_today": max_per_day - total_today,
        "interval_minutes": POST_INTERVAL_SECONDS // 60,
        "accounts": account_status,
        "date": today,
    }
