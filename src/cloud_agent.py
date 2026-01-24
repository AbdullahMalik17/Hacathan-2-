#!/usr/bin/env python3
"""
Platinum Tier Cloud Agent

24/7 cloud agent that monitors watchers and creates drafts for human review.
Runs on Oracle Cloud VM in CLOUD work-zone (draft-only mode).

Features:
- Gmail inbox monitoring
- WhatsApp message monitoring
- LinkedIn message monitoring
- Task classification and draft creation
- Git sync for vault communication
- Auto-restart on failure

Usage:
    # Set environment
    export WORK_ZONE=cloud
    export AGENT_ID=cloud-oracle-001

    # Run agent
    python src/cloud_agent.py

    # Or with systemd
    sudo systemctl start digitalfte-cloud
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config, WorkZone
from src.utils.orchestrator_work_zone import WorkZoneOrchestrator
from src.utils.git_sync import git_pull, git_push, git_sync
from src.utils.audit_logger import log_audit, AuditDomain, AuditStatus


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_SYNC_INTERVAL = 30  # seconds
DEFAULT_POLL_INTERVAL = 60  # seconds
MAX_ERRORS_BEFORE_RESTART = 5

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("CloudAgent")


class CloudAgent:
    """
    Cloud Agent for Platinum Tier dual-agent architecture.

    Runs 24/7 on Oracle Cloud VM:
    - Monitors Gmail, WhatsApp, LinkedIn
    - Creates tasks from incoming messages
    - Generates drafts for human review
    - Syncs vault via Git
    """

    def __init__(self):
        """Initialize Cloud Agent."""
        # Load configuration
        self.config = load_config()

        # Verify we're in CLOUD work-zone
        if self.config["work_zone"] != WorkZone.CLOUD:
            logger.warning(
                f"Cloud Agent should run in CLOUD work-zone, "
                f"but current work-zone is {self.config['work_zone'].value}"
            )

        self.agent_id = self.config["agent_id"]
        self.vault_path = self.config["vault_path"]
        self.sync_interval = self.config.get("git_sync_interval", DEFAULT_SYNC_INTERVAL)

        # Initialize orchestrator
        self.orchestrator = WorkZoneOrchestrator()

        # State tracking
        self.running = False
        self.error_count = 0
        self.last_sync_time = None
        self.last_poll_time = None
        self.stats = {
            "tasks_processed": 0,
            "drafts_created": 0,
            "errors": 0,
            "syncs": 0,
            "start_time": None,
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        logger.info("=" * 60)
        logger.info("Cloud Agent Initialized (Platinum Tier)")
        logger.info(f"  Agent ID: {self.agent_id}")
        logger.info(f"  Work-Zone: {self.config['work_zone'].value}")
        logger.info(f"  Vault Path: {self.vault_path}")
        logger.info(f"  Sync Interval: {self.sync_interval}s")
        logger.info("=" * 60)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received shutdown signal ({signum})")
        self.running = False

    def start(self):
        """Start the Cloud Agent main loop."""
        logger.info("Starting Cloud Agent...")
        self.running = True
        self.stats["start_time"] = datetime.now()

        # Log startup
        log_audit(
            action="cloud_agent.started",
            actor=self.agent_id,
            domain=AuditDomain.SYSTEM,
            resource="cloud_agent",
            status=AuditStatus.SUCCESS,
            details={
                "work_zone": self.config["work_zone"].value,
                "vault_path": str(self.vault_path),
            },
        )

        try:
            self._main_loop()
        except Exception as e:
            logger.error(f"Cloud Agent crashed: {e}")
            log_audit(
                action="cloud_agent.crashed",
                actor=self.agent_id,
                domain=AuditDomain.SYSTEM,
                resource="cloud_agent",
                status=AuditStatus.FAILURE,
                error=str(e),
            )
            raise
        finally:
            self._shutdown()

    def _main_loop(self):
        """Main processing loop."""
        while self.running:
            try:
                loop_start = datetime.now()

                # 1. Git Pull (get latest from remote)
                self._sync_pull()

                # 2. Process pending tasks
                self._process_tasks()

                # 3. Git Push (send drafts to remote)
                self._sync_push()

                # 4. Update dashboard
                self._update_dashboard()

                # Reset error count on successful loop
                self.error_count = 0

                # Sleep until next iteration
                elapsed = (datetime.now() - loop_start).total_seconds()
                sleep_time = max(0, self.sync_interval - elapsed)

                logger.debug(f"Loop completed in {elapsed:.1f}s, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)

            except Exception as e:
                self.error_count += 1
                self.stats["errors"] += 1
                logger.error(f"Error in main loop: {e}")

                if self.error_count >= MAX_ERRORS_BEFORE_RESTART:
                    logger.critical(f"Too many errors ({self.error_count}), shutting down")
                    self.running = False
                else:
                    # Back off before retry
                    time.sleep(min(30, self.error_count * 5))

    def _sync_pull(self):
        """Pull latest changes from Git."""
        logger.debug("Pulling from Git...")

        result = git_pull(self.vault_path)

        if result["success"]:
            if result["files_changed"] > 0:
                logger.info(f"Git pull: {result['files_changed']} files changed")
            self.stats["syncs"] += 1
        else:
            logger.warning(f"Git pull failed: {result.get('error', 'Unknown error')}")

        self.last_sync_time = datetime.now()

    def _sync_push(self):
        """Push drafts and logs to Git."""
        logger.debug("Pushing to Git...")

        folders = ["Drafts/", "Logs/audit/", "Dashboard.md"]

        result = git_push(
            agent_id=self.agent_id,
            description="",
            folders=folders,
            vault_path=self.vault_path,
        )

        if result["success"]:
            if result["files_pushed"] > 0:
                logger.info(f"Git push: {result['files_pushed']} files pushed")
        elif result.get("error"):
            # Only log if there's an actual error (not just "no changes")
            if "no changes" not in result["error"].lower():
                logger.warning(f"Git push issue: {result['error']}")

    def _process_tasks(self):
        """Process pending tasks in Needs_Action."""
        result = self.orchestrator.process_pending_tasks()

        if result["processed"] > 0 or result["drafted"] > 0:
            logger.info(
                f"Processed: {result['processed']} tasks, "
                f"Created: {result['drafted']} drafts, "
                f"Failed: {result['failed']}"
            )

        self.stats["tasks_processed"] += result["processed"]
        self.stats["drafts_created"] += result["drafted"]
        self.stats["errors"] += result["failed"]

    def _update_dashboard(self):
        """Update the dashboard file with current status."""
        dashboard_path = self.vault_path / "Dashboard.md"

        # Get task counts
        needs_action_count = len(list((self.vault_path / "Needs_Action").glob("*.md")))
        drafts_count = len(list((self.vault_path / "Drafts").glob("*.md")))
        done_count = len(list((self.vault_path / "Done").glob("*.md")))

        # Calculate uptime
        uptime = ""
        if self.stats["start_time"]:
            delta = datetime.now() - self.stats["start_time"]
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{hours}h {minutes}m {seconds}s"

        dashboard_content = f"""# Digital FTE Health Dashboard

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Agent Status

| Agent ID | Work-Zone | Status | Uptime |
|----------|-----------|--------|--------|
| {self.agent_id} | CLOUD | 🟢 RUNNING | {uptime} |

## Work-Zone Mode

- **Current Mode:** DRAFT ONLY
- **Execution:** Blocked (requires Local approval)
- **MCP Servers:** Disabled

## Queue Status

| Folder | Count | Description |
|--------|-------|-------------|
| Needs_Action | {needs_action_count} | Tasks awaiting processing |
| Drafts | {drafts_count} | Drafts awaiting approval |
| Done | {done_count} | Completed tasks |

## Session Statistics

| Metric | Value |
|--------|-------|
| Tasks Processed | {self.stats['tasks_processed']} |
| Drafts Created | {self.stats['drafts_created']} |
| Git Syncs | {self.stats['syncs']} |
| Errors | {self.stats['errors']} |

## Recent Activity

- **Last Sync:** {self.last_sync_time.strftime('%H:%M:%S') if self.last_sync_time else 'N/A'}
- **Error Count:** {self.error_count}

---

*Dashboard updated by Cloud Agent ({self.agent_id})*
"""

        try:
            dashboard_path.write_text(dashboard_content, encoding='utf-8')
        except Exception as e:
            logger.warning(f"Failed to update dashboard: {e}")

    def _shutdown(self):
        """Clean shutdown."""
        logger.info("Shutting down Cloud Agent...")

        # Final sync
        try:
            self._sync_push()
        except Exception as e:
            logger.warning(f"Final sync failed: {e}")

        # Log shutdown
        log_audit(
            action="cloud_agent.stopped",
            actor=self.agent_id,
            domain=AuditDomain.SYSTEM,
            resource="cloud_agent",
            status=AuditStatus.SUCCESS,
            details={
                "uptime": str(datetime.now() - self.stats["start_time"]) if self.stats["start_time"] else "N/A",
                "tasks_processed": self.stats["tasks_processed"],
                "drafts_created": self.stats["drafts_created"],
            },
        )

        logger.info("Cloud Agent stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "work_zone": self.config["work_zone"].value,
            "running": self.running,
            "uptime": str(datetime.now() - self.stats["start_time"]) if self.stats["start_time"] else None,
            "stats": self.stats,
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "error_count": self.error_count,
        }


def main():
    """Main entry point."""
    # Ensure WORK_ZONE is set to cloud
    if os.getenv("WORK_ZONE", "").lower() != "cloud":
        logger.warning("WORK_ZONE not set to 'cloud', setting it now")
        os.environ["WORK_ZONE"] = "cloud"

    # Create and start agent
    agent = CloudAgent()

    try:
        agent.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
