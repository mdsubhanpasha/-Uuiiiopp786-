import os
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from loguru import logger

try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot v20 not installed.")

class TelegramApprovalBot:
    """
    Layer 3 - Human-in-the-Loop Approval Telegram Bot:
    - Sends formatted post card with virality score & predicted views
    - Inline Keyboard buttons:
      [✅ Approve & Schedule 9:30 AM IST] [❌ Reject] [✏️ Rewrite Hook] [🔄 Regenerate Image]
    - Calls FastAPI endpoints to execute schedule, rejection, hook rewrite, or image regeneration.
    """

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None, api_url: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self.api_url = api_url or os.getenv("API_URL", "http://localhost:8000")
        self.app = None

        if TELEGRAM_AVAILABLE and self.token and not self.token.startswith("123456789"):
            try:
                self.app = Application.builder().token(self.token).build()
                self._setup_handlers()
            except Exception as e:
                logger.warning(f"Could not build Telegram bot: {e}")

    def _setup_handlers(self):
        if not self.app:
            return
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("generate", self._cmd_generate))
        self.app.add_handler(CommandHandler("queue", self._cmd_queue))
        self.app.add_handler(CallbackQueryHandler(self._handle_button))

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🚀 PASHA-UNIFIED-OS Telegram Bot Online!\n"
            "Use /generate to run the multi-agent engine or /queue to view pending approvals."
        )

    async def _cmd_generate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("⏳ Running LangGraph 4-Node Generation Engine...")
        try:
            res = requests.post(f"{self.api_url}/generate", json={}, timeout=30)
            if res.status_code == 200:
                data = res.json()
                post = data.get("post", {})
                await self.send_post_approval_card(post)
            else:
                await update.message.reply_text(f"❌ Error generating post: {res.text}")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to reach API: {e}")

    async def _cmd_queue(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            res = requests.get(f"{self.api_url}/posts/pending", timeout=10)
            if res.status_code == 200:
                posts = res.json().get("posts", [])
                if not posts:
                    await update.message.reply_text("✅ No pending posts in approval queue!")
                    return
                for p in posts:
                    await self.send_post_approval_card(p)
            else:
                await update.message.reply_text(f"❌ Error fetching queue: {res.text}")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to reach API: {e}")

    async def send_post_approval_card(self, post: Dict[str, Any]):
        if not self.app or not self.chat_id:
            logger.warning("Telegram bot not configured for card dispatch.")
            return

        post_id = post.get("id", 1)
        score = post.get("virality_score", 88)
        predicted_views = post.get("predicted_views", "5k-8k views")
        topic = post.get("topic", "")
        angle = post.get("angle", "")
        full_text = post.get("full_text", "")
        sources = post.get("source_urls", "https://arxiv.org")

        card_text = (
            f"🔥 *New Post Ready for Review* | Score: *{score}/100*\n"
            f"📊 *Predicted:* {predicted_views}\n\n"
            f"📌 *Topic:* {topic}\n"
            f"🎯 *Angle:* {angle}\n\n"
            f"```text\n{full_text}\n```\n\n"
            f"🔗 *Sources:* {sources}"
        )

        keyboard = [
            [
                InlineKeyboardButton("✅ Approve & Schedule 9:30 AM IST", callback_data=f"approve_{post_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{post_id}")
            ],
            [
                InlineKeyboardButton("✏️ Rewrite Hook", callback_data=f"rewrite_{post_id}"),
                InlineKeyboardButton("🔄 Regenerate Image", callback_data=f"reimage_{post_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        image_url = post.get("image_url", "")
        if image_url and os.path.exists(image_url):
            with open(image_url, "rb") as photo:
                await self.app.bot.send_photo(
                    chat_id=self.chat_id,
                    photo=photo,
                    caption=card_text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
        else:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=card_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

    async def _handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        data = query.data
        action, post_id_str = data.split("_", 1)
        post_id = int(post_id_str)

        if action == "approve":
            # Schedule for next day 9:30 AM IST (UTC+5:30)
            now_utc = datetime.now(timezone.utc)
            ist_tz = timezone(timedelta(hours=5, minutes=30))
            now_ist = now_utc.astimezone(ist_tz)
            scheduled_ist = (now_ist + timedelta(days=1)).replace(hour=9, minute=30, second=0, microsecond=0)
            scheduled_iso = scheduled_ist.isoformat()

            res = requests.post(f"{self.api_url}/approve", json={"post_id": post_id, "scheduled_time": scheduled_iso})
            if res.status_code == 200:
                await query.edit_message_reply_markup(reply_markup=None)
                await query.message.reply_text(f"✅ *Post #{post_id} Approved & Scheduled for 9:30 AM IST!*", parse_mode="Markdown")
            else:
                await query.message.reply_text(f"❌ Failed to approve post #{post_id}: {res.text}")

        elif action == "reject":
            res = requests.post(f"{self.api_url}/reject", json={"post_id": post_id, "feedback": "Rejected via Telegram"})
            if res.status_code == 200:
                await query.edit_message_reply_markup(reply_markup=None)
                await query.message.reply_text(f"❌ *Post #{post_id} Rejected & Removed.*", parse_mode="Markdown")
            else:
                await query.message.reply_text(f"❌ Failed to reject post #{post_id}: {res.text}")

        elif action == "rewrite":
            await query.message.reply_text(f"🔄 Rewriting hook for Post #{post_id}...")
            res = requests.post(f"{self.api_url}/rewrite-hook", json={"post_id": post_id, "instructions": "Make hook punchier with high tension"})
            if res.status_code == 200:
                updated_post = res.json().get("post", {})
                await self.send_post_approval_card(updated_post)

        elif action == "reimage":
            await query.message.reply_text(f"🎨 Regenerating DALL-E 3 image for Post #{post_id}...")
            res = requests.post(f"{self.api_url}/regenerate-image", json={"post_id": post_id})
            if res.status_code == 200:
                updated_post = res.json().get("post", {})
                await self.send_post_approval_card(updated_post)

    def run_polling(self):
        if self.app:
            logger.info("Starting Telegram Bot polling...")
            self.app.run_polling()

    def send_post_approval_sync(self, post: Dict[str, Any]):
        """Synchronous helper using HTTP Telegram Bot API directly."""
        if not self.token or self.token.startswith("123456789") or not self.chat_id:
            logger.info("Telegram Bot token/chat_id not set. Skipping Telegram notification.")
            return False

        post_id = post.get("id", 1)
        score = post.get("virality_score", 88)
        predicted_views = post.get("predicted_views", "5k-8k views")
        topic = post.get("topic", "")
        full_text = post.get("full_text", "")

        msg = (
            f"🔥 *New Post Ready for Review* | Score: *{score}/100*\n"
            f"📊 *Predicted:* {predicted_views}\n"
            f"📌 *Topic:* {topic}\n\n"
            f"{full_text}\n\n"
            f"Approve or manage in Streamlit Dashboard!"
        )

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        try:
            res = requests.post(url, json={"chat_id": self.chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=10)
            return res.status_code == 200
        except Exception as e:
            logger.error(f"Error sending sync Telegram message: {e}")
            return False
