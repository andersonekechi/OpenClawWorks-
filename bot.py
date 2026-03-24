"""BaceHelpr Interactive Telegram Bot.

Posts sorted by most recent. Each post has a button -> ready-to-copy tweet.
Mark as posted to avoid repeats. Threads split at 280 chars with hooks.
"""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone

import yaml
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from scanner.keywords import PostCategory, CATEGORY_DISPLAY
from scanner.reddit_client import RedditClient
from scanner.scanner import RedditScanner
from scanner.storage import PostStore
from scanner.articles import generate_articles
from auto_scheduler import run_auto_poster, set_auto_posting, is_auto_posting_enabled, get_status as get_autopost_status
from x_poster import get_all_credentials as get_x_credentials, verify_credentials, load_credentials

from scanner.templates import generate_tweet

load_dotenv()
# ─── .env writer for X key setup from Telegram ───────────────────────────────

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

def _env_read() -> dict:
    """Read .env into a dict (preserves all existing keys)."""
    pairs = {}
    try:
        with open(ENV_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    pairs[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return pairs


def _env_write(pairs: dict) -> None:
    """Write dict back to .env, preserving comment blocks."""
    try:
        with open(ENV_PATH, "r") as f:
            raw = f.read()
    except FileNotFoundError:
        raw = ""

    for key, value in pairs.items():
        import re as _re
        pattern = _re.compile(rf"^{_re.escape(key)}=.*$", _re.MULTILINE)
        replacement = f"{key}={value}"
        if pattern.search(raw):
            raw = pattern.sub(replacement, raw)
        else:
            raw = raw.rstrip() + f"\n{key}={value}\n"

    with open(ENV_PATH, "w") as f:
        f.write(raw)

    # Hot-reload into os.environ so bot sees them immediately
    for key, value in pairs.items():
        os.environ[key] = value


# Conversation states for /xsetup wizard
XS_ACCOUNT   = 0
XS_API_KEY   = 1
XS_API_SEC   = 2
XS_ACC_TOK   = 3
XS_ACC_SEC   = 4

# Temporary storage for keys being entered (per user)
_xsetup_temp: dict = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bacehelpr")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CONFIG_PATH = "config.yaml"

_raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = {int(x.strip()) for x in _raw_admins.split(",") if x.strip().isdigit()}

DENIED_MSG = (
    "<b>Access Denied</b>\n\n"
    "This bot is private.\n\n"
    "Want your own BaceHelpr bot that scans Reddit daily "
    "and generates ready-to-post crypto tweets?\n\n"
    "Contact the dev: @andersonekechi\n\n"
    "Features:\n"
    "- Daily Reddit scans (Solana, ETH, Base...)\n"
    "- Ready-to-copy tweets &amp; article threads\n"
    "- Posted tracking so you never repeat\n"
    "- Runs 24/7 on your own server"
)

POSTS_PER_PAGE = 8

CATEGORY_ORDER = [
    PostCategory.INVESTOR,
    PostCategory.NEWBIE_HELP,
    PostCategory.STUCK_DEV,
    PostCategory.BUILDING,
]

CAT_SHORT = {
    PostCategory.INVESTOR.value: "inv",
    PostCategory.NEWBIE_HELP.value: "new",
    PostCategory.STUCK_DEV.value: "stk",
    PostCategory.BUILDING.value: "bld",
    PostCategory.DISCUSSION.value: "dis",
}
SHORT_TO_CAT = {v: k for k, v in CAT_SHORT.items()}


def _is_admin(update: Update) -> bool:
    user = update.effective_user
    return user is not None and user.id in ADMIN_IDS


async def _deny(update: Update):
    """Send denial message to unauthorized users."""
    if update.callback_query:
        await update.callback_query.answer("Access denied", show_alert=True)
    elif update.message:
        await update.message.reply_text(DENIED_MSG, parse_mode="HTML")


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fmt_date(created_utc) -> str:
    """Format a UTC timestamp as dd.mm"""
    try:
        dt = datetime.fromtimestamp(float(created_utc), tz=timezone.utc)
        return dt.strftime("%d.%m")
    except (ValueError, TypeError, OSError):
        return "??.??"


def _main_menu_keyboard() -> InlineKeyboardMarkup:
    creds = get_x_credentials()
    ap_status = get_autopost_status(creds)
    ap_icon = "✅ ON" if ap_status["enabled"] else "⛔ OFF"
    accounts = ap_status["accounts_configured"]
    x_label = f"⚙️ X Account & Auto-Post  [{ap_icon}]" if accounts else "⚙️ Connect X Account"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Stats & Queue", callback_data="stats_queue")],
        [InlineKeyboardButton("🔄 Run Fresh Scan", callback_data="scan")],
        [InlineKeyboardButton(x_label, callback_data="xsetup_menu")],
    ])


def _get_store() -> PostStore:
    return PostStore()


def _run_scan() -> dict[str, list[dict]]:
    client = RedditClient()
    store = _get_store()
    scanner = RedditScanner(client, config_path=CONFIG_PATH, store=store)
    results = scanner.scan_all()
    articles = generate_articles(store)
    for art in articles:
        store.save_article(art)
    return results


def _get_posts_for_category(cat_value: str) -> list[dict]:
    store = _get_store()
    posts = store.get_todays_posts(category=cat_value, exclude_posted=True)
    if not posts:
        posts = store.get_latest_posts(category=cat_value, limit=50, exclude_posted=True)
    return posts


def _post_list_keyboard(cat_short: str, posts: list[dict], page: int) -> InlineKeyboardMarkup:
    start = page * POSTS_PER_PAGE
    end = start + POSTS_PER_PAGE
    page_posts = posts[start:end]
    total_pages = max(1, (len(posts) + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE)

    buttons = []
    for i, p in enumerate(page_posts):
        idx = start + i
        date = _fmt_date(p.get("created_utc", 0))
        title = p["title"][:38]
        networks = p.get("matched_networks", "")
        if isinstance(networks, str):
            networks = networks.split(",") if networks else []
        tag = f" [{networks[0]}]" if networks else ""
        label = f"{idx+1}. {title}{tag} | {date}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"tw_{cat_short}_{idx}_0")])

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("< Prev", callback_data=f"cat_{cat_short}_{page-1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("Next >", callback_data=f"cat_{cat_short}_{page+1}"))
    if nav_row:
        buttons.append(nav_row)
    buttons.append([InlineKeyboardButton("< Back to Menu", callback_data="menu")])
    return InlineKeyboardMarkup(buttons)


def _tweet_nav_keyboard(
    cat_short: str, post_idx: int, post_id: str,
    page: int, total_pages: int, list_page: int, is_posted: bool
) -> InlineKeyboardMarkup:
    rows = []

    thread_nav = []
    if page > 0:
        thread_nav.append(InlineKeyboardButton(
            f"< Page {page}", callback_data=f"tw_{cat_short}_{post_idx}_{page-1}"
        ))
    if page < total_pages - 1:
        thread_nav.append(InlineKeyboardButton(
            f"Page {page+2} >", callback_data=f"tw_{cat_short}_{post_idx}_{page+1}"
        ))
    if thread_nav:
        rows.append(thread_nav)

    if is_posted:
        rows.append([InlineKeyboardButton(
            "POSTED", callback_data="noop"
        )])
    else:
        rows.append([InlineKeyboardButton(
            "Mark as Posted", callback_data=f"done_{post_id}"
        )])

    rows.append([InlineKeyboardButton(
        "< Back to List", callback_data=f"cat_{cat_short}_{list_page}"
    )])
    return InlineKeyboardMarkup(rows)


# --- Handlers ---

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    await update.message.reply_text(
        "<b>BaceHelpr</b> - Reddit Crypto Scanner\n\n"
        "I scan crypto subreddits and find:\n"
        "  <b>$</b> Investors &amp; jobs hiring devs\n"
        "  <b>?</b> Newbies who need your help\n"
        "  <b>!</b> Devs stuck on problems\n"
        "  <b>&gt;</b> Projects to collaborate on\n"
        "  <b>+</b> Articles (5-8 tweet long threads)\n\n"
        "<b>How it works:</b>\n"
        "1. Tap a category = single-post tweets\n"
        "2. Tap Articles = full long-form threads\n"
        "3. Tap any item = ready-to-copy text\n"
        "4. Mark as Posted when done\n"
        "5. Refresh adds new content, never removes old\n\n"
        "Pick a category:",
        parse_mode="HTML",
        reply_markup=_main_menu_keyboard(),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    await update.message.reply_text(
        "<b>Commands:</b>\n"
        "/start - Main menu\n"
        "/scan - Fresh Reddit scan\n"
        "/jobs - Investor &amp; job posts\n"
        "/newbies - Newbie help requests\n"
        "/stuck - Devs stuck on problems\n"
        "/builds - Building &amp; collabs\n"
        "/stats - Statistics\n\n"
        "<b>Tips:</b>\n"
        "- Posts with DONE are already posted\n"
        "- Dates show dd.mm so you pick fresh ones\n"
        "- Tweets in <code>code blocks</code> = tap to copy",
        parse_mode="HTML",
    )


async def scan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    msg = await update.message.reply_text("Scanning 13 crypto subreddits... (~15s)")
    results = await asyncio.to_thread(_run_scan)
    total = sum(len(v) for v in results.values())

    parts = []
    for cat in CATEGORY_ORDER:
        count = len(results.get(cat.value, []))
        if count:
            label, _, emoji = CATEGORY_DISPLAY[cat]
            parts.append(f"  {emoji} {label}: <b>{count}</b>")

    await msg.edit_text(
        f"<b>Scan complete!</b> {total} posts found.\n\n" +
        "\n".join(parts) + "\n\nPick a category:",
        parse_mode="HTML",
        reply_markup=_main_menu_keyboard(),
    )


async def _show_category_page(target, cat_short: str, page: int):
    cat_value = SHORT_TO_CAT.get(cat_short)
    if not cat_value:
        return

    posts = _get_posts_for_category(cat_value)
    category = PostCategory(cat_value)
    label, _, emoji = CATEGORY_DISPLAY[category]
    total = len(posts)
    total_pages = max(1, (total + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE)
    page = min(page, total_pages - 1)

    header = (
        f"<b>{emoji} {label}</b> ({total} posts)\n"
        f"Page {page+1}/{total_pages} | Newest first\n\n"
        f"Tap any post for a ready tweet:"
    )
    keyboard = _post_list_keyboard(cat_short, posts, page)

    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(header, parse_mode="HTML", reply_markup=keyboard)
    else:
        await target.message.reply_text(header, parse_mode="HTML", reply_markup=keyboard)


async def _show_tweet(query, cat_short: str, post_idx: int, thread_page: int):
    cat_value = SHORT_TO_CAT.get(cat_short)
    if not cat_value:
        return

    posts = _get_posts_for_category(cat_value)
    if post_idx >= len(posts):
        await query.edit_message_text(
            "Post not found. Run a fresh scan.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("< Back", callback_data=f"cat_{cat_short}_0")]
            ]),
        )
        return

    post = posts[post_idx]
    store = _get_store()
    is_posted = store.is_posted(post["id"])
    thread = generate_tweet(post)
    total_thread = len(thread)
    thread_page = min(thread_page, total_thread - 1)
    tweet_text = thread[thread_page]
    list_page = post_idx // POSTS_PER_PAGE
    date = _fmt_date(post.get("created_utc", 0))

    if total_thread > 1:
        header = (
            f"<b>Thread {thread_page+1}/{total_thread}</b> | "
            f"{len(tweet_text)} chars | {date}\n"
        )
    else:
        header = f"<b>Ready Tweet</b> | {len(tweet_text)} chars | {date}\n"

    if is_posted:
        header += "ALREADY POSTED\n"

    header += "\n"
    msg = header + f"<code>{_escape(tweet_text)}</code>"

    keyboard = _tweet_nav_keyboard(
        cat_short, post_idx, post["id"],
        thread_page, total_thread, list_page, is_posted
    )

    await query.edit_message_text(
        msg, parse_mode="HTML", reply_markup=keyboard,
        disable_web_page_preview=True,
    )


async def jobs_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    await _show_category_page(update, "inv", 0)

async def newbies_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    await _show_category_page(update, "new", 0)

async def stuck_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    await _show_category_page(update, "stk", 0)

async def builds_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    await _show_category_page(update, "bld", 0)


async def stats_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    store = _get_store()
    s = store.get_stats()
    cats = "\n".join(f"  {k}: <b>{v}</b>" for k, v in s.get("by_category", {}).items())
    subs = "\n".join(f"  r/{k}: {v}" for k, v in list(s.get("top_subreddits", {}).items())[:8])

    text = (
        f"<b>BaceHelpr Stats</b>\n\n"
        f"Total posts: <b>{s['total_posts']}</b>\n"
        f"Posted: <b>{s.get('posted', 0)}</b>\n"
        f"Remaining: <b>{s.get('unposted', 0)}</b>\n\n"
        f"<b>By category:</b>\n{cats}\n\n"
        f"<b>Top subreddits:</b>\n{subs}"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("< Menu", callback_data="menu")]])
    if hasattr(update, "message") and update.message:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await update.edit_message_text(text, parse_mode="HTML", reply_markup=kb)


# --- Article handlers ---

ARTICLES_PER_PAGE = 6


async def _show_articles_page(target, page: int):
    store = _get_store()
    articles = store.get_articles(limit=50, exclude_posted=True)
    total = len(articles)
    total_pages = max(1, (total + ARTICLES_PER_PAGE - 1) // ARTICLES_PER_PAGE)
    page = min(page, total_pages - 1)

    if not articles:
        text = (
            "<b>Articles</b>\n\n"
            "No articles yet. Hit <b>Run Fresh Scan</b> first -- "
            "articles are auto-generated from your scanned posts."
        )
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("< Menu", callback_data="menu")]])
        if hasattr(target, "edit_message_text"):
            await target.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
        else:
            await target.message.reply_text(text, parse_mode="HTML", reply_markup=kb)
        return

    start = page * ARTICLES_PER_PAGE
    page_articles = articles[start:start + ARTICLES_PER_PAGE]

    buttons = []
    for i, art in enumerate(page_articles):
        idx = start + i
        pages = len(art.get("thread", []))
        label = f"{idx+1}. {art['title'][:40]} ({pages}tw)"
        buttons.append([InlineKeyboardButton(label, callback_data=f"art_{idx}_0")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("< Prev", callback_data=f"articles_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next >", callback_data=f"articles_{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("< Menu", callback_data="menu")])

    header = (
        f"<b>Articles (Long Threads)</b>\n"
        f"{total} articles | Page {page+1}/{total_pages}\n\n"
        f"Each article is a 5-8 tweet thread.\n"
        f"Tap one to see all pages:"
    )
    kb = InlineKeyboardMarkup(buttons)
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(header, parse_mode="HTML", reply_markup=kb)
    else:
        await target.message.reply_text(header, parse_mode="HTML", reply_markup=kb)


async def _show_article_tweet(query, art_idx: int, tweet_page: int):
    store = _get_store()
    articles = store.get_articles(limit=50, exclude_posted=True)

    if art_idx >= len(articles):
        await query.edit_message_text(
            "Article not found.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("< Articles", callback_data="articles_0")]
            ]),
        )
        return

    art = articles[art_idx]
    thread = art.get("thread", [])
    total_tw = len(thread)
    tweet_page = min(tweet_page, total_tw - 1)
    tweet_text = thread[tweet_page]
    is_posted = store.is_article_posted(art["id"])
    list_page = art_idx // ARTICLES_PER_PAGE

    header = (
        f"<b>{_escape(art['title'][:60])}</b>\n"
        f"Thread {tweet_page+1}/{total_tw} | {len(tweet_text)} chars | "
        f"{art.get('network', '')}\n"
    )
    if is_posted:
        header += "ALREADY POSTED\n"
    header += "\n"

    msg = header + f"<code>{_escape(tweet_text)}</code>"

    rows = []
    nav = []
    if tweet_page > 0:
        nav.append(InlineKeyboardButton(
            f"< Page {tweet_page}", callback_data=f"art_{art_idx}_{tweet_page-1}"
        ))
    if tweet_page < total_tw - 1:
        nav.append(InlineKeyboardButton(
            f"Page {tweet_page+2} >", callback_data=f"art_{art_idx}_{tweet_page+1}"
        ))
    if nav:
        rows.append(nav)

    if is_posted:
        rows.append([InlineKeyboardButton("POSTED", callback_data="noop")])
    else:
        rows.append([InlineKeyboardButton(
            "Mark Article Posted", callback_data=f"artdone_{art['id']}"
        )])

    rows.append([InlineKeyboardButton(
        "< Back to Articles", callback_data=f"articles_{list_page}"
    )])

    await query.edit_message_text(
        msg, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(rows),
        disable_web_page_preview=True,
    )


async def articles_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    await _show_articles_page(update, 0)


# --- Button handler ---


async def autopost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Control automatic X posting. Usage: /autopost on|off|status"""
    if not _is_admin(update):
        await _deny(update)
        return

    args = context.args or []
    action = args[0].lower() if args else "status"
    chat_id = str(update.effective_chat.id)
    creds = get_x_credentials()

    if action == "on":
        if not creds:
            await update.message.reply_text(
                "<b>No X accounts configured!</b>\n\n"
                "Add to <code>/opt/bacehelpr/.env</code>:\n\n"
                "<code>X_API_KEY_1=your_key_here</code>\n"
                "<code>X_API_SECRET_1=your_secret</code>\n"
                "<code>X_ACCESS_TOKEN_1=your_token</code>\n"
                "<code>X_ACCESS_TOKEN_SECRET_1=your_token_secret</code>\n\n"
                "Get keys at developer.x.com (free tier = 17 posts/day per account)\n"
                "Add a 2nd account with _2 suffix for 34 posts/day total.\n\n"
                "Then restart the bot.",
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
            return
        set_auto_posting(True, chat_id)
        status = get_autopost_status(creds)
        await update.message.reply_text(
            "<b>Auto-posting ENABLED!</b>\n\n"
            f"Accounts: <b>{status['accounts_configured']}</b>\n"
            f"Max posts/day: <b>{status['max_posts_per_day']}</b>\n"
            f"Post interval: every <b>~{status['interval_minutes']} min</b>\n\n"
            "Posts will go out automatically from your DB.\n"
            "You\'ll get a notification here after each post.",
            parse_mode="HTML",
        )

    elif action == "off":
        set_auto_posting(False)
        await update.message.reply_text(
            "<b>Auto-posting DISABLED.</b>\n\nNo more automatic posts.",
            parse_mode="HTML",
        )

    else:  # status
        status = get_autopost_status(creds)
        state_icon = "✅ ON" if status["enabled"] else "⛔ OFF"
        lines = [
            f"<b>Auto-posting: {state_icon}</b>\n",
            f"Accounts configured: <b>{status['accounts_configured']}</b>",
            f"Max posts/day: <b>{status['max_posts_per_day']}</b>",
            f"Posted today: <b>{status['posted_today']}</b>",
            f"Remaining today: <b>{status['remaining_today']}</b>",
            f"Interval: every <b>~{status['interval_minutes']} min</b>",
        ]
        if status.get("accounts"):
            lines.append("")
            for acc in status["accounts"]:
                total_allowed = acc["posted_today"] + acc["remaining_today"]
                lines.append(f"  • {acc['label']}: {acc['posted_today']}/{total_allowed} today")
        if not creds:
            lines.append("\n<i>No X API keys set yet. Run /autopost on for setup instructions.</i>")
        await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def _show_xsetup_menu(target):
    """Show X API setup guide and account status."""
    creds_list = get_x_credentials()
    lines = ["<b>X Account Setup</b>\n"]

    if not creds_list:
        lines.append("No X accounts connected yet.\n")
    else:
        for c in creds_list:
            lines.append(f"• {c.label} — tap to verify")
        lines.append("")

    lines.append(
        "<b>How to add an account:</b>\n"
        "1. Go to developer.x.com\n"
        "2. Sign in with your X account\n"
        "3. Create project + app\n"
        "4. Set permissions to Read & Write\n"
        "5. Generate Access Token & Secret\n"
        "6. SSH into VPS:\n"
        "   <code>ssh root@217.156.64.90</code>\n"
        "7. Edit: <code>nano /opt/bacehelpr/.env</code>\n"
        "8. Paste the 4 keys (X_API_KEY_1= etc)\n"
        "9. Restart: <code>systemctl restart bacehelpr</code>\n"
        "10. Come back here → Verify Account\n\n"
        "<b>Free tier = 17 posts/day per account</b>\n"
        "2 accounts = 34/day free"
    )

    buttons = []
    for i in range(1, 4):
        c = load_credentials(str(i))
        if c.is_configured:
            buttons.append([InlineKeyboardButton(f"✅ Verify Account {i}", callback_data=f"xverify_{i}")])
    buttons.append([InlineKeyboardButton("< Menu", callback_data="menu")])

    text = "\n".join(lines)
    kb = InlineKeyboardMarkup(buttons)
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
    else:
        await target.message.reply_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)



# ─── X API Key Setup Wizard ───────────────────────────────────────────────────

async def xsetup_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Entry point: /xsetup — starts the X API key wizard."""
    if not _is_admin(update):
        await _deny(update)
        return ConversationHandler.END

    creds_list = get_x_credentials()
    lines = ["<b>X Account Setup Wizard</b>\n"]

    if creds_list:
        for c in creds_list:
            lines.append(f"  ✅ {c.label} already connected")
        lines.append("")

    lines.append(
        "Which account slot do you want to set up?\n\n"
        "Reply <b>1</b> for Account 1 (17 posts/day)\n"
        "Reply <b>2</b> for Account 2 (+17 posts/day = 34/day total)\n"
        "Reply <b>3</b> for Account 3 (+17 more)\n\n"
        "Or type /cancel to exit."
    )
    await update.message.reply_text("\n".join(lines), parse_mode="HTML")
    return XS_ACCOUNT


async def xsetup_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User chose account slot number."""
    if not _is_admin(update):
        return ConversationHandler.END
    text = update.message.text.strip()
    if text not in ("1", "2", "3", "4", "5"):
        await update.message.reply_text("Please reply with a number: 1, 2, or 3")
        return XS_ACCOUNT
    user_id = update.effective_user.id
    _xsetup_temp[user_id] = {"slot": text}
    await update.message.reply_text(
        f"Setting up <b>Account {text}</b>.\n\n"
        f"<b>Step 1 of 4</b>\n\n"
        "Go to <a href=\"https://developer.x.com\">developer.x.com</a>, sign in, "
        "open your app → Keys and Tokens.\n\n"
        "Paste your <b>API Key</b> (also called Consumer Key):\n\n"
        "<i>It looks like: AbCdEfGhIjKlMnOpQrStUvWxYz1234567890ABCDE</i>",
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    return XS_API_KEY


async def xsetup_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User pasted API Key."""
    if not _is_admin(update):
        return ConversationHandler.END
    key = update.message.text.strip()
    user_id = update.effective_user.id
    _xsetup_temp.setdefault(user_id, {})["api_key"] = key
    # Delete the message so key isn't visible in chat
    try:
        await update.message.delete()
    except Exception:
        pass
    await update.message.reply_text(
        "✅ API Key saved.\n\n"
        "<b>Step 2 of 4</b>\n\n"
        "Paste your <b>API Secret</b> (also called Consumer Secret):\n\n"
        "<i>Longer string, starts similar to the key</i>",
        parse_mode="HTML",
    )
    return XS_API_SEC


async def xsetup_api_secret(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User pasted API Secret."""
    if not _is_admin(update):
        return ConversationHandler.END
    key = update.message.text.strip()
    user_id = update.effective_user.id
    _xsetup_temp.setdefault(user_id, {})["api_secret"] = key
    try:
        await update.message.delete()
    except Exception:
        pass
    await update.message.reply_text(
        "✅ API Secret saved.\n\n"
        "<b>Step 3 of 4</b>\n\n"
        "Paste your <b>Access Token</b>:\n\n"
        "<i>Looks like: 123456789-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890</i>\n\n"
        "If you don\'t see it, click <b>Generate</b> next to Access Token in developer.x.com",
        parse_mode="HTML",
    )
    return XS_ACC_TOK


async def xsetup_access_token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User pasted Access Token."""
    if not _is_admin(update):
        return ConversationHandler.END
    key = update.message.text.strip()
    user_id = update.effective_user.id
    _xsetup_temp.setdefault(user_id, {})["access_token"] = key
    try:
        await update.message.delete()
    except Exception:
        pass
    await update.message.reply_text(
        "✅ Access Token saved.\n\n"
        "<b>Step 4 of 4 — Last one!</b>\n\n"
        "Paste your <b>Access Token Secret</b>:\n\n"
        "<i>Shorter string shown right below the Access Token</i>",
        parse_mode="HTML",
    )
    return XS_ACC_SEC


async def xsetup_access_secret(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User pasted Access Token Secret — save everything and verify."""
    if not _is_admin(update):
        return ConversationHandler.END
    key = update.message.text.strip()
    user_id = update.effective_user.id
    data = _xsetup_temp.get(user_id, {})
    data["access_token_secret"] = key
    try:
        await update.message.delete()
    except Exception:
        pass

    slot = data.get("slot", "1")
    await update.message.reply_text(
        f"Saving Account {slot} credentials and verifying with X...\n\n"
        "⏳ Please wait a moment...",
        parse_mode="HTML",
    )

    # Save to .env
    _env_write({
        f"X_API_KEY_{slot}":              data.get("api_key", ""),
        f"X_API_SECRET_{slot}":           data.get("api_secret", ""),
        f"X_ACCESS_TOKEN_{slot}":         data.get("access_token", ""),
        f"X_ACCESS_TOKEN_SECRET_{slot}":  data.get("access_token_secret", ""),
    })

    # Reload and verify
    from x_poster import load_credentials, verify_credentials
    creds = load_credentials(slot)
    result = await asyncio.to_thread(verify_credentials, creds)

    if result.get("success"):
        username = result.get("username", "unknown")
        total_accounts = len(get_x_credentials())
        max_per_day = total_accounts * 17
        await update.message.reply_text(
            f"✅ <b>Account {slot} connected!</b>\n\n"
            f"Verified as: <b>@{username}</b>\n\n"
            f"Total accounts: <b>{total_accounts}</b>\n"
            f"Max posts/day: <b>{max_per_day}</b> (FREE)\n\n"
            "Now tap the <b>Auto-Post: OFF</b> button in the menu to start posting!",
            parse_mode="HTML",
            reply_markup=_main_menu_keyboard(),
        )
    else:
        err = result.get("error", "unknown error")
        await update.message.reply_text(
            f"❌ <b>Verification failed for Account {slot}</b>\n\n"
            f"Error: <code>{err}</code>\n\n"
            "The keys were saved. Common fixes:\n"
            "• Make sure app permissions are set to <b>Read and Write</b>\n"
            "• Regenerate Access Token after changing permissions\n"
            "• Check you copied the full key (no spaces)\n\n"
            "Run /xsetup to try again.",
            parse_mode="HTML",
        )

    # Clean up temp storage
    _xsetup_temp.pop(user_id, None)
    return ConversationHandler.END


async def xsetup_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """User cancelled setup."""
    user_id = update.effective_user.id
    _xsetup_temp.pop(user_id, None)
    await update.message.reply_text(
        "Setup cancelled. Use /xsetup to start again anytime.",
        reply_markup=_main_menu_keyboard(),
    )
    return ConversationHandler.END


async def _show_stats_queue(target):
    store = _get_store()
    s = store.get_stats()
    creds = get_x_credentials()
    ap = get_autopost_status(creds)

    unposted = s.get("unposted", 0)
    posted = s.get("posted", 0)
    arts_total = s.get("articles_total", 0)
    arts_posted = s.get("articles_posted", 0)
    arts_left = arts_total - arts_posted
    max_pd = max(ap["max_posts_per_day"], 1)
    days_left = unposted // max_pd

    ap_icon = "\u2705 ON" if ap["enabled"] else "\u26d4 OFF"

    lines = [
        "<b>Stats & Queue</b>\n",
        f"<b>Auto-posting:</b> {ap_icon}",
        f"<b>Posted today:</b> {ap['posted_today']}/{ap['max_posts_per_day']}",
        f"<b>Remaining today:</b> {ap['remaining_today']}",
        "",
        "<b>Content Queue</b>",
        f"  Tweets ready:   <b>{unposted}</b>",
        f"  Threads ready:  <b>{arts_left}</b>",
        f"  Already posted: <b>{posted}</b>",
        f"  Queue covers:   <b>~{days_left} days</b>",
        "",
        "<b>By Category (unposted)</b>",
    ]
    cat_labels = {
        "investor":    "\U0001f4b0 Investors & Jobs",
        "newbie_help": "\U0001f198 Newbies",
        "stuck_dev":   "\U0001f41b Devs Stuck",
        "building":    "\U0001f3d7 Building",
    }
    by_cat = s.get("by_category", {})
    for key, label in cat_labels.items():
        lines.append(f"  {label}: <b>{by_cat.get(key, 0)}</b>")

    next_posts = store.get_latest_posts(limit=1, exclude_posted=True)
    if next_posts:
        p = next_posts[0]
        lines.append("")
        lines.append(f"<b>Next up:</b> {p['title'][:60]}...")

    text = "\n".join(lines)
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("< Menu", callback_data="menu")]])
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await target.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


async def _show_x_account_panel(target):
    """Show X account status dashboard with live stats."""
    creds_list = get_x_credentials()
    state = __import__("auto_scheduler").get_status(creds_list)
    store = _get_store()
    db_stats = store.get_stats()

    lines = ["<b>X Account Dashboard</b>\n"]

    if not creds_list:
        lines.append("❌ No X accounts connected yet.\n")
    else:
        for c in creds_list:
            from x_poster import verify_credentials
            result = await asyncio.to_thread(verify_credentials, c)
            if result.get("success"):
                username = result.get("username", "?")
                posted = next((a["posted_today"] for a in state.get("accounts", []) if a["label"] == c.label), 0)
                remaining = 17 - posted
                lines.append(f"✅ <b>@{username}</b> ({c.label})")
                lines.append(f"   Posted today: <b>{posted}/17</b> | Remaining: <b>{remaining}</b>")
            else:
                lines.append(f"⚠️ {c.label} — <i>connection issue</i>")
        lines.append("")

    # Auto-post status
    ap_icon = "✅ ON" if state["enabled"] else "⛔ OFF"
    lines.append(f"Auto-posting: <b>{ap_icon}</b>")
    lines.append(f"Posts today: <b>{state['posted_today']}/{state['max_posts_per_day']}</b>")
    lines.append(f"Remaining today: <b>{state['remaining_today']}</b>")
    lines.append(f"Interval: every <b>~{state['interval_minutes']} min</b>")
    lines.append("")

    # DB content remaining
    unposted = db_stats.get("unposted", 0)
    total = db_stats.get("total_posts", 0)
    articles = db_stats.get("articles_total", 0)
    unposted_arts = articles - db_stats.get("articles_posted", 0)
    lines.append(f"Posts in queue: <b>{unposted}</b> tweets ready")
    lines.append(f"Article threads: <b>{unposted_arts}</b> threads ready")
    if state["max_posts_per_day"] > 0:
        days_left = unposted // max(state["max_posts_per_day"], 1)
        lines.append(f"Content covers: <b>~{days_left} days</b> at current rate")

    # Buttons
    buttons = []
    ap_toggle_label = "⛔ Turn Auto-Post OFF" if state["enabled"] else "✅ Turn Auto-Post ON"
    buttons.append([InlineKeyboardButton(ap_toggle_label, callback_data="autopost_toggle")])
    buttons.append([InlineKeyboardButton("➕ Add Another X Account", callback_data="xsetup_start_wizard")])
    if creds_list:
        for c in creds_list:
            buttons.append([InlineKeyboardButton(f"🔄 Re-verify {c.label}", callback_data=f"xverify_{c.label.split('_')[1]}")])
    buttons.append([InlineKeyboardButton("< Menu", callback_data="menu")])

    text = "\n".join(lines)
    kb = InlineKeyboardMarkup(buttons)
    if hasattr(target, "edit_message_text"):
        await target.edit_message_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
    else:
        await target.message.reply_text(text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update):
        return await _deny(update)
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    data = query.data

    if data == "noop":
        return

    if data == "stats_queue":
        await _show_stats_queue(query)
        return

    # Auto-Post toggle button from menu
    if data == "autopost_toggle":
        creds = get_x_credentials()
        ap_status = get_autopost_status(creds)
        if not creds:
            await query.edit_message_text(
                "<b>No X account connected yet.</b>\n\n"
                "Tap <b>Connect X Account</b> in the menu to set up your API keys.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("< Menu", callback_data="menu")]]),
            )
            return
        if ap_status["enabled"]:
            set_auto_posting(False)
            msg = "⛔ <b>Auto-posting OFF</b>\n\nPosts have been paused."
        else:
            chat_id = str(query.message.chat_id)
            set_auto_posting(True, chat_id)
            s = get_autopost_status(creds)
            msg = (
                "✅ <b>Auto-posting ON</b>\n\n"
                f"Accounts: <b>{s['accounts_configured']}</b>\n"
                f"Max posts/day: <b>{s['max_posts_per_day']}</b>\n"
                f"Posting every: <b>~{s['interval_minutes']} min</b>\n\n"
                "You'll get a notification here after each post."
            )
        await query.edit_message_text(msg, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("< Menu", callback_data="menu")]]))
        return

    # X Setup menu — show connected account info + options
    if data == "xsetup_menu":
        await _show_x_account_panel(query)
        return

    if data == "xsetup_start_wizard":
        await query.message.reply_text(
            "Starting X account setup wizard...\n\nSend /xsetup to begin.",
            parse_mode="HTML",
        )
        return

    # X Setup: verify account 1 or 2
    if data.startswith("xverify_"):
        suffix = data.split("_")[1]
        creds = load_credentials(suffix)
        result = await asyncio.to_thread(verify_credentials, creds)
        if result.get("success"):
            await query.edit_message_text(
                f"✅ <b>Account {suffix} connected!</b>\n\n"
                f"Username: @{result['username']}\n\n"
                "Great — this account can post 17 tweets/day free.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("< X Setup", callback_data="xsetup_menu")]])
            )
        else:
            err = result.get("error", "unknown")
            await query.edit_message_text(
                f"❌ <b>Account {suffix} failed</b>\n\n"
                f"Error: <code>{err}</code>\n\n"
                "Check that all 4 keys are correct in .env and restart the bot.",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("< X Setup", callback_data="xsetup_menu")]])
            )
        return

    if data == "menu":
        await query.edit_message_text(
            "<b>BaceHelpr</b> - Pick a category:",
            parse_mode="HTML",
            reply_markup=_main_menu_keyboard(),
        )
        return

    if data == "scan":
        await query.edit_message_text("Scanning 13 crypto subreddits... (~15s)")
        results = await asyncio.to_thread(_run_scan)
        total = sum(len(v) for v in results.values())

        parts = []
        for cat in CATEGORY_ORDER:
            count = len(results.get(cat.value, []))
            if count:
                label, _, emoji = CATEGORY_DISPLAY[cat]
                parts.append(f"  {emoji} {label}: <b>{count}</b>")

        await query.edit_message_text(
            f"<b>Scan complete!</b> {total} posts found.\n\n" +
            "\n".join(parts) + "\n\nPick a category:",
            parse_mode="HTML",
            reply_markup=_main_menu_keyboard(),
        )
        return

    if data == "stats":
        store = _get_store()
        s = store.get_stats()
        cats = "\n".join(f"  {k}: <b>{v}</b>" for k, v in s.get("by_category", {}).items())
        subs = "\n".join(f"  r/{k}: {v}" for k, v in list(s.get("top_subreddits", {}).items())[:8])
        await query.edit_message_text(
            f"<b>BaceHelpr Stats</b>\n\n"
            f"Total: <b>{s['total_posts']}</b> | "
            f"Posted: <b>{s.get('posted', 0)}</b> | "
            f"Remaining: <b>{s.get('unposted', 0)}</b>\n\n"
            f"<b>By category:</b>\n{cats}\n\n"
            f"<b>Top subreddits:</b>\n{subs}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("< Menu", callback_data="menu")]
            ]),
        )
        return

    # articles_{page}
    if data.startswith("articles_"):
        page = int(data.split("_")[1])
        await _show_articles_page(query, page)
        return

    # art_{idx}_{tweet_page}
    if data.startswith("art_") and not data.startswith("artdone_"):
        parts = data.split("_")
        if len(parts) == 3:
            await _show_article_tweet(query, int(parts[1]), int(parts[2]))
        return

    # artdone_{article_id}
    if data.startswith("artdone_"):
        art_id = data[8:]
        store = _get_store()
        store.mark_article_posted(art_id)
        await query.edit_message_text(
            "Article marked as posted!\n\nIt will show DONE in the list now.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("< Menu", callback_data="menu")]
            ]),
        )
        return

    # done_{post_id} -- mark as posted
    if data.startswith("done_"):
        post_id = data[5:]
        store = _get_store()
        store.mark_posted(post_id)
        await query.edit_message_text(
            "Marked as posted!\n\nIt will show DONE in the list now.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("< Menu", callback_data="menu")]
            ]),
        )
        return

    # cat_{short}_{page}
    if data.startswith("cat_"):
        parts = data.split("_")
        if len(parts) == 3:
            await _show_category_page(query, parts[1], int(parts[2]))
        return

    # tw_{short}_{postIdx}_{threadPage}
    if data.startswith("tw_"):
        parts = data.split("_")
        if len(parts) == 4:
            await _show_tweet(query, parts[1], int(parts[2]), int(parts[3]))
        return


# --- Scheduled scan ---

async def scheduled_scan(context: ContextTypes.DEFAULT_TYPE):
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not chat_id:
        return

    results = await asyncio.to_thread(_run_scan)
    total = sum(len(v) for v in results.values())

    parts = [f"<b>New Scan</b> - {total} posts found\n"]
    for cat in CATEGORY_ORDER:
        posts = results.get(cat.value, [])
        if posts:
            label, _, emoji = CATEGORY_DISPLAY[cat]
            parts.append(f"{emoji} {label}: <b>{len(posts)}</b>")

    await context.bot.send_message(
        chat_id=chat_id,
        text="\n".join(parts) + "\n\nTap a category:",
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=_main_menu_keyboard(),
    )


# --- Startup ---

async def send_startup_message(app: Application):
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not chat_id:
        return
    try:
        store = _get_store()
        s = store.get_stats()
        total = s.get("total_posts", 0)
        unposted = s.get("unposted", 0)

        text = (
            "<b>BaceHelpr is online!</b>\n\n"
            f"<b>{total}</b> posts in database"
        )
        if total > 0:
            text += f" | <b>{unposted}</b> not yet posted\n\n"
        else:
            text += "\n\nHit <b>Run Fresh Scan</b> to get started.\n\n"

        creds_list = get_x_credentials()
        ap_status = get_autopost_status(creds_list)
        if creds_list:
            text += f"X: <b>{len(creds_list)} account(s)</b> | Auto-post: <b>{'ON' if ap_status['enabled'] else 'OFF'}</b>\n\n"
        else:
            text += "Tap <b>Connect X Account</b> to set up auto-posting.\n\n"
        text += "Use the buttons below:"

        await app.bot.send_message(
            chat_id=chat_id, text=text, parse_mode="HTML",
            reply_markup=_main_menu_keyboard(),
        )
        logger.info("Startup message sent to chat %s", chat_id)
    except Exception as e:
        logger.warning("Could not send startup message: %s", e)


def main():
    if not TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN in .env file")
        print("1. Message @BotFather on Telegram, send /newbot")
        print("2. Copy the token to .env as TELEGRAM_BOT_TOKEN=xxx")
        return

    with open(CONFIG_PATH) as f:
        cfg = yaml.safe_load(f)
    interval_hours = cfg.get("schedule", {}).get("scan_interval_hours", 12)

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("scan", scan_cmd))
    app.add_handler(CommandHandler("jobs", jobs_cmd))
    app.add_handler(CommandHandler("newbies", newbies_cmd))
    app.add_handler(CommandHandler("stuck", stuck_cmd))
    app.add_handler(CommandHandler("builds", builds_cmd))
    app.add_handler(CommandHandler("articles", articles_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    # X API Key setup wizard (conversation)
    xsetup_conv = ConversationHandler(
        entry_points=[CommandHandler("xsetup", xsetup_start)],
        states={
            XS_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, xsetup_account)],
            XS_API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, xsetup_api_key)],
            XS_API_SEC: [MessageHandler(filters.TEXT & ~filters.COMMAND, xsetup_api_secret)],
            XS_ACC_TOK: [MessageHandler(filters.TEXT & ~filters.COMMAND, xsetup_access_token)],
            XS_ACC_SEC: [MessageHandler(filters.TEXT & ~filters.COMMAND, xsetup_access_secret)],
        },
        fallbacks=[CommandHandler("cancel", xsetup_cancel)],
        allow_reentry=True,
    )
    app.add_handler(xsetup_conv)
    app.add_handler(CommandHandler("autopost", autopost_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.job_queue.run_repeating(
        scheduled_scan,
        interval=interval_hours * 3600,
        first=interval_hours * 3600,
    )
    async def post_init(app):
        await send_startup_message(app)
        # Auto-enable posting on startup if chat_id is configured
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        if chat_id:
            set_auto_posting(True, chat_id)
            logger.info("Auto-posting enabled on startup for chat %s", chat_id)
        asyncio.ensure_future(run_auto_poster(app.bot))

    app.post_init = post_init

    logger.info("BaceHelpr bot started. Scanning every %d hours.", interval_hours)
    app.run_polling()


if __name__ == "__main__":
    main()
