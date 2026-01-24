from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import logging
import os
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.token:
            logger.warning("Telegram token not found. Telegram notifications disabled.")
            self.bot = None
            self.app = None
            return

        self.bot = Bot(self.token)
        self.app = Application.builder().token(self.token).build()
        self._setup_handlers()
        
        # Start polling in background if standalone, otherwise webhook
        # For this implementation, we assume it runs within the existing asyncio loop
        # or as a separate service. Here we just prepare it.

    def _setup_handlers(self):
        """Setup command and callback handlers."""
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("status", self._cmd_status))
        self.app.add_handler(CommandHandler("pending", self._cmd_pending))
        self.app.add_handler(CallbackQueryHandler(self._handle_callback))

    async def initialize(self):
        """Initialize the application."""
        if self.app:
            await self.app.initialize()
            await self.app.start()
            logger.info("Telegram bot initialized")

    async def shutdown(self):
        """Shutdown the application."""
        if self.app:
            await self.app.stop()
            await self.app.shutdown()

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "👋 Hello! I am Abdullah Junior's notification bot.\n\n"
            "I will notify you of pending approvals and important updates.\n"
            "Use /status to check system status."
        )

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # In a real app, fetch from Orchestrator
        await update.message.reply_text(
            "🟢 **System Online**\n\n"
            "Pending Approvals: 3\n"
            "Completed Today: 12\n"
            "Agent Status: Idle",
            parse_mode="Markdown"
        )

    async def _cmd_pending(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Mock pending list
        await update.message.reply_text("Fetching pending approvals...")

    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button clicks."""
        query = update.callback_query
        await query.answer()

        data = query.data
        action, task_id = data.split("_", 1)

        if action == "approve":
            await query.edit_message_text(text=f"✅ Approved task {task_id}")
            # Call API to approve
            logger.info(f"Approved task {task_id} via Telegram")
            
        elif action == "reject":
            await query.edit_message_text(text=f"❌ Rejected task {task_id}")
            # Call API to reject
            logger.info(f"Rejected task {task_id} via Telegram")

    async def send_approval_request(
        self,
        task_id: str,
        title: str,
        description: str,
        priority: str = "medium"
    ):
        """Send approval request with inline buttons."""
        if not self.bot or not self.chat_id:
            return

        priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{task_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{task_id}")
            ]
        ])

        text = (
            f"🔔 *Approval Required*\n\n"
            f"{priority_emoji} *{title}*\n\n"
            f"{description[:200]}{'...' if len(description) > 200 else ''}"
        )

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")

    async def send_digest(self, summary: str):
        """Send daily digest."""
        if not self.bot or not self.chat_id:
            return
            
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=f"📊 *Daily Digest*\n\n{summary}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram digest: {e}")
