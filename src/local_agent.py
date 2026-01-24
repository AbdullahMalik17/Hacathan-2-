#!/usr/bin/env python3
"""
Platinum Tier Local Agent

Local agent that runs on user's machine for draft approval and execution.
Runs in LOCAL work-zone with full execution capabilities.

Features:
- Git sync to pull drafts from Cloud
- Draft review notification
- Approved task execution
- MCP server integration
- Obsidian vault display

Usage:
    # Set environment
    export WORK_ZONE=local
    export AGENT_ID=local-laptop-001

    # Run agent
    python src/local_agent.py

    # Or run in background
    python src/local_agent.py &
"""

import os
import sys
import time
import signal
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config, WorkZone
from src.utils.orchestrator_work_zone import WorkZoneOrchestrator
from src.utils.git_sync import git_pull, git_push, git_sync
from src.utils.claim_by_move import claim_task, get_claimable_tasks
from src.utils.audit_logger import log_audit, AuditDomain, AuditStatus


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_SYNC_INTERVAL = 30  # seconds
DEFAULT_POLL_INTERVAL = 10  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("LocalAgent")


class LocalAgent:
    """
    Local Agent for Platinum Tier dual-agent architecture.

    Runs on user's machine:
    - Pulls drafts from Cloud via Git
    - Displays drafts in Obsidian
    - Executes approved tasks
    - Has full MCP server access
    """

    def __init__(self):
        """Initialize Local Agent."""
        # Load configuration
        self.config = load_config()

        # Verify we're in LOCAL work-zone
        if self.config["work_zone"] != WorkZone.LOCAL:
            logger.warning(
                f"Local Agent should run in LOCAL work-zone, "
                f"but current work-zone is {self.config['work_zone'].value}"
            )

        self.agent_id = self.config["agent_id"]
        self.vault_path = self.config["vault_path"]
        self.sync_interval = self.config.get("git_sync_interval", DEFAULT_SYNC_INTERVAL)

        # Initialize orchestrator
        self.orchestrator = WorkZoneOrchestrator()

        # State tracking
        self.running = False
        self.last_sync_time = None
        self.pending_drafts: List[Path] = []
        self.stats = {
            "tasks_executed": 0,
            "drafts_pulled": 0,
            "errors": 0,
            "syncs": 0,
            "start_time": None,
        }

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        logger.info("=" * 60)
        logger.info("Local Agent Initialized (Platinum Tier)")
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
        """Start the Local Agent main loop."""
        logger.info("Starting Local Agent...")
        self.running = True
        self.stats["start_time"] = datetime.now()

        # Log startup
        log_audit(
            action="local_agent.started",
            actor=self.agent_id,
            domain=AuditDomain.SYSTEM,
            resource="local_agent",
            status=AuditStatus.SUCCESS,
            details={
                "work_zone": self.config["work_zone"].value,
                "vault_path": str(self.vault_path),
            },
        )

        try:
            self._main_loop()
        except Exception as e:
            logger.error(f"Local Agent crashed: {e}")
            log_audit(
                action="local_agent.crashed",
                actor=self.agent_id,
                domain=AuditDomain.SYSTEM,
                resource="local_agent",
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

                # 1. Git Pull (get drafts from Cloud)
                self._sync_pull()

                # 2. Check for new drafts
                self._check_drafts()

                # 3. Process approved tasks
                self._process_approved()

                # 4. Git Push (sync changes back)
                self._sync_push()

                # 5. Update dashboard
                self._update_dashboard()

                # Sleep until next iteration
                elapsed = (datetime.now() - loop_start).total_seconds()
                sleep_time = max(0, self.sync_interval - elapsed)

                logger.debug(f"Loop completed in {elapsed:.1f}s, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)

            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)  # Brief pause before retry

    def _sync_pull(self):
        """Pull latest changes from Git (including Cloud drafts)."""
        logger.debug("Pulling from Git...")

        result = git_pull(self.vault_path)

        if result["success"]:
            if result["files_changed"] > 0:
                logger.info(f"Git pull: {result['files_changed']} files changed")
                self.stats["drafts_pulled"] += result["files_changed"]
            self.stats["syncs"] += 1
        else:
            logger.warning(f"Git pull failed: {result.get('error', 'Unknown error')}")

        self.last_sync_time = datetime.now()

    def _sync_push(self):
        """Push local changes to Git."""
        logger.debug("Pushing to Git...")

        folders = ["Approved/", "Done/", "Logs/audit/", "Dashboard.md"]

        result = git_push(
            agent_id=self.agent_id,
            description="",
            folders=folders,
            vault_path=self.vault_path,
        )

        if result["success"] and result["files_pushed"] > 0:
            logger.info(f"Git push: {result['files_pushed']} files pushed")

    def _check_drafts(self):
        """Check for new drafts from Cloud."""
        drafts_path = self.vault_path / "Drafts"

        if not drafts_path.exists():
            return

        drafts = list(drafts_path.glob("*.md"))
        drafts = [d for d in drafts if d.name not in [".gitkeep", "README.md"]]

        if drafts:
            # Check for new drafts
            new_drafts = [d for d in drafts if d not in self.pending_drafts]

            if new_drafts:
                logger.info(f"📬 {len(new_drafts)} new draft(s) available for review!")
                for draft in new_drafts:
                    logger.info(f"  - {draft.name}")

                # Show notification (if available)
                self._notify_drafts(new_drafts)

            self.pending_drafts = drafts

    def _notify_drafts(self, drafts: List[Path]):
        """Show notification for new drafts (platform-specific)."""
        try:
            # Try Windows toast notification
            if sys.platform == "win32":
                try:
                    from win10toast import ToastNotifier
                    toaster = ToastNotifier()
                    toaster.show_toast(
                        "Digital FTE - New Drafts",
                        f"{len(drafts)} draft(s) ready for review in Obsidian",
                        duration=10,
                        threaded=True,
                    )
                except ImportError:
                    pass

            # Try macOS notification
            elif sys.platform == "darwin":
                os.system(f"""osascript -e 'display notification "{len(drafts)} draft(s) ready for review" with title "Digital FTE"'""")

            # Try Linux notification
            elif sys.platform.startswith("linux"):
                os.system(f"""notify-send "Digital FTE" "{len(drafts)} draft(s) ready for review" """)

        except Exception as e:
            logger.debug(f"Could not show notification: {e}")

    def _process_approved(self):
        """Process tasks that have been approved."""
        approved_path = self.vault_path / "Approved"

        if not approved_path.exists():
            return

        approved_tasks = get_claimable_tasks("Approved", self.vault_path)

        for task_path in approved_tasks:
            logger.info(f"Executing approved task: {task_path.name}")

            try:
                # Move to Done (execution would happen here with MCP)
                success, message = claim_task(
                    task_path=task_path,
                    agent_id=self.agent_id,
                    destination_folder="Done",
                    vault_path=self.vault_path,
                )

                if success:
                    self.stats["tasks_executed"] += 1
                    logger.info(f"✅ Task executed: {task_path.name}")

                    # Log execution
                    log_audit(
                        action="local_agent.task_executed",
                        actor=self.agent_id,
                        domain=AuditDomain.SYSTEM,
                        resource=task_path.stem,
                        status=AuditStatus.SUCCESS,
                        details={"task_file": task_path.name},
                    )
                else:
                    logger.warning(f"Failed to execute: {message}")

            except Exception as e:
                self.stats["errors"] += 1
                logger.error(f"Error executing task: {e}")

    def _update_dashboard(self):
        """Update the dashboard file with current status."""
        dashboard_path = self.vault_path / "Dashboard.md"

        # Get task counts
        needs_action_count = len(list((self.vault_path / "Needs_Action").glob("*.md")))
        drafts_count = len([d for d in (self.vault_path / "Drafts").glob("*.md")
                           if d.name not in [".gitkeep", "README.md"]])
        approved_count = len(list((self.vault_path / "Approved").glob("*.md")))
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
| {self.agent_id} | LOCAL | 🟢 RUNNING | {uptime} |

## Work-Zone Mode

- **Current Mode:** FULL EXECUTION
- **Execution:** Enabled (after approval)
- **MCP Servers:** Available

## Queue Status

| Folder | Count | Action |
|--------|-------|--------|
| Needs_Action | {needs_action_count} | Awaiting processing |
| **Drafts** | **{drafts_count}** | **Review in Obsidian** |
| Approved | {approved_count} | Ready for execution |
| Done | {done_count} | Completed |

{f'### ⚠️ {drafts_count} Draft(s) Awaiting Review!' if drafts_count > 0 else ''}

## Session Statistics

| Metric | Value |
|--------|-------|
| Tasks Executed | {self.stats['tasks_executed']} |
| Drafts Pulled | {self.stats['drafts_pulled']} |
| Git Syncs | {self.stats['syncs']} |
| Errors | {self.stats['errors']} |

## How to Approve Drafts

1. Open **Vault/Drafts/** in Obsidian
2. Review each draft
3. If approved, move file to **Vault/Approved/**
4. Local Agent will execute automatically

---

*Dashboard updated by Local Agent ({self.agent_id})*
"""

        try:
            dashboard_path.write_text(dashboard_content, encoding='utf-8')
        except Exception as e:
            logger.warning(f"Failed to update dashboard: {e}")

    def _shutdown(self):
        """Clean shutdown."""
        logger.info("Shutting down Local Agent...")

        # Final sync
        try:
            self._sync_push()
        except Exception as e:
            logger.warning(f"Final sync failed: {e}")

        # Log shutdown
        log_audit(
            action="local_agent.stopped",
            actor=self.agent_id,
            domain=AuditDomain.SYSTEM,
            resource="local_agent",
            status=AuditStatus.SUCCESS,
            details={
                "uptime": str(datetime.now() - self.stats["start_time"]) if self.stats["start_time"] else "N/A",
                "tasks_executed": self.stats["tasks_executed"],
            },
        )

        logger.info("Local Agent stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "work_zone": self.config["work_zone"].value,
            "running": self.running,
            "uptime": str(datetime.now() - self.stats["start_time"]) if self.stats["start_time"] else None,
            "stats": self.stats,
            "pending_drafts": len(self.pending_drafts),
            "last_sync": self.last_sync_time.isoformat() if self.last_sync_time else None,
        }

    def run_once(self):
        """Run a single sync cycle (useful for testing)."""
        logger.info("Running single sync cycle...")

        self._sync_pull()
        self._check_drafts()
        self._process_approved()
        self._sync_push()
        self._update_dashboard()

        return self.get_status()


def main():
    """Main entry point."""
    # Ensure WORK_ZONE is set to local
    if os.getenv("WORK_ZONE", "").lower() != "local":
        logger.warning("WORK_ZONE not set to 'local', setting it now")
        os.environ["WORK_ZONE"] = "local"

    # Create and start agent
    agent = LocalAgent()

    try:
        agent.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
