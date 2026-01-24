"""
LinkedIn Watcher - Digital FTE Sensory System

This script monitors LinkedIn for new notifications and messages using Playwright
browser automation and creates markdown task files in the Obsidian vault.

Setup:
1. Ensure Playwright is installed (pip install playwright)
2. Ensure you have logged in via the LinkedIn Poster or manually to populate session
"""

import os
import sys
import json
import time
import asyncio
import logging
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
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
LINKEDIN_DATA_DIR = CONFIG_PATH / "linkedin_data"

# Polling configuration
POLL_INTERVAL = int(os.getenv("LINKEDIN_POLL_INTERVAL", "300"))  # 5 minutes default
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
HEADLESS = os.getenv("LINKEDIN_HEADLESS", "false").lower() == "true"

# URLs
LINKEDIN_BASE_URL = "https://www.linkedin.com"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"
LINKEDIN_NOTIFICATIONS_URL = "https://www.linkedin.com/notifications/"
LINKEDIN_MESSAGING_URL = "https://www.linkedin.com/messaging/"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LinkedInWatcher")


def ensure_directories():
    """Ensure all required directories exist."""
    for path in [NEEDS_ACTION_PATH, LOGS_PATH, LINKEDIN_DATA_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def create_task_file(item_type: str, sender: str, content: str, url: str) -> Optional[Path]:
    """Create a markdown task file for the LinkedIn item."""
    try:
        # Generate filename
        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        safe_sender = "".join(c if c.isalnum() or c in " -_" else "" for c in sender)[:30]
        filename = f"{time_str}_linkedin_{item_type}_{safe_sender}.md"
        filepath = NEEDS_ACTION_PATH / filename

        # Create markdown content
        markdown = f"""# 🔵 LinkedIn {item_type.title()}: {sender}

## Metadata
- **Source:** LinkedIn
- **Type:** {item_type.title()}
- **From:** {sender}
- **Time:** {datetime.now().isoformat()}
- **Priority:** MEDIUM
- **URL:** {url}

---

## Content
{content}

---

## Suggested Actions
- [ ] View on LinkedIn: [Link]({url})
- [ ] Reply/Respond
- [ ] Ignore/Archive

---

## Decision Required
- [ ] **Respond** - Draft a reply
- [ ] **Connect** - Accept connection request
- [ ] **Ignore** - No action needed

"""

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would create: {filepath}")
            return None

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

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
        "actor": "linkedin_watcher",
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
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)


class LinkedInWatcher:
    """LinkedIn Watcher using Playwright."""

    def __init__(self):
        self.browser: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.processed_ids: set = set()

    async def start(self):
        """Start the browser and load session."""
        logger.info("Starting LinkedIn Watcher...")
        ensure_directories()

        self.playwright = await async_playwright().start()

        # Use persistent context to maintain login (shared with Poster)
        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(LINKEDIN_DATA_DIR),
            headless=HEADLESS,
            viewport={'width': 1280, 'height': 800},
            # Use a real user agent to reduce bot detection risk
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            args=['--disable-blink-features=AutomationControlled']
        )

        # Get or create page
        if self.browser.pages:
            self.page = self.browser.pages[0]
        else:
            self.page = await self.browser.new_page()

        # Set default timeout
        self.page.set_default_timeout(30000)

    async def check_login(self) -> bool:
        """Check if logged in."""
        try:
            await self.page.goto(LINKEDIN_FEED_URL, wait_until="networkidle")
            await asyncio.sleep(2)
            
            # Check for login indicators (feed nav, me icon)
            if "login" in self.page.url or "signup" in self.page.url:
                logger.warning("Not logged in to LinkedIn. Please login via Poster or manually.")
                return False
            
            # Look for specific element
            try:
                await self.page.wait_for_selector(".global-nav__me", timeout=5000)
                logger.info("Successfully authenticated with LinkedIn")
                return True
            except:
                logger.warning("Could not find profile icon, might not be logged in.")
                return False

        except Exception as e:
            logger.error(f"Error checking login: {e}")
            return False

    async def check_notifications(self):
        """Check for new notifications."""
        logger.info("Checking notifications...")
        try:
            await self.page.goto(LINKEDIN_NOTIFICATIONS_URL, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(2, 4))

            # Selector for unread/new notifications might vary. 
            # We look for notification cards.
            # Usually: .nt-card-list__container or similar.
            
            # Get notification items
            notifications = await self.page.query_selector_all("article.nt-card")
            
            count = 0
            for notif in notifications[:5]: # Process top 5
                try:
                    # Check if unread (often has a class like 'nt-card--unread')
                    classes = await notif.get_attribute("class")
                    if "unread" in classes:
                        # Extract text
                        text_el = await notif.query_selector(".nt-card__text")
                        text = await text_el.inner_text() if text_el else "New Notification"
                        
                        # Extract ID
                        notif_id = await notif.get_attribute("id") or text[:20]
                        
                        if notif_id not in self.processed_ids:
                            logger.info(f"New notification: {text[:50]}...")
                            create_task_file("notification", "LinkedIn", text, LINKEDIN_NOTIFICATIONS_URL)
                            self.processed_ids.add(notif_id)
                            count += 1
                except Exception as e:
                    logger.debug(f"Error parsing notification: {e}")
            
            if count > 0:
                logger.info(f"Created {count} tasks from notifications")

        except Exception as e:
            logger.error(f"Error checking notifications: {e}")

    async def check_messages(self):
        """Check for unread messages."""
        logger.info("Checking messages...")
        try:
            await self.page.goto(LINKEDIN_MESSAGING_URL, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(2, 4))

            # Look for conversation list items
            # Selectors: .msg-conversation-listitem
            
            conversations = await self.page.query_selector_all(".msg-conversation-listitem")
            
            count = 0
            for conv in conversations[:5]: # Check top 5
                try:
                    # Check for unread badge/indicator
                    # Often: .notification-badge--show
                    unread_badge = await conv.query_selector(".notification-badge--show")
                    
                    if unread_badge:
                        # Extract sender name
                        name_el = await conv.query_selector(".msg-conversation-listitem__participant-names")
                        sender = await name_el.inner_text() if name_el else "Unknown"
                        
                        # Extract preview
                        preview_el = await conv.query_selector(".msg-conversation-card__message-snippet")
                        preview = await preview_el.inner_text() if preview_el else ""
                        
                        # Unique ID
                        conv_id = f"msg_{sender}_{preview[:10]}"
                        
                        if conv_id not in self.processed_ids:
                            logger.info(f"New message from: {sender}")
                            create_task_file("message", sender, preview, LINKEDIN_MESSAGING_URL)
                            self.processed_ids.add(conv_id)
                            count += 1
                            
                except Exception as e:
                    logger.debug(f"Error parsing conversation: {e}")

            if count > 0:
                logger.info(f"Created {count} tasks from messages")

        except Exception as e:
            logger.error(f"Error checking messages: {e}")

    async def run(self):
        """Main loop."""
        try:
            await self.start()
            
            if not await self.check_login():
                logger.error("Login failed. Stopping.")
                return

            while True:
                try:
                    await self.check_notifications()
                    await asyncio.sleep(random.uniform(5, 10))
                    
                    await self.check_messages()
                    
                    logger.info(f"Sleeping for {POLL_INTERVAL} seconds...")
                    await asyncio.sleep(POLL_INTERVAL)
                    
                except Exception as e:
                    logger.error(f"Loop error: {e}")
                    await asyncio.sleep(60)

        except Exception as e:
            logger.critical(f"Watcher crashed: {e}")
        finally:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

def main():
    watcher = LinkedInWatcher()
    asyncio.run(watcher.run())

if __name__ == "__main__":
    main()
