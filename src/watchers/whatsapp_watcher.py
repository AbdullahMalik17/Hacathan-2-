"""
WhatsApp Watcher - Digital FTE Sensory System

This script monitors WhatsApp Web for new messages using Playwright
browser automation and creates markdown task files in the Obsidian vault.

Setup:
1. Install Playwright: pip install playwright
2. Install browser: playwright install chromium
3. Run script and scan QR code to authenticate
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    from playwright.async_api import async_playwright, Browser, Page
except ImportError:
    print("Playwright not installed. Run:")
    print("pip install playwright")
    print("playwright install chromium")
    sys.exit(1)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
CONFIG_PATH = PROJECT_ROOT / "config"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"
WHATSAPP_DATA_DIR = CONFIG_PATH / "whatsapp_data"

# Polling configuration
POLL_INTERVAL = int(os.getenv("WHATSAPP_POLL_INTERVAL", "30"))  # seconds
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
HEADLESS = os.getenv("WHATSAPP_HEADLESS", "false").lower() == "true"

# Priority keywords
PRIORITY_KEYWORDS = {
    "urgent": ["urgent", "asap", "emergency", "immediately", "critical"],
    "high": ["important", "invoice", "payment", "deadline", "meeting", "client"],
    "medium": ["question", "request", "update", "information", "follow-up"],
    "low": ["thanks", "ok", "noted", "sure", "👍"]
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WhatsAppWatcher")


def ensure_directories():
    """Ensure all required directories exist."""
    for path in [NEEDS_ACTION_PATH, LOGS_PATH, WHATSAPP_DATA_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def determine_priority(message_text: str) -> str:
    """Determine message priority based on keywords."""
    text = message_text.lower()

    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return priority

    return "medium"


def get_priority_emoji(priority: str) -> str:
    """Get emoji for priority level."""
    return {
        "urgent": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }.get(priority, "🟡")


def create_task_file(message_data: Dict[str, Any]) -> Optional[Path]:
    """Create a markdown task file for the WhatsApp message."""
    try:
        sender = message_data.get("sender", "Unknown")
        message = message_data.get("message", "")
        timestamp = message_data.get("timestamp", datetime.now().isoformat())
        chat_name = message_data.get("chat_name", sender)

        # Determine priority
        priority = determine_priority(message)
        priority_emoji = get_priority_emoji(priority)

        # Generate filename
        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        safe_sender = "".join(c if c.isalnum() or c in " -_" else "" for c in sender)[:30]
        filename = f"{time_str}_whatsapp_{priority}_{safe_sender}.md"
        filepath = NEEDS_ACTION_PATH / filename

        # Truncate long messages
        message_preview = message[:200] + "..." if len(message) > 200 else message

        # Create markdown content
        content = f"""# {priority_emoji} WhatsApp: {chat_name}

## Metadata
- **Source:** WhatsApp
- **From:** {sender}
- **Chat:** {chat_name}
- **Time:** {timestamp}
- **Priority:** {priority.upper()}
- **Created:** {datetime.now().isoformat()}

---

## Message
{message}

---

## Suggested Actions
- [ ] Read and understand the message
- [ ] Determine if response is needed
- [ ] Draft response (if applicable)
- [ ] Mark as handled

---

## Decision Required
- [ ] **No action needed** - Archive this message
- [ ] **Reply needed** - Draft response for approval
- [ ] **Forward to human** - Requires immediate attention
- [ ] **Schedule follow-up** - Set reminder for later

---

## Notes
_Add any notes or context here_

"""

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would create: {filepath}")
            return None

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created task file: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Error creating task file: {e}")
        return None


def log_action(action: str, details: Dict[str, Any]):
    """Log action to daily log file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "actor": "whatsapp_watcher",
        **details
    }

    log_file = LOGS_PATH / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text())
        except json.JSONDecodeError:
            logs = []

    logs.append(log_entry)
    log_file.write_text(json.dumps(logs, indent=2))


class WhatsAppWatcher:
    """WhatsApp Web watcher using Playwright."""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.processed_messages: set = set()
        self.is_authenticated = False

    async def start(self):
        """Start the browser and navigate to WhatsApp Web."""
        logger.info("Starting WhatsApp Watcher...")

        playwright = await async_playwright().start()

        # Use persistent context to maintain login
        self.browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(WHATSAPP_DATA_DIR),
            headless=HEADLESS,
            args=['--disable-blink-features=AutomationControlled']
        )

        # Get or create page
        if self.browser.pages:
            self.page = self.browser.pages[0]
        else:
            self.page = await self.browser.new_page()

        # Navigate to WhatsApp Web
        await self.page.goto("https://web.whatsapp.com")
        logger.info("Navigated to WhatsApp Web")

        # Wait for either QR code or chat list
        await self.wait_for_auth()

    async def wait_for_auth(self):
        """Wait for user to authenticate via QR code."""
        logger.info("Waiting for authentication...")

        try:
            # Wait for main chat panel (indicates logged in)
            await self.page.wait_for_selector(
                'div[data-testid="chat-list"]',
                timeout=120000  # 2 minutes to scan QR
            )
            self.is_authenticated = True
            logger.info("Successfully authenticated with WhatsApp Web!")

        except Exception as e:
            logger.warning(f"Authentication timeout or error: {e}")
            logger.info("Please scan the QR code in the browser window")

            # Create alert task for user
            create_task_file({
                "sender": "System",
                "chat_name": "WhatsApp Watcher Alert",
                "message": "WhatsApp Web requires authentication. Please scan the QR code in the browser window to continue monitoring.",
                "timestamp": datetime.now().isoformat()
            })

    async def get_unread_chats(self) -> List[Dict[str, Any]]:
        """Get list of chats with unread messages."""
        if not self.is_authenticated:
            return []

        unread_messages = []

        try:
            # Find chats with unread indicators
            unread_badges = await self.page.query_selector_all(
                'span[data-testid="icon-unread-count"]'
            )

            for badge in unread_badges:
                try:
                    # Get parent chat element
                    chat_element = await badge.evaluate_handle(
                        'el => el.closest(\'div[data-testid="cell-frame-container"]\')'
                    )

                    if chat_element:
                        # Extract chat info
                        chat_name_el = await chat_element.query_selector(
                            'span[data-testid="cell-frame-title"]'
                        )
                        last_msg_el = await chat_element.query_selector(
                            'span[data-testid="last-msg-status"]'
                        )

                        chat_name = await chat_name_el.inner_text() if chat_name_el else "Unknown"
                        last_msg = await last_msg_el.inner_text() if last_msg_el else ""

                        # Create message ID to track processed messages
                        msg_id = f"{chat_name}_{last_msg[:50]}"

                        if msg_id not in self.processed_messages:
                            unread_messages.append({
                                "chat_name": chat_name,
                                "sender": chat_name,
                                "message": last_msg,
                                "timestamp": datetime.now().isoformat(),
                                "msg_id": msg_id
                            })

                except Exception as e:
                    logger.debug(f"Error processing chat element: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error getting unread chats: {e}")

        return unread_messages

    async def check_session_valid(self) -> bool:
        """Check if WhatsApp Web session is still valid."""
        try:
            # Check for QR code (indicates logged out)
            qr_code = await self.page.query_selector('canvas[aria-label="Scan me!"]')
            if qr_code:
                self.is_authenticated = False
                logger.warning("Session expired - QR code detected")
                return False

            # Check for chat list (indicates logged in)
            chat_list = await self.page.query_selector('div[data-testid="chat-list"]')
            return chat_list is not None

        except Exception as e:
            logger.error(f"Error checking session: {e}")
            return False

    async def run(self):
        """Main watcher loop."""
        logger.info("=" * 50)
        logger.info("WhatsApp Watcher Starting...")
        logger.info(f"Poll Interval: {POLL_INTERVAL} seconds")
        logger.info(f"Dry Run: {DRY_RUN}")
        logger.info(f"Headless: {HEADLESS}")
        logger.info("=" * 50)

        ensure_directories()
        await self.start()

        while True:
            try:
                # Check session validity
                if not await self.check_session_valid():
                    logger.warning("Session invalid, waiting for re-auth...")
                    await self.wait_for_auth()
                    continue

                # Get unread messages
                logger.debug("Checking for new messages...")
                unread = await self.get_unread_chats()

                for msg in unread:
                    msg_id = msg.get("msg_id")

                    # Check priority keywords
                    priority = determine_priority(msg.get("message", ""))

                    # Only process high-priority messages or all if configured
                    if priority in ["urgent", "high"] or os.getenv("WHATSAPP_ALL_MESSAGES", "false").lower() == "true":
                        logger.info(f"Processing message from: {msg.get('chat_name')}")

                        filepath = create_task_file(msg)

                        if filepath:
                            self.processed_messages.add(msg_id)
                            log_action("whatsapp_message_processed", {
                                "chat": msg.get("chat_name"),
                                "priority": priority,
                                "task_file": str(filepath),
                                "result": "success"
                            })
                    else:
                        # Mark as processed but don't create task
                        self.processed_messages.add(msg_id)
                        logger.debug(f"Skipping low-priority message from: {msg.get('chat_name')}")

                # Clean up old processed IDs (keep last 500)
                if len(self.processed_messages) > 500:
                    self.processed_messages = set(list(self.processed_messages)[-500:])

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                log_action("error", {
                    "error": str(e),
                    "result": "failure"
                })

            await asyncio.sleep(POLL_INTERVAL)

    async def stop(self):
        """Stop the watcher and close browser."""
        if self.browser:
            await self.browser.close()
        logger.info("WhatsApp Watcher stopped")


async def main():
    """Entry point."""
    watcher = WhatsAppWatcher()

    try:
        await watcher.run()
    except KeyboardInterrupt:
        logger.info("Stopping WhatsApp Watcher...")
        await watcher.stop()


if __name__ == "__main__":
    asyncio.run(main())
