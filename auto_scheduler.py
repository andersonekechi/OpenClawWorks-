"""Auto-scheduler: posts BaceHelpr content to X automatically.

FREE tier strategy (official X API docs):
  - Each X developer app = 17 POST /2/tweets per 24h
  - 2 accounts = 34 posts/day, still $0
  - Posts spaced ~43 min apart (86400s / 34 = 2541s)

Thread posting strategy (engagement-optimised):
  - Tweet 1 = main post (shows in feed/timeline, gets impressions)
  - Tweets 2-N = reply chain on that tweet
  - Forces followers to click "Show replies" -> boosts engagement signal
  - X algorithm rewards high reply activity on posts
  - "Show more..." hook on each tweet keeps scroll depth high

Content mix (proven engagement pattern):
  - 3 single tweets, then 1 full article thread, repeat
  - Article threads tagged [Thread] to signal value upfront
  - Optimal posting times built in (9am, 12pm, 6pm UTC)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from scanner.storage import PostStore
from scanner.templates import generate_tweet
from x_poster import (
    post_tweet, post_thread, get_all_credentials,
    MAX_FREE_POSTS_PER_DAY, MAX_TWEET_LEN
)

logger = logging.getLogger("auto_scheduler")

POSTS_PER_ACCOUNT_PER_DAY = MAX_FREE_POSTS_PER_DAY  # 17

# Gap between posts spread across 24h for 2 accounts
# 86400 / (17 * 2) = 2541s = ~42 min
POST_INTERVAL_SECONDS = 2601  # 43 min, gives small buffer

STATE_FILE = "auto_post_state.json"

_auto_posting_enabled: bool = False
_notify_chat_id: str = ""


def set_auto_posting(enabled: bool, chat_id: str = "") -> None:
    global _auto_posting_enabled, _notify_chat_id
    _auto_posting_enabled = enabled
    if chat_id:
        _notify_chat_id = chat_id
    logger.info(f"Auto-posting {'ENABLED' if enabled else 'DISABLED'}")
    # Persist state so the panel can read the true value
    try:
        state = _load_state()
        state["auto_posting_enabled"] = enabled
        if chat_id:
            state["notify_chat_id"] = chat_id
        _save_state(state)
    except Exception:
        pass


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
        logger.error(f"State save error: {e}")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _account_posts_today(state: dict, label: str) -> int:
    return state.get(_today(), {}).get(label, 0)


def _increment_count(state: dict, label: str) -> dict:
    today = _today()
    # Clean old keys
    state = {k: v for k, v in state.items() if k >= today}
    if today not in state:
        state[today] = {}
    state[today][label] = state[today].get(label, 0) + 1
    return state


def _pick_account(creds_list, state: dict):
    """Pick the account with fewest posts today that's under the limit."""
    available = [
        c for c in creds_list
        if _account_posts_today(state, c.label) < POSTS_PER_ACCOUNT_PER_DAY
    ]
    if not available:
        return None
    # Use the one with fewest posts today for even distribution
    return min(available, key=lambda c: _account_posts_today(state, c.label))


def _get_best_post(store: PostStore) -> Optional[dict]:
    """Get the highest-scored unposted post."""
    posts = store.get_latest_posts(limit=20, exclude_posted=True)
    if not posts:
        return None
    return max(posts, key=lambda p: float(p.get("match_score", 0)))


def _get_next_article(store: PostStore) -> Optional[dict]:
    """Get the next unposted article thread."""
    articles = store.get_articles(limit=1, exclude_posted=True)
    return articles[0] if articles else None


def _prepare_thread_tweets(tweets: list[str]) -> list[str]:
    """Prepare thread tweets for posting.

    - Tweet 1: keep "Show more..." hook (drives X to show it in feed)
    - Tweets 2-N: also keep hooks (drives reply interaction)
    - Hard-cap each at 280 chars
    - "Show more..." is intentional — makes X show expand button
    """
    result = []
    for i, tw in enumerate(tweets):
        tw = tw.strip()
        if len(tw) > MAX_TWEET_LEN:
            tw = tw[:MAX_TWEET_LEN - 3] + "..."
        result.append(tw)
    return result


async def run_auto_poster(bot=None) -> None:
    """Main loop: posts to X on interval when enabled."""
    global _notify_chat_id
    logger.info(f"Auto-poster loop started. Interval: {POST_INTERVAL_SECONDS}s (~{POST_INTERVAL_SECONDS//60}min)")

    # Restore notify_chat_id from persisted state
    state = _load_state()
    if state.get("notify_chat_id"):
        _notify_chat_id = state["notify_chat_id"]

    creds_list = get_all_credentials()
    if not creds_list:
        logger.warning("No X credentials found in .env. Auto-poster standing by.")

    post_cycle = 0

    while True:
        await asyncio.sleep(POST_INTERVAL_SECONDS)

        if not _auto_posting_enabled:
            continue

        creds_list = get_all_credentials()
        if not creds_list:
            logger.warning("Auto-posting ON but no X credentials in .env")
            continue

        state = _load_state()
        creds = _pick_account(creds_list, state)
        if creds is None:
            logger.info("All accounts at daily limit. Waiting for UTC midnight reset.")
            continue

        store = PostStore()
        post_cycle += 1

        # Pattern: 3 single posts, then 1 article thread
        if post_cycle % 4 == 0:
            await _post_article(store, creds, state, creds_list, bot)
        else:
            await _post_single(store, creds, state, creds_list, bot)


async def _post_single(store, creds, state, creds_list, bot):
    """Post one tweet from the best unposted post."""
    post = _get_best_post(store)
    if not post:
        logger.info("No unposted posts available.")
        return

    try:
        tweet_pages = generate_tweet(post)  # returns list[str]
        # For single posts: if it's a multi-page tweet, post as thread too
        if len(tweet_pages) == 1:
            result = await asyncio.to_thread(post_tweet, tweet_pages[0], creds)
        else:
            # Even "single" posts that split become a thread chain
            prepared = _prepare_thread_tweets(tweet_pages)
            results = await asyncio.to_thread(post_thread, prepared, creds)
            result = results[0] if results else {"success": False, "error": "empty_results"}

        if result.get("success"):
            store.mark_posted(post["id"])
            state = _increment_count(state, creds.label)
            _save_state(state)

            total_today = sum(_account_posts_today(state, c.label) for c in creds_list)
            today_count = _account_posts_today(state, creds.label)
            max_today = len(creds_list) * POSTS_PER_ACCOUNT_PER_DAY

            logger.info(
                f"Posted via {creds.label} "
                f"({today_count}/{POSTS_PER_ACCOUNT_PER_DAY}) | "
                f"Total today: {total_today}/{max_today}"
            )

            if bot and _notify_chat_id:
                tweet_id = result.get("tweet_id", "")
                url = f"https://x.com/i/web/status/{tweet_id}" if tweet_id else ""
                await bot.send_message(
                    chat_id=_notify_chat_id,
                    text=(
                        f"✅ Auto-posted tweet\n\n"
                        f"<b>{post['title'][:80]}</b>\n"
                        f"via {creds.label} | Today: {total_today}/{max_today}\n"
                        + (f"\n{url}" if url else "")
                    ),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )

        elif result.get("error") == "rate_limited":
            logger.warning(f"Rate limited on {creds.label}")
            if bot and _notify_chat_id:
                await bot.send_message(
                    chat_id=_notify_chat_id,
                    text="⏳ Rate limited on X — waiting for reset. Will retry next interval.",
                    parse_mode="HTML",
                )
        elif result.get("error", "").startswith("http_503") or result.get("error", "").startswith("http_502"):
            logger.warning(f"X API down (503) on {creds.label}")
            if bot and _notify_chat_id:
                await bot.send_message(
                    chat_id=_notify_chat_id,
                    text=(
                        "⚠️ <b>X API is down (503)</b> — tried to post but X servers are degraded.\n\n"
                        f"Post queued: <b>{post['title'][:60]}</b>\n\n"
                        "Will retry automatically next interval (~43 min). "
                        "Check: api.status.x.com"
                    ),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
        else:
            logger.error(f"Post failed: {result}")
            if bot and _notify_chat_id:
                await bot.send_message(
                    chat_id=_notify_chat_id,
                    text=f"❌ Post failed: <code>{result.get('error','unknown')}</code>",
                    parse_mode="HTML",
                )

    except Exception as e:
        logger.error(f"_post_single error: {e}", exc_info=True)


async def _post_article(store, creds, state, creds_list, bot):
    """Post an article thread as a reply chain."""
    article = _get_next_article(store)
    if not article:
        logger.info("No unposted articles. Falling back to single post.")
        await _post_single(store, creds, state, creds_list, bot)
        return

    try:
        raw_tweets = json.loads(article["thread_json"])
        tweets = _prepare_thread_tweets(raw_tweets)

        logger.info(f"Posting article thread ({len(tweets)} tweets): {article['title'][:60]}")
        results = await asyncio.to_thread(post_thread, tweets, creds)

        success_count = sum(1 for r in results if r.get("success"))

        if success_count > 0:
            store.mark_article_posted(article["id"])
            state = _increment_count(state, creds.label)
            _save_state(state)

            total_today = sum(_account_posts_today(state, c.label) for c in creds_list)
            max_today = len(creds_list) * POSTS_PER_ACCOUNT_PER_DAY

            first_id = next((r.get("tweet_id") for r in results if r.get("success")), "")
            url = f"https://x.com/i/web/status/{first_id}" if first_id else ""

            logger.info(f"Thread posted: {success_count}/{len(tweets)} tweets")

            if bot and _notify_chat_id:
                await bot.send_message(
                    chat_id=_notify_chat_id,
                    text=(
                        f"🧵 Auto-posted thread ({success_count}/{len(tweets)} tweets)\n\n"
                        f"<b>{article['title'][:80]}</b>\n"
                        f"via {creds.label} | Today: {total_today}/{max_today}\n"
                        + (f"\n{url}" if url else "")
                    ),
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )

    except Exception as e:
        logger.error(f"_post_article error: {e}", exc_info=True)
        if bot and _notify_chat_id:
            err_str = str(e)
            if '503' in err_str or '502' in err_str:
                await bot.send_message(
                    chat_id=_notify_chat_id,
                    text="⚠️ <b>X API is down (503)</b> — thread post failed. Will retry next interval.",
                    parse_mode="HTML",
                )


def get_status(creds_list=None) -> dict:
    """Return current auto-posting status."""
    if creds_list is None:
        creds_list = get_all_credentials()

    state = _load_state()
    # Read persisted enabled flag (accurate even when called from outside the bot process)
    enabled = state.get("auto_posting_enabled", _auto_posting_enabled)
    total_today = sum(_account_posts_today(state, c.label) for c in creds_list)
    max_per_day = len(creds_list) * POSTS_PER_ACCOUNT_PER_DAY

    return {
        "enabled": enabled,
        "accounts_configured": len(creds_list),
        "max_posts_per_day": max_per_day,
        "posted_today": total_today,
        "remaining_today": max(0, max_per_day - total_today),
        "interval_minutes": POST_INTERVAL_SECONDS // 60,
        "accounts": [
            {
                "label": c.label,
                "posted_today": _account_posts_today(state, c.label),
                "remaining_today": max(0, POSTS_PER_ACCOUNT_PER_DAY - _account_posts_today(state, c.label)),
            }
            for c in creds_list
        ],
        "date": _today(),
    }
