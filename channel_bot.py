"""GSCF Channel Manager Bot.

Workflow:
  1. Admin (@Onlyfewisreal) sends any post (text, photo, video, document) to the bot.
  2. Bot forwards it to the owner (7800993199) with Approve / Edit / Reject buttons.
  3. Owner taps Approve  → bot posts to @gscfgs7baby as-is.
  4. Owner taps Edit     → bot asks owner to send the corrected version,
                           then posts the corrected version to the channel.
  5. Owner taps Reject   → bot notifies the admin the post was rejected.
  6. Owner can also submit posts directly — they go straight to channel
     after confirmation.
"""

from __future__ import annotations

import logging
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="telegram")

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
)
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
BOT_TOKEN   = "8488113072:AAHG5kg7XZ0PseN0Q1X_8xkm5F4ki70QV0g"
CHANNEL_ID  = "@gscfgs7baby"
OWNER_ID    = 7800993199   # approves / edits / rejects
ADMIN_IDS   = {7800993199, 6162101530}  # who can submit posts

# ConversationHandler state
WAITING_EDIT = 1

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _approval_keyboard(pending_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve",  callback_data=f"approve:{pending_id}"),
            InlineKeyboardButton("✏️ Edit",     callback_data=f"edit:{pending_id}"),
            InlineKeyboardButton("❌ Reject",   callback_data=f"reject:{pending_id}"),
        ]
    ])


def _store_pending(context: ContextTypes.DEFAULT_TYPE, pending_id: str, data: dict) -> None:
    context.bot_data.setdefault("pending", {})[pending_id] = data


def _get_pending(context: ContextTypes.DEFAULT_TYPE, pending_id: str) -> dict | None:
    return context.bot_data.get("pending", {}).get(pending_id)


def _del_pending(context: ContextTypes.DEFAULT_TYPE, pending_id: str) -> None:
    context.bot_data.get("pending", {}).pop(pending_id, None)


async def _forward_to_channel(bot, msg) -> None:
    """Post a message (original or edited) to the channel."""
    if msg.get("type") == "text":
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=msg["text"],
            entities=msg.get("entities"),
            parse_mode=None,
        )
    elif msg.get("type") == "photo":
        await bot.send_photo(
            chat_id=CHANNEL_ID,
            photo=msg["file_id"],
            caption=msg.get("caption"),
            caption_entities=msg.get("caption_entities"),
        )
    elif msg.get("type") == "video":
        await bot.send_video(
            chat_id=CHANNEL_ID,
            video=msg["file_id"],
            caption=msg.get("caption"),
            caption_entities=msg.get("caption_entities"),
        )
    elif msg.get("type") == "document":
        await bot.send_document(
            chat_id=CHANNEL_ID,
            document=msg["file_id"],
            caption=msg.get("caption"),
            caption_entities=msg.get("caption_entities"),
        )
    else:
        # Fallback: forward the original telegram message
        await bot.forward_message(
            chat_id=CHANNEL_ID,
            from_chat_id=msg["from_chat_id"],
            message_id=msg["message_id"],
        )


def _extract_msg(update_message) -> dict:
    """Extract a portable message dict from a Telegram Message object."""
    m = update_message
    if m.photo:
        return {
            "type": "photo",
            "file_id": m.photo[-1].file_id,
            "caption": m.caption,
            "caption_entities": m.caption_entities,
        }
    if m.video:
        return {
            "type": "video",
            "file_id": m.video.file_id,
            "caption": m.caption,
            "caption_entities": m.caption_entities,
        }
    if m.document:
        return {
            "type": "document",
            "file_id": m.document.file_id,
            "caption": m.caption,
            "caption_entities": m.caption_entities,
        }
    if m.text:
        return {
            "type": "text",
            "text": m.text,
            "entities": m.entities,
        }
    # Unsupported type — store enough for a raw forward
    return {
        "type": "unsupported",
        "from_chat_id": m.chat_id,
        "message_id": m.message_id,
    }


def _preview_text(msg: dict) -> str:
    if msg["type"] == "text":
        text = msg.get("text", "")
        return text[:300] + ("…" if len(text) > 300 else "")
    cap = msg.get("caption") or ""
    return f"[{msg['type'].upper()}]" + (f"\n{cap[:200]}" if cap else "")


# ─── Handlers ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        return
    if uid == OWNER_ID:
        await update.message.reply_text(
            "👋 *GSCF Channel Manager*\n\n"
            "Send me any post and I'll publish it straight to @gscfgs7baby after you confirm.\n"
            "Admins can also send drafts here for your approval.",
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            "👋 *GSCF Channel Manager*\n\n"
            "Send me the post you want published to @gscfgs7baby.\n"
            "The owner will review and approve it.",
            parse_mode="Markdown",
        )


async def receive_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Called when an admin sends a draft post."""
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        return

    msg = _extract_msg(update.message)

    if msg["type"] == "unsupported":
        await update.message.reply_text("⚠️ This message type isn't supported yet. Send text, photo, video or a file.")
        return

    pending_id = str(update.message.message_id)
    _store_pending(context, pending_id, {
        "msg": msg,
        "submitter_id": uid,
        "submitter_name": update.effective_user.full_name,
    })

    # Owner sent it themselves → ask for direct confirmation
    if uid == OWNER_ID:
        preview = _preview_text(msg)
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"📤 *Post to channel:*\n\n{preview}\n\nConfirm?",
            parse_mode="Markdown",
            reply_markup=_approval_keyboard(pending_id),
        )
        await update.message.reply_text("✅ Queued for your confirmation.")
        return

    # Another admin submitted → forward to owner for approval
    preview = _preview_text(msg)
    submitter = update.effective_user
    name = submitter.full_name
    username = f"@{submitter.username}" if submitter.username else ""

    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=(
            f"📨 *New post from {name} {username}:*\n\n"
            f"{preview}\n\n"
            f"Approve, edit or reject?"
        ),
        parse_mode="Markdown",
        reply_markup=_approval_keyboard(pending_id),
    )
    await update.message.reply_text("📨 Sent to owner for approval. You'll be notified.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int | None:
    """Handle Approve / Edit / Reject button taps."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != OWNER_ID:
        await query.answer("Only the owner can do this.", show_alert=True)
        return None

    action, pending_id = query.data.split(":", 1)
    pending = _get_pending(context, pending_id)

    if not pending:
        await query.edit_message_text("⚠️ This post is no longer available (already handled).")
        return None

    submitter_id   = pending["submitter_id"]
    submitter_name = pending["submitter_name"]
    msg            = pending["msg"]

    # ── Approve ──────────────────────────────────────────────────────────────
    if action == "approve":
        await _forward_to_channel(context.bot, msg)
        await query.edit_message_text("✅ Posted to @gscfgs7baby.")
        if submitter_id != OWNER_ID:
            await context.bot.send_message(
                chat_id=submitter_id,
                text="✅ Your post was approved and published to the channel!",
            )
        _del_pending(context, pending_id)
        return None

    # ── Reject ───────────────────────────────────────────────────────────────
    if action == "reject":
        await query.edit_message_text("❌ Post rejected.")
        if submitter_id != OWNER_ID:
            await context.bot.send_message(
                chat_id=submitter_id,
                text="❌ Your post was reviewed but not approved for the channel.",
            )
        _del_pending(context, pending_id)
        return None

    # ── Edit ─────────────────────────────────────────────────────────────────
    if action == "edit":
        context.user_data["editing_pending_id"] = pending_id
        await query.edit_message_text(
            "✏️ Send me the corrected version of the post (text, photo, video or file).\n\n"
            "Send /cancel to abort."
        )
        return WAITING_EDIT

    return None


async def receive_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Owner sends the corrected post."""
    if update.effective_user.id != OWNER_ID:
        return WAITING_EDIT

    pending_id = context.user_data.get("editing_pending_id")
    pending    = _get_pending(context, pending_id) if pending_id else None

    if not pending:
        await update.message.reply_text("⚠️ No post is waiting for an edit. Tap Edit on the original message first.")
        return ConversationHandler.END

    edited_msg     = _extract_msg(update.message)
    submitter_id   = pending["submitter_id"]

    if edited_msg["type"] == "unsupported":
        await update.message.reply_text("⚠️ Unsupported type. Send text, photo, video or a file.")
        return WAITING_EDIT

    await _forward_to_channel(context.bot, edited_msg)
    await update.message.reply_text("✅ Edited version posted to @gscfgs7baby.")

    if submitter_id != OWNER_ID:
        await context.bot.send_message(
            chat_id=submitter_id,
            text="✅ Your post was approved (with edits) and published to the channel!",
        )

    _del_pending(context, pending_id)
    context.user_data.pop("editing_pending_id", None)
    return ConversationHandler.END


async def cancel_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("editing_pending_id", None)
    await update.message.reply_text("✏️ Edit cancelled.")
    return ConversationHandler.END


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    edit_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern=r"^edit:")],
        states={
            WAITING_EDIT: [
                CommandHandler("cancel", cancel_edit),
                MessageHandler(
                    filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL,
                    receive_edit,
                ),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_edit)],
        per_user=True,
        per_chat=True,
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(edit_conv)
    app.add_handler(CallbackQueryHandler(button_handler, pattern=r"^(approve|reject):"))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL,
        receive_post,
    ))

    logger.info("GSCF Channel Manager bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
