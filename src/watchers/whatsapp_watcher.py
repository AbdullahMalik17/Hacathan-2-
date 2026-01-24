# WhatsApp Watcher - Digital FTE Sensory System
# This script monitors WhatsApp Web for new messages using Playwright

import os
import sys
import json
import time
import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
except ImportError:
    print("Playwright not installed.")
    sys.exit(1)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Import contact manager
sys.path.append(str(PROJECT_ROOT / "src"))
try:
    from utils.contacts import is_known_contact, get_contact_info
except ImportError:
    def is_known_contact(name): return False
    def get_contact_info(name): return None

VAULT_PATH = PROJECT_ROOT / "Vault"
CONFIG_PATH = PROJECT_ROOT / "config"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"
WHATSAPP_DATA_DIR = CONFIG_PATH / "whatsapp_data"
WHATSAPP_QUEUE_PATH = VAULT_PATH / "WhatsApp_Queue"

# Polling configuration
POLL_INTERVAL = int(os.getenv("WHATSAPP_POLL_INTERVAL", "30"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
HEADLESS = os.getenv("WHATSAPP_HEADLESS", "false").lower() == "true"
AUTO_REPLY_ENABLED = os.getenv("WHATSAPP_AUTO_REPLY", "false").lower() == "true"

# Priority keywords
PRIORITY_KEYWORDS = {
    "urgent": ["urgent", "asap", "emergency", "immediately", "critical"],
    "high": ["important", "invoice", "payment", "deadline", "meeting", "client"],
    "medium": ["question", "request", "update", "information", "follow-up"],
    "low": ["thanks", "ok", "noted", "sure"]
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WhatsAppWatcher")

def ensure_directories():
    for path in [NEEDS_ACTION_PATH, LOGS_PATH, WHATSAPP_DATA_DIR, WHATSAPP_QUEUE_PATH]:
        path.mkdir(parents=True, exist_ok=True)

def determine_priority(message_text: str, is_known: bool = False) -> str:
    text = message_text.lower()
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            if is_known and priority == "medium":
                return "high"
            return priority
    return "medium"

def get_priority_emoji(priority: str, is_escalation: bool = False) -> str:
    if is_escalation: return "!"
    return {"urgent": "!!", "high": "!", "medium": "-", "low": "."}.get(priority, "-")

def redact_pii(text: str) -> str:
    """Redact phone numbers from text."""
    phone_pattern = r'\+?(\d[\d\s-]{8,}\d)'
    return re.sub(phone_pattern, '[REDACTED]', text)

def create_task_file(message_data: Dict[str, Any]) -> Optional[Path]:
    try:
        sender = message_data.get("sender", "Unknown")
        message = message_data.get("message", "")
        timestamp = message_data.get("timestamp", datetime.now().isoformat())
        chat_name = message_data.get("chat_name", sender)
        is_known = message_data.get("is_known", False)

        priority = determine_priority(message, is_known)
        is_escalation = not is_known and priority in ["urgent", "high"]
        priority_emoji = get_priority_emoji(priority, is_escalation)

        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        prefix = "ESCALATION" if is_escalation else "whatsapp"
        safe_sender = "".join(c if c.isalnum() or c in " -_" else "" for c in sender)[:30]
        filename = f"{time_str}_{prefix}_{priority}_{safe_sender}.md"
        filepath = NEEDS_ACTION_PATH / filename

        content = f"""# {priority_emoji} {prefix.upper()}: {chat_name}

## Metadata
- **Source:** WhatsApp
- **From:** {sender}
- **Known Contact:** {"Yes" if is_known else "No"}
- **Chat:** {chat_name}
- **Priority:** {priority.upper()}
- **Created:** {datetime.now().isoformat()}

---

## Message
{message}

---

## Suggested Actions
- [ ] Read message
"""
        if is_escalation:
            content += "- [ ] URGENT: Verify identity\n"
        
        content += "- [ ] Respond if needed\n"

        if DRY_RUN: return None
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

def log_action(action: str, details: Dict[str, Any]):
    safe_details = {k: redact_pii(str(v)) if isinstance(v, str) else v for k, v in details.items()}
    log_entry = {"timestamp": datetime.now().isoformat(), "action": action, **safe_details}
    log_file = LOGS_PATH / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    logs = []
    if log_file.exists():
        try: logs = json.loads(log_file.read_text())
        except: logs = []
    logs.append(log_entry)
    log_file.write_text(json.dumps(logs, indent=2))

class WhatsAppWatcher:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.processed_messages = set()
        self.is_authenticated = False

    async def start(self):
        """Initialize browser and log in to WhatsApp."""
        logger.info("Starting WhatsApp Watcher...")
        self.playwright = await async_playwright().start()
        
        # Launch browser with persistence
        # Note: launch_persistent_context returns a context, not a browser object in the traditional sense
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(WHATSAPP_DATA_DIR),
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
            viewport={"width": 1280, "height": 800}
        )
        
        # Persistent context starts with one page
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        
        await self.page.goto("https://web.whatsapp.com", timeout=60000, wait_until="domcontentloaded")
        
        # Wait for authentication
        logger.info("Waiting for authentication...")
        try:
            # Race between success (chat list) and needs auth (QR code)
            # We use a longer timeout for the user to scan the QR code if it appears
            
            # First, wait for the page to load enough to show either
            await self.page.wait_for_load_state("domcontentloaded", timeout=60000)
            
            try:
                # Check if we are already logged in (chat list visible immediately)
                await self.page.wait_for_selector('div[data-testid="chat-list-search"]', timeout=10000)
                self.is_authenticated = True
                logger.info("✅ Authentication successful (Session restored)")
                return
            except:
                pass
                
            # If not immediately logged in, look for QR code or wait for login
            logger.info("Session not restored immediately. Checking for QR code...")
            
            # Wait up to 2 minutes for user to scan QR code if needed
            # Check for multiple possible success indicators
            login_success_selectors = [
                'div[data-testid="chat-list-search"]',
                'div[data-testid="menu-bar-chat-list"]', 
                'span[data-testid="chat"]',
                'header[data-testid="chat-list-header"]',
                'div[id="pane-side"]'
            ]
            
            logger.info("Waiting for login success indicators...")
            # Create a combined selector or loop through them
            # Playwright doesn't support "OR" in waitForSelector easily with different types, 
            # so we'll poll for them.
            
            start_time = time.time()
            while time.time() - start_time < 120:
                for selector in login_success_selectors:
                    try:
                        if await self.page.query_selector(selector):
                            self.is_authenticated = True
                            logger.info(f"✅ Authentication successful (Found {selector})")
                            return
                    except:
                        pass
                await asyncio.sleep(1)
                
            raise TimeoutError("Login indicators not found after 120s")
            
        except Exception as e:
            self.is_authenticated = False
            logger.warning(f"⚠️ Authentication failed or timed out: {e}")
            
            # Take debug screenshot
            try:
                debug_shot = LOGS_PATH / f"whatsapp_login_fail_{datetime.now().strftime('%H%M%S')}.png"
                await self.page.screenshot(path=str(debug_shot))
                logger.info(f"Saved debug screenshot to {debug_shot}")
            except Exception as s_e:
                logger.error(f"Could not take screenshot: {s_e}")

            # Notification logic (FR-005)
            self._notify_auth_needed()

    def _notify_auth_needed(self):
        """Notify user that authentication is required."""
        # Create a task in Needs_Action
        alert_file = NEEDS_ACTION_PATH / f"ALERT_WhatsApp_Auth_{datetime.now().strftime('%H%M')}.md"
        content = """# ⚠️ WhatsApp Authentication Required

The WhatsApp Watcher cannot log in. 

## Action Required
1. Open the server VNC/Display
2. Scan the QR code on the WhatsApp Web window
3. Or restart the watcher in non-headless mode

**Status:** Critical - Messaging Halted
"""
        with open(alert_file, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.warning("Created auth alert task")

    async def get_unread_chats(self) -> List[Dict[str, Any]]:
        """Scan for unread messages."""
        if not self.is_authenticated:
            return []

        messages = []
        try:
            # Look for unread badges
            unread_selectors = await self.page.query_selector_all('span[aria-label*="unread"]')

            for badge in unread_selectors:
                try:
                    # Get parent container to find chat name
                    parent_handle = await badge.evaluate_handle('el => el.closest("div[role=\'listitem\']")')
                    parent = parent_handle.as_element()
                    if not parent: continue

                    # Extract chat name
                    chat_name_el = await parent.query_selector('span[title]')
                    chat_name = await chat_name_el.get_attribute('title') if chat_name_el else "Unknown"

                    # Try to extract message preview
                    message_preview = "New unread messages detected"
                    try:
                        # Look for message text in the chat list item
                        preview_selectors = [
                            'span[title]:not([aria-label])',  # Message preview text
                            'span.selectable-text',            # Alternative selector
                            'div._11JPr span'                  # Last message span
                        ]

                        for selector in preview_selectors:
                            preview_el = await parent.query_selector(selector)
                            if preview_el:
                                preview_text = await preview_el.inner_text()
                                if preview_text and preview_text != chat_name and len(preview_text) > 0:
                                    message_preview = preview_text[:200]  # Limit length
                                    break
                    except Exception as e:
                        logger.debug(f"Could not extract message preview for {chat_name}: {e}")

                    messages.append({
                        "sender": chat_name,
                        "chat_name": chat_name,
                        "message": message_preview,
                        "timestamp": datetime.now().isoformat(),
                        "is_known_contact": is_known_contact(chat_name),
                        "msg_id": f"{chat_name}_{datetime.now().timestamp()}"
                    })
                except Exception as e:
                    logger.warning(f"Error processing unread badge: {e}")

        except Exception as e:
            logger.error(f"Error scanning unread chats: {e}")

        return messages

    async def _send_message(self, chat_name: str, text: str) -> bool:
        """Send a message to a specific chat (active sending)."""
        if DRY_RUN:
            logger.info(f"[DRY RUN] Would send to {chat_name}: {text}")
            return True

        if not self.is_authenticated:
            logger.error("Cannot send: Not authenticated")
            return False

        try:
            # Search for chat
            search_box = 'div[contenteditable="true"][data-tab="3"]'
            
            # Wait for search box
            await self.page.wait_for_selector(search_box, timeout=5000)
            
            await self.page.fill(search_box, chat_name)
            await asyncio.sleep(2) # Wait for search results
            await self.page.press(search_box, "Enter")
            await asyncio.sleep(1)

            # Type message
            input_selector = 'div[contenteditable="true"][data-tab="10"]' 
            try:
                await self.page.wait_for_selector(input_selector, timeout=5000)
            except:
                # Fallback
                input_selector = 'div[data-testid="conversation-compose-box-input"]'
                await self.page.wait_for_selector(input_selector, timeout=5000)

            await self.page.fill(input_selector, text)
            await asyncio.sleep(0.5)
            await self.page.press(input_selector, "Enter")
            
            logger.info(f"Sent message to {chat_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {chat_name}: {e}")
            return False

    async def process_outbox(self):
        """Process messages in the WhatsApp Queue."""
        if not self.is_authenticated: return

        queue_files = list(WHATSAPP_QUEUE_PATH.glob("SEND_*.md"))
        for file in queue_files:
            try:
                content = file.read_text(encoding='utf-8')
                
                recipient = None
                message_body = content
                
                # Check for frontmatter
                if content.startswith("---"):
                    try:
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            yaml_content = parts[1]
                            body_content = parts[2].strip()
                            
                            for line in yaml_content.splitlines():
                                if line.startswith("to:"):
                                    recipient = line.split(":", 1)[1].strip()
                            
                            message_body = body_content
                    except:
                        pass
                
                if not recipient:
                    # Fallback to filename parsing
                    match = re.search(r"SEND_to_(.*?)_\d+", file.name)
                    if match:
                        recipient = match.group(1).replace("_", " ")
                
                if recipient and message_body:
                    logger.info(f"Processing outbox message to {recipient}")
                    success = await self._send_message(recipient, message_body)
                    
                    if success:
                        # Move to Done
                        done_path = VAULT_PATH / "Done" / file.name
                        file.rename(done_path)
                        log_action("whatsapp_sent", {"recipient": recipient, "file": file.name})
                    else:
                        logger.warning(f"Failed to send to {recipient}")
            except Exception as e:
                logger.error(f"Error processing outbox file {file.name}: {e}")

    async def run(self):
        ensure_directories()
        await self.start()
        logger.info(f"WhatsApp Watcher Running (Poll: {POLL_INTERVAL}s)")
        
        while True:
            try:
                # 1. Process Incoming
                unread = await self.get_unread_chats()
                for msg in unread:
                    if msg.get("msg_id") not in self.processed_messages:
                        filepath = create_task_file(msg)
                        if filepath:
                            self.processed_messages.add(msg.get("msg_id"))
                            log_action("whatsapp_received", {"chat": msg.get("chat_name")})
                
                # 2. Process Outbox
                await self.process_outbox()

            except Exception as e: 
                logger.error(f"Loop Error: {e}")
                
            await asyncio.sleep(POLL_INTERVAL)


async def main():
    watcher = WhatsAppWatcher()
    try:
        await watcher.run()
    except KeyboardInterrupt:
        logger.info("Stopping...")
        if watcher.context:
            await watcher.context.close()
        elif watcher.browser:
            await watcher.browser.close()

if __name__ == "__main__":
    asyncio.run(main())