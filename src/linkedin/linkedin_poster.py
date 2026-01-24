"""
LinkedIn Poster - Digital FTE Action System

This script handles LinkedIn posting using Playwright browser automation.
It supports both text posts and posts with media attachments.

Setup:
1. Install Playwright: pip install playwright
2. Install browser: playwright install chromium
3. Run script and login manually on first run
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
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
LINKEDIN_DATA_DIR = CONFIG_PATH / "linkedin_data"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"
LINKEDIN_QUEUE_PATH = VAULT_PATH / "LinkedIn_Queue"

# Rate limiting
MAX_POSTS_PER_DAY = 2
MAX_POSTS_PER_HOUR = 1

# URLs
LINKEDIN_URL = "https://www.linkedin.com"
LINKEDIN_FEED_URL = "https://www.linkedin.com/feed/"
LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"

# Polling configuration
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
HEADLESS = os.getenv("LINKEDIN_HEADLESS", "false").lower() == "true"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LinkedInPoster")


def ensure_directories():
    """Ensure all required directories exist."""
    for path in [LINKEDIN_DATA_DIR, PENDING_APPROVAL_PATH, APPROVED_PATH,
                 DONE_PATH, LOGS_PATH, LINKEDIN_QUEUE_PATH]:
        path.mkdir(parents=True, exist_ok=True)


def load_post_history() -> Dict[str, Any]:
    """Load post history for rate limiting."""
    history_file = LINKEDIN_DATA_DIR / "post_history.json"
    if history_file.exists():
        with open(history_file, "r") as f:
            return json.load(f)
    return {"posts": [], "last_updated": None}


def save_post_history(history: Dict[str, Any]):
    """Save post history."""
    history_file = LINKEDIN_DATA_DIR / "post_history.json"
    history["last_updated"] = datetime.now().isoformat()
    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)


def check_rate_limit() -> tuple[bool, str]:
    """Check if posting is allowed based on rate limits."""
    history = load_post_history()
    now = datetime.now()

    # Filter posts from last 24 hours
    day_ago = now - timedelta(hours=24)
    hour_ago = now - timedelta(hours=1)

    recent_posts = [
        p for p in history.get("posts", [])
        if datetime.fromisoformat(p["timestamp"]) > day_ago
    ]

    hourly_posts = [
        p for p in recent_posts
        if datetime.fromisoformat(p["timestamp"]) > hour_ago
    ]

    if len(recent_posts) >= MAX_POSTS_PER_DAY:
        return False, f"Daily limit reached ({MAX_POSTS_PER_DAY} posts/day)"

    if len(hourly_posts) >= MAX_POSTS_PER_HOUR:
        return False, f"Hourly limit reached ({MAX_POSTS_PER_HOUR} posts/hour)"

    return True, "OK"


def record_post(post_id: str, content_preview: str):
    """Record a successful post for rate limiting."""
    history = load_post_history()
    history["posts"].append({
        "id": post_id,
        "timestamp": datetime.now().isoformat(),
        "preview": content_preview[:100]
    })
    # Keep only last 30 days
    cutoff = datetime.now() - timedelta(days=30)
    history["posts"] = [
        p for p in history["posts"]
        if datetime.fromisoformat(p["timestamp"]) > cutoff
    ]
    save_post_history(history)


def log_to_audit(action: str, details: Dict[str, Any], success: bool):
    """Log action to LinkedIn audit log."""
    audit_file = LOGS_PATH / "linkedin_audit_log.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILED"

    entry = f"\n## {timestamp} - {action} [{status}]\n"
    for key, value in details.items():
        entry += f"- **{key}**: {value}\n"
    entry += "\n---\n"

    with open(audit_file, "a") as f:
        f.write(entry)


def log_to_daily(action: str, details: Dict[str, Any]):
    """Log to daily JSON log."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_PATH / f"{today}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source": "linkedin_poster",
        "action": action,
        **details
    }

    # Load existing or create new
    logs = []
    if log_file.exists():
        with open(log_file, "r") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(log_entry)

    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)


class LinkedInPoster:
    """Browser automation for LinkedIn posting using Playwright."""

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.authenticated = False

    async def start(self):
        """Start browser with persistent context."""
        ensure_directories()

        self.playwright = await async_playwright().start()

        # Use persistent context for session persistence
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(LINKEDIN_DATA_DIR),
            headless=HEADLESS,
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Get or create page
        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()

        logger.info("Browser started with persistent context")

    async def stop(self):
        """Stop browser and cleanup."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser stopped")

    async def check_session(self) -> bool:
        """Check if we have a valid LinkedIn session."""
        try:
            await self.page.goto(LINKEDIN_FEED_URL, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Check if we're on the feed (logged in) or redirected to login
            current_url = self.page.url

            if "login" in current_url or "checkpoint" in current_url:
                logger.info("Not logged in - session invalid")
                return False

            # Look for feed indicators
            feed_indicators = [
                'div[data-id="feed-nav-item"]',
                'button[aria-label="Start a post"]',
                'div.feed-shared-update-v2'
            ]

            for selector in feed_indicators:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000)
                    if element:
                        logger.info("Session valid - logged in to LinkedIn")
                        self.authenticated = True
                        return True
                except:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error checking session: {e}")
            return False

    async def authenticate(self) -> bool:
        """Navigate to LinkedIn and handle authentication."""
        try:
            # First check if we already have a valid session
            if await self.check_session():
                return True

            # Navigate to login page
            await self.page.goto(LINKEDIN_LOGIN_URL, wait_until="networkidle")

            logger.info("="*50)
            logger.info("LINKEDIN LOGIN REQUIRED")
            logger.info("Please log in to LinkedIn in the browser window.")
            logger.info("The script will wait for you to complete login.")
            logger.info("="*50)

            # Wait for user to log in (check for feed page)
            max_wait = 300  # 5 minutes
            start_time = asyncio.get_event_loop().time()

            while asyncio.get_event_loop().time() - start_time < max_wait:
                await asyncio.sleep(3)

                current_url = self.page.url
                if "feed" in current_url and "login" not in current_url:
                    logger.info("Login successful!")
                    self.authenticated = True
                    log_to_audit("authenticate", {"method": "manual_login"}, True)
                    return True

            logger.error("Login timeout - please try again")
            log_to_audit("authenticate", {"error": "timeout"}, False)
            return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            log_to_audit("authenticate", {"error": str(e)}, False)
            return False

    async def create_post(self, content: str, media_paths: List[Path] = None) -> tuple[bool, str]:
        """
        Create a new LinkedIn post.

        Args:
            content: The post text content
            media_paths: Optional list of image paths to attach

        Returns:
            Tuple of (success: bool, message: str)
        """
        if DRY_RUN:
            logger.info(f"[DRY RUN] Would post: {content[:100]}...")
            return True, "DRY_RUN"

        # Check rate limits
        can_post, reason = check_rate_limit()
        if not can_post:
            logger.warning(f"Rate limit: {reason}")
            return False, reason

        # Ensure authenticated
        if not self.authenticated:
            if not await self.authenticate():
                return False, "Authentication failed"

        try:
            # Navigate to feed
            await self.page.goto(LINKEDIN_FEED_URL, wait_until="networkidle")
            await asyncio.sleep(2)

            # Click "Start a post" button
            start_post_selectors = [
                'button[aria-label="Start a post"]',
                'button:has-text("Start a post")',
                '.share-box-feed-entry__trigger',
                'div.share-box-feed-entry__top-bar button'
            ]

            clicked = False
            for selector in start_post_selectors:
                try:
                    button = await self.page.wait_for_selector(selector, timeout=5000)
                    if button:
                        await button.click()
                        clicked = True
                        logger.info("Clicked 'Start a post' button")
                        break
                except:
                    continue

            if not clicked:
                return False, "Could not find 'Start a post' button"

            await asyncio.sleep(2)

            # Find and fill the post editor
            editor_selectors = [
                'div.ql-editor[data-placeholder]',
                'div[aria-label="Text editor for creating content"]',
                'div.editor-content',
                'div[role="textbox"]'
            ]

            editor = None
            for selector in editor_selectors:
                try:
                    editor = await self.page.wait_for_selector(selector, timeout=5000)
                    if editor:
                        break
                except:
                    continue

            if not editor:
                return False, "Could not find post editor"

            # Type the content
            await editor.click()
            await self.page.keyboard.type(content, delay=20)
            logger.info("Typed post content")

            await asyncio.sleep(1)

            # Handle media attachments if provided
            if media_paths:
                for media_path in media_paths:
                    if media_path.exists():
                        try:
                            # Find media upload button
                            media_button = await self.page.wait_for_selector(
                                'button[aria-label="Add a photo"]',
                                timeout=5000
                            )
                            if media_button:
                                await media_button.click()

                                # Handle file input
                                file_input = await self.page.wait_for_selector(
                                    'input[type="file"]',
                                    timeout=5000
                                )
                                if file_input:
                                    await file_input.set_input_files(str(media_path))
                                    logger.info(f"Attached media: {media_path.name}")
                                    await asyncio.sleep(2)
                        except Exception as e:
                            logger.warning(f"Could not attach media {media_path}: {e}")

            # Click Post button
            post_button_selectors = [
                'button:has-text("Post")',
                'button.share-actions__primary-action',
                'button[aria-label="Post"]'
            ]

            for selector in post_button_selectors:
                try:
                    post_button = await self.page.wait_for_selector(selector, timeout=5000)
                    if post_button:
                        # Check if button is enabled
                        is_disabled = await post_button.get_attribute("disabled")
                        if not is_disabled:
                            await post_button.click()
                            logger.info("Clicked Post button")
                            break
                except:
                    continue

            # Wait for post to complete
            await asyncio.sleep(5)

            # Generate post ID
            post_id = f"li_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Record successful post
            record_post(post_id, content)

            # Log success
            log_to_audit("create_post", {
                "post_id": post_id,
                "content_length": len(content),
                "has_media": bool(media_paths)
            }, True)

            log_to_daily("post_created", {
                "post_id": post_id,
                "result": "success"
            })

            logger.info(f"Post created successfully: {post_id}")
            return True, post_id

        except Exception as e:
            logger.error(f"Error creating post: {e}")
            log_to_audit("create_post", {"error": str(e)}, False)
            return False, str(e)

    async def process_approved_posts(self) -> int:
        """Process all approved LinkedIn posts."""
        posted_count = 0

        # Find LinkedIn posts in Approved folder
        for post_file in APPROVED_PATH.glob("LinkedIn_*.md"):
            logger.info(f"Processing approved post: {post_file.name}")

            try:
                content = post_file.read_text(encoding="utf-8")

                # Extract post content (after frontmatter)
                if "---" in content:
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        post_content = parts[2].strip()
                    else:
                        post_content = content
                else:
                    post_content = content

                # Remove markdown headers and metadata
                lines = post_content.split("\n")
                clean_lines = [
                    l for l in lines
                    if not l.startswith("#") and
                       not l.startswith("- [") and
                       not l.startswith("## Actions")
                ]
                post_content = "\n".join(clean_lines).strip()

                if not post_content:
                    logger.warning(f"Empty post content in {post_file.name}")
                    continue

                # Create the post
                success, result = await self.create_post(post_content)

                if success:
                    # Move to Done
                    done_file = DONE_PATH / post_file.name
                    post_file.rename(done_file)
                    logger.info(f"Moved {post_file.name} to Done/")
                    posted_count += 1
                else:
                    logger.error(f"Failed to post {post_file.name}: {result}")

            except Exception as e:
                logger.error(f"Error processing {post_file.name}: {e}")

        return posted_count


async def main():
    """Main entry point for LinkedIn poster."""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Poster - Digital FTE")
    parser.add_argument("--post", type=str, help="Post content directly")
    parser.add_argument("--process-approved", action="store_true",
                        help="Process all approved LinkedIn posts")
    parser.add_argument("--check-session", action="store_true",
                        help="Check if LinkedIn session is valid")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run without actually posting")
    args = parser.parse_args()

    if args.dry_run:
        os.environ["DRY_RUN"] = "true"

    poster = LinkedInPoster()

    try:
        await poster.start()

        if args.check_session:
            valid = await poster.check_session()
            print(f"Session valid: {valid}")

        elif args.post:
            success, result = await poster.create_post(args.post)
            print(f"Post result: {result}")

        elif args.process_approved:
            count = await poster.process_approved_posts()
            print(f"Processed {count} approved posts")

        else:
            # Default: authenticate and process approved
            if await poster.authenticate():
                count = await poster.process_approved_posts()
                print(f"Processed {count} approved posts")
            else:
                print("Authentication failed")
                sys.exit(1)

    finally:
        await poster.stop()


if __name__ == "__main__":
    asyncio.run(main())
