"""
LinkedIn Scheduler - Digital FTE Action System

This script manages the LinkedIn posting queue and approval workflow.
It moves posts through the workflow: Queue → Pending_Approval → Approved → Done

Setup:
1. Place posts in Vault/LinkedIn_Queue/ or they're auto-generated from CEO Briefing
2. Run scheduler to move posts to Pending_Approval
3. Human reviews and approves (moves to Approved/)
4. LinkedIn poster posts from Approved/
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import frontmatter

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from linkedin.content_generator import ContentGenerator
except ImportError:
    print("Content generator not found. Run from project root.")
    sys.exit(1)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
CONFIG_PATH = PROJECT_ROOT / "config"
LINKEDIN_QUEUE_PATH = VAULT_PATH / "LinkedIn_Queue"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"
CEO_BRIEFING_PATH = VAULT_PATH

# Default configuration
DEFAULT_CONFIG = {
    "posting_schedule": {
        "days": ["Monday", "Wednesday", "Friday"],
        "preferred_times": ["09:00", "15:00"]
    },
    "rate_limits": {
        "max_per_day": 2,
        "max_per_hour": 1
    },
    "approval_required": True,
    "auto_generate_from_briefing": True,
    "default_hashtags": ["AIAutomation", "Productivity", "DigitalTransformation"]
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("LinkedInScheduler")


def ensure_directories():
    """Ensure all required directories exist."""
    for path in [LINKEDIN_QUEUE_PATH, PENDING_APPROVAL_PATH, APPROVED_PATH, DONE_PATH, LOGS_PATH]:
        path.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """Load LinkedIn configuration."""
    config_file = CONFIG_PATH / "linkedin_config.json"
    if config_file.exists():
        with open(config_file, "r") as f:
            return json.load(f)
    logger.warning(f"Config file not found at {config_file}, using defaults")
    return DEFAULT_CONFIG


def save_config(config: Dict[str, Any]):
    """Save LinkedIn configuration."""
    config_file = CONFIG_PATH / "linkedin_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    logger.info(f"Configuration saved to {config_file}")


def get_post_history() -> List[Dict[str, Any]]:
    """Get posting history for rate limit checks."""
    history_file = CONFIG_PATH / "linkedin_data" / "post_history.json"
    if history_file.exists():
        with open(history_file, "r") as f:
            data = json.load(f)
            return data.get("posts", [])
    return []


def can_schedule_post() -> tuple[bool, str]:
    """Check if we can schedule a new post based on rate limits."""
    config = load_config()
    history = get_post_history()

    max_per_day = config["rate_limits"]["max_per_day"]
    max_per_hour = config["rate_limits"]["max_per_hour"]

    now = datetime.now()
    day_ago = now - timedelta(hours=24)
    hour_ago = now - timedelta(hours=1)

    # Count posts in last 24 hours
    daily_posts = [
        p for p in history
        if datetime.fromisoformat(p["timestamp"]) > day_ago
    ]

    # Count posts in last hour
    hourly_posts = [
        p for p in history
        if datetime.fromisoformat(p["timestamp"]) > hour_ago
    ]

    if len(daily_posts) >= max_per_day:
        return False, f"Daily limit reached ({len(daily_posts)}/{max_per_day})"

    if len(hourly_posts) >= max_per_hour:
        return False, f"Hourly limit reached ({len(hourly_posts)}/{max_per_hour})"

    return True, "OK"


def get_next_posting_slot() -> Optional[datetime]:
    """Calculate the next available posting slot based on schedule."""
    config = load_config()
    schedule = config["posting_schedule"]
    preferred_days = schedule["days"]
    preferred_times = schedule["preferred_times"]

    now = datetime.now()

    # Check next 7 days
    for day_offset in range(7):
        check_date = now + timedelta(days=day_offset)
        day_name = check_date.strftime("%A")

        if day_name in preferred_days:
            for time_str in preferred_times:
                hour, minute = map(int, time_str.split(":"))
                slot = check_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # Skip if slot is in the past
                if slot <= now:
                    continue

                # Check if slot is available (rate limits)
                # For simplicity, we'll return first future slot on preferred day
                return slot

    return None


def create_approval_request(content: str, source: str, metadata: Dict[str, Any]) -> Path:
    """Create a pending approval file for a LinkedIn post."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"LinkedIn_{timestamp}_{metadata.get('type', 'post')}.md"
    filepath = PENDING_APPROVAL_PATH / filename

    # Create frontmatter
    post_data = frontmatter.Post(content)
    post_data.metadata = {
        "type": "linkedin_post",
        "source": source,
        "scheduled": metadata.get("scheduled", get_next_posting_slot().isoformat() if get_next_posting_slot() else None),
        "status": "pending_approval",
        "created": datetime.now().isoformat(),
        "priority": metadata.get("priority", "medium")
    }

    # Create approval template
    approval_content = f"""---
type: {post_data.metadata['type']}
source: {post_data.metadata['source']}
scheduled: {post_data.metadata['scheduled']}
status: {post_data.metadata['status']}
created: {post_data.metadata['created']}
priority: {post_data.metadata['priority']}
---

## Proposed LinkedIn Post

{content}

---

## Actions
- [ ] Approve - Move to Approved/
- [ ] Edit - Modify content above and approve
- [ ] Reject - Delete this file

---

## Metadata
- **Source:** {source}
- **Scheduled:** {post_data.metadata['scheduled']}
- **Created:** {post_data.metadata['created']}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(approval_content)

    logger.info(f"Created approval request: {filepath}")
    return filepath


def process_queue_posts():
    """Process posts from LinkedIn_Queue and move to Pending_Approval."""
    if not LINKEDIN_QUEUE_PATH.exists():
        logger.warning(f"LinkedIn queue path not found: {LINKEDIN_QUEUE_PATH}")
        return

    # Get all markdown files from queue
    queue_files = list(LINKEDIN_QUEUE_PATH.glob("*.md"))

    if not queue_files:
        logger.info("No posts in LinkedIn queue")
        return

    for post_file in queue_files:
        if post_file.name == ".gitkeep":
            continue

        try:
            # Read post content
            with open(post_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse frontmatter if present
            try:
                post = frontmatter.loads(content)
                post_content = post.content
                metadata = post.metadata
            except:
                post_content = content
                metadata = {}

            # Create approval request
            create_approval_request(
                content=post_content,
                source="manual_queue",
                metadata=metadata
            )

            # Move original file to Done
            done_file = DONE_PATH / f"processed_{post_file.name}"
            post_file.rename(done_file)
            logger.info(f"Moved {post_file.name} to Done/")

        except Exception as e:
            logger.error(f"Error processing {post_file.name}: {e}")


def generate_from_ceo_briefing():
    """Auto-generate LinkedIn post from latest CEO briefing."""
    config = load_config()

    if not config.get("auto_generate_from_briefing", True):
        logger.info("Auto-generation from CEO briefing is disabled")
        return

    # Find latest CEO briefing
    briefing_files = list(CEO_BRIEFING_PATH.glob("CEO_Briefing_*.md"))
    if not briefing_files:
        logger.info("No CEO briefing files found")
        return

    # Get most recent
    latest_briefing = max(briefing_files, key=lambda p: p.stat().st_mtime)

    # Check if we already generated from this briefing
    briefing_date = latest_briefing.stem.replace("CEO_Briefing_", "")
    marker_file = CONFIG_PATH / "linkedin_data" / f"generated_{briefing_date}.marker"

    if marker_file.exists():
        logger.info(f"Already generated post from {latest_briefing.name}")
        return

    try:
        # Generate content
        generator = ContentGenerator()
        content = generator.from_ceo_briefing(latest_briefing)

        # Create approval request
        create_approval_request(
            content=content,
            source="ceo_briefing",
            metadata={
                "type": "weekly_update",
                "briefing_file": str(latest_briefing),
                "priority": "medium"
            }
        )

        # Create marker file
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_file.touch()
        logger.info(f"Generated LinkedIn post from {latest_briefing.name}")

    except Exception as e:
        logger.error(f"Error generating from CEO briefing: {e}")


def get_approved_posts() -> List[Path]:
    """Get all approved posts ready for posting."""
    if not APPROVED_PATH.exists():
        return []

    return list(APPROVED_PATH.glob("LinkedIn_*.md"))


def run_scheduler(test_mode: bool = False):
    """Main scheduler loop."""
    logger.info("Starting LinkedIn Scheduler")
    ensure_directories()

    # Check rate limits
    can_post, reason = can_schedule_post()
    if not can_post:
        logger.warning(f"Cannot schedule new posts: {reason}")
    else:
        logger.info(f"Ready to schedule posts: {reason}")

    # Process manual queue
    logger.info("Processing manual queue...")
    process_queue_posts()

    # Generate from CEO briefing
    logger.info("Checking for CEO briefing updates...")
    generate_from_ceo_briefing()

    # Show pending and approved counts
    pending_count = len(list(PENDING_APPROVAL_PATH.glob("LinkedIn_*.md")))
    approved_count = len(get_approved_posts())

    logger.info(f"Status: {pending_count} pending approval, {approved_count} approved")

    if test_mode:
        logger.info("Test mode - scheduler completed successfully")

    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Scheduler")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--init-config", action="store_true", help="Initialize default config")

    args = parser.parse_args()

    if args.init_config:
        save_config(DEFAULT_CONFIG)
        print("✓ Configuration initialized")
        return

    try:
        run_scheduler(test_mode=args.test)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
