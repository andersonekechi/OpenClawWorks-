"""GSCF Channel Manager Bot.

Workflow:
  1. Admin (@Onlyfewisreal) sends any post (text, photo, video, document) to the bot.
  2. Bot forwards the actual media to the owner (7800993199) with Approve / Edit / Reject buttons.
  3. Owner taps Approve  → bot posts to @gscfgs7baby as-is.
  4. Owner taps Edit     → bot asks owner to send the corrected version,
                           then posts the corrected version to the channel.
  5. Owner taps Reject   → bot asks for a reason (optional Skip button),
                           then notifies the admin with the reason so they can fix it.
  6. Owner can also submit posts directly — they go straight to channel
     after confirmation.
"""

from __future__ import annotations

import logging
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="telegram")

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

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("channel_bot")

# ─── Config ───────────────────────────────────────────────────────────────────
BOT_TOKEN  = "8488113072:AAHG5kg7XZ0PseN0Q1X_8xkm5F4ki70QV0g"
CHANNEL_ID = "@gscfgs7baby"
OWNER_ID   = 7800993199
ADMIN_IDS  = {7800993199, 6162101530}

# ConversationHandler states
WAITING_EDIT          = 1
WAITING_REJECT_REASON = 2

# ─── Keyboards ────────────────────────────────────────────────────────────────

def _approval_keyboard(pending_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Approve", callback_data=f"approve:{pending_id}"),
        InlineKeyboardButton("✏️ Edit",    callback_data=f"edit:{pending_id}"),
        InlineKeyboardButton("❌ Reject",  callback_data=f"reject:{pending_id}"),
    ]])


def _skip_reason_keyboard(pending_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⏭ Skip (no reason)", callback_data=f"skip_reject:{pending_id}"),
    ]])


# ─── Pending store ────────────────────────────────────────────────────────────

def _store_pending(context: ContextTypes.DEFAULT_TYPE, pending_id: str, data: dict) -> None:
    context.bot_data.setdefault("pending", {})[pending_id] = data


def _get_pending(context: ContextTypes.DEFAULT_TYPE, pending_id: str) -> dict | None:
    return context.bot_data.get("pending", {}).get(pending_id)


def _del_pending(context: ContextTypes.DEFAULT_TYPE, pending_id: str) -> None:
    context.bot_data.get("pending", {}).pop(pending_id, None)


# ─── Media helpers ────────────────────────────────────────────────────────────

def _extract_msg(m) -> dict:
    if m.photo:
        return {"type": "photo",    "file_id": m.photo[-1].file_id,
                "caption": m.caption, "caption_entities": m.caption_entities}
    if m.video:
        return {"type": "video",    "file_id": m.video.file_id,
                "caption": m.caption, "caption_entities": m.caption_entities}
    if m.document:
        return {"type": "document", "file_id": m.document.file_id,
                "caption": m.caption, "caption_entities": m.caption_entities}
    if m.text:
        return {"type": "text", "text": m.text, "entities": m.entities}
    return {"type": "unsupported", "from_chat_id": m.chat_id, "message_id": m.message_id}


async def _send_to_owner(bot, msg: dict, header: str, pending_id: str) -> None:
    """Send the actual media to the owner with approval buttons."""
    kb  = _approval_keyboard(pending_id)
    cap = (msg.get("caption") or "")

    if msg["type"] == "text":
        await bot.send_message(chat_id=OWNER_ID,
                               text=f"{header}\n\n{msg.get('text','')[:300]}",
                               reply_markup=kb)
    elif msg["type"] == "photo":
        await bot.send_photo(chat_id=OWNER_ID, photo=msg["file_id"],
                             caption=f"{header}\n\n{cap}".strip()[:1024],
                             reply_markup=kb)
    elif msg["type"] == "video":
        await bot.send_video(chat_id=OWNER_ID, video=msg["file_id"],
                             caption=f"{header}\n\n{cap}".strip()[:1024],
                             reply_markup=kb)
    elif msg["type"] == "document":
        await bot.send_document(chat_id=OWNER_ID, document=msg["file_id"],
                                caption=f"{header}\n\n{cap}".strip()[:1024],
                                reply_markup=kb)
    else:
        await bot.send_message(chat_id=OWNER_ID,
                               text=f"{header}\n\n[Unsupported media]",
                               reply_markup=kb)


async def _post_to_channel(bot, msg: dict) -> None:
    """Post a message (original or edited) to the channel."""
    if msg["type"] == "text":
        await bot.send_message(chat_id=CHANNEL_ID, text=msg["text"],
                               entities=msg.get("entities"))
    elif msg["type"] == "photo":
        await bot.send_photo(chat_id=CHANNEL_ID, photo=msg["file_id"],
                             caption=msg.get("caption"),
                             caption_entities=msg.get("caption_entities"))
    elif msg["type"] == "video":
        await bot.send_video(chat_id=CHANNEL_ID, video=msg["file_id"],
                             caption=msg.get("caption"),
                             caption_entities=msg.get("caption_entities"))
    elif msg["type"] == "document":
        await bot.send_document(chat_id=CHANNEL_ID, document=msg["file_id"],
                                caption=msg.get("caption"),
                                caption_entities=msg.get("caption_entities"))
    else:
        await bot.forward_message(chat_id=CHANNEL_ID,
                                  from_chat_id=msg["from_chat_id"],
                                  message_id=msg["message_id"])


# ─── Command handlers ─────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        return
    if uid == OWNER_ID:
        await update.message.reply_text(
            "👋 *GSCF Channel Manager*\n\n"
            "Send me any post and I'll publish it to @gscfgs7baby after your confirmation.\n"
            "Admins send drafts here for your review.",
            parse_mode="Markdown")
    else:
        await update.message.reply_text(
            "👋 *GSCF Channel Manager*\n\n"
            "Send me the post you want published to @gscfgs7baby.\n"
            "The owner will review it and you'll be notified of the outcome.",
            parse_mode="Markdown")


async def receive_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        return

    msg = _extract_msg(update.message)
    if msg["type"] == "unsupported":
        await update.message.reply_text(
            "⚠️ Unsupported message type. Send text, photo, video or a file.")
        return

    pending_id = str(update.message.message_id)
    _store_pending(context, pending_id, {
        "msg": msg,
        "submitter_id": uid,
        "submitter_name": update.effective_user.full_name,
    })

    if uid == OWNER_ID:
        await _send_to_owner(context.bot, msg, "📤 Post to channel — confirm?", pending_id)
        await update.message.reply_text("✅ Queued for your confirmation.")
    else:
        u = update.effective_user
        header = f"📨 From {u.full_name} {'@' + u.username if u.username else ''} — approve, edit or reject?"
        await _send_to_owner(context.bot, msg, header, pending_id)
        await update.message.reply_text("📨 Sent to owner for approval. You'll be notified.")


# ─── Button / Conversation handlers ───────────────────────────────────────────

async def on_approve_or_edit_or_reject(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """Entry point for Approve, Edit and Reject buttons."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != OWNER_ID:
        await query.answer("Only the owner can do this.", show_alert=True)
        return ConversationHandler.END

    action, pending_id = query.data.split(":", 1)
    pending = _get_pending(context, pending_id)

    if not pending:
        await query.edit_message_caption("⚠️ Already handled.") if query.message.caption else \
            await query.edit_message_text("⚠️ Already handled.")
        return ConversationHandler.END

    submitter_id = pending["submitter_id"]
    msg          = pending["msg"]

    # ── Approve ──────────────────────────────────────────────────────────────
    if action == "approve":
        await _post_to_channel(context.bot, msg)
        _edit_approval_msg(query, "✅ Posted to @gscfgs7baby.")
        if submitter_id != OWNER_ID:
            await context.bot.send_message(chat_id=submitter_id,
                                           text="✅ Your post was approved and published!")
        _del_pending(context, pending_id)
        return ConversationHandler.END

    # ── Edit ─────────────────────────────────────────────────────────────────
    if action == "edit":
        context.user_data["editing_pending_id"] = pending_id
        _edit_approval_msg(query,
            "✏️ Send me the corrected version (text, photo, video or file).\n\n"
            "Send /cancel to abort.")
        return WAITING_EDIT

    # ── Reject — ask for reason ───────────────────────────────────────────────
    if action == "reject":
        context.user_data["rejecting_pending_id"] = pending_id
        _edit_approval_msg(query,
            "❌ Type your reason for rejecting this post, then send it.\n\n"
            "Or tap the button below to reject without giving a reason.",
            extra_kb=_skip_reason_keyboard(pending_id))
        return WAITING_REJECT_REASON

    return ConversationHandler.END


def _edit_approval_msg(query, text: str, extra_kb: InlineKeyboardMarkup | None = None) -> None:
    """Edit the caption or text of the approval message."""
    try:
        if query.message.caption is not None:
            query.message.edit_caption(caption=text, reply_markup=extra_kb)
        else:
            query.message.edit_text(text=text, reply_markup=extra_kb)
    except Exception:
        pass


async def receive_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Owner typed a rejection reason."""
    if update.effective_user.id != OWNER_ID:
        return WAITING_REJECT_REASON

    pending_id = context.user_data.get("rejecting_pending_id")
    pending    = _get_pending(context, pending_id) if pending_id else None

    if not pending:
        await update.message.reply_text("⚠️ No post is waiting for rejection.")
        return ConversationHandler.END

    reason       = update.message.text or ""
    submitter_id = pending["submitter_id"]

    await update.message.reply_text("❌ Post rejected with reason sent to admin.")

    if submitter_id != OWNER_ID:
        await context.bot.send_message(
            chat_id=submitter_id,
            text=f"❌ Your post was not approved.\n\n*Reason:* {reason}",
            parse_mode="Markdown",
        )

    _del_pending(context, pending_id)
    context.user_data.pop("rejecting_pending_id", None)
    return ConversationHandler.END


async def skip_reject_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Owner tapped 'Skip' — reject without a reason."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != OWNER_ID:
        return WAITING_REJECT_REASON

    _, pending_id = query.data.split(":", 1)
    pending       = _get_pending(context, pending_id)

    submitter_id = pending["submitter_id"] if pending else None

    _edit_approval_msg(query, "❌ Post rejected (no reason given).")

    if pending and submitter_id != OWNER_ID:
        await context.bot.send_message(
            chat_id=submitter_id,
            text="❌ Your post was reviewed but not approved for the channel.",
        )

    if pending:
        _del_pending(context, pending_id)
    context.user_data.pop("rejecting_pending_id", None)
    return ConversationHandler.END


async def receive_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Owner sends the corrected post."""
    if update.effective_user.id != OWNER_ID:
        return WAITING_EDIT

    pending_id = context.user_data.get("editing_pending_id")
    pending    = _get_pending(context, pending_id) if pending_id else None

    if not pending:
        await update.message.reply_text(
            "⚠️ No post is waiting for an edit. Tap Edit on the original message first.")
        return ConversationHandler.END

    edited_msg = _extract_msg(update.message)
    if edited_msg["type"] == "unsupported":
        await update.message.reply_text("⚠️ Unsupported type. Send text, photo, video or a file.")
        return WAITING_EDIT

    await _post_to_channel(context.bot, edited_msg)
    await update.message.reply_text("✅ Edited version posted to @gscfgs7baby.")

    if pending["submitter_id"] != OWNER_ID:
        await context.bot.send_message(
            chat_id=pending["submitter_id"],
            text="✅ Your post was approved (with edits) and published to the channel!",
        )

    _del_pending(context, pending_id)
    context.user_data.pop("editing_pending_id", None)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("editing_pending_id", None)
    context.user_data.pop("rejecting_pending_id", None)
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(on_approve_or_edit_or_reject,
                                 pattern=r"^(approve|edit|reject):"),
        ],
        states={
            WAITING_EDIT: [
                CommandHandler("cancel", cancel),
                MessageHandler(
                    filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL,
                    receive_edit,
                ),
            ],
            WAITING_REJECT_REASON: [
                CommandHandler("cancel", cancel),
                CallbackQueryHandler(skip_reject_reason, pattern=r"^skip_reject:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reject_reason),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True,
        per_chat=True,
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL,
        receive_post,
    ))

    logger.info("GSCF Channel Manager bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
