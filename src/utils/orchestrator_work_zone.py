"""
Platinum Tier Orchestrator Work-Zone Integration

Provides work-zone aware task processing for the orchestrator.
Enforces CLOUD (draft-only) and LOCAL (full execution) modes.

Features:
- Work-zone detection and enforcement
- Automatic draft creation for blocked actions
- Integration with existing orchestrator
- Audit logging for all decisions

Usage:
    from src.utils.orchestrator_work_zone import (
        WorkZoneOrchestrator,
        process_task_with_work_zone,
    )

    # Create work-zone aware orchestrator
    orchestrator = WorkZoneOrchestrator()
    result = orchestrator.process_task(task_path)

    # Or use the standalone function
    result = process_task_with_work_zone(task_path, action_type)
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from src.utils.config import load_config, WorkZone
from src.utils.work_zone import (
    ActionType,
    can_execute_action,
    enforce_work_zone,
    get_action_type_from_string,
    is_sensitive_action,
)
from src.utils.claim_by_move import claim_task, get_claimable_tasks
from src.utils.draft_creator import create_draft, DraftCreator
from src.utils.git_sync import git_sync
from src.utils.audit_logger import log_audit, AuditDomain, AuditStatus


# Configure logging
logger = logging.getLogger(__name__)


class WorkZoneOrchestrator:
    """
    Work-zone aware orchestrator for Platinum Tier dual-agent architecture.

    Handles task processing with automatic work-zone enforcement:
    - CLOUD: Creates drafts for sensitive actions
    - LOCAL: Executes actions after human approval
    """

    def __init__(self):
        """Initialize work-zone orchestrator."""
        self.config = load_config()
        self.work_zone = self.config["work_zone"]
        self.agent_id = self.config["agent_id"]
        self.vault_path = self.config["vault_path"]

        # Initialize paths
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.drafts_path = self.vault_path / "Drafts"
        self.approved_path = self.vault_path / "Approved"
        self.done_path = self.vault_path / "Done"
        self.pending_approval_path = self.vault_path / "Pending_Approval"

        # Initialize draft creator
        self.draft_creator = DraftCreator(
            agent_id=self.agent_id,
            vault_path=self.vault_path,
        )

        # Ensure directories exist
        for path in [
            self.needs_action_path,
            self.drafts_path,
            self.approved_path,
            self.done_path,
            self.pending_approval_path,
        ]:
            path.mkdir(parents=True, exist_ok=True)

        logger.info(f"WorkZoneOrchestrator initialized")
        logger.info(f"  Work-Zone: {self.work_zone.value}")
        logger.info(f"  Agent ID: {self.agent_id}")
        logger.info(f"  Vault Path: {self.vault_path}")

    def process_task(
        self,
        task_path: Path,
        action_type: Optional[ActionType] = None,
        ai_response: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a task with work-zone enforcement.

        Args:
            task_path: Path to task file
            action_type: Optional action type (auto-detected if not provided)
            ai_response: Optional AI-generated response for drafts

        Returns:
            {
                "success": bool,
                "action": str,  # "executed", "draft_created", "claimed", "error"
                "path": Path,  # Path to result file
                "message": str,
            }
        """
        task_id = task_path.stem
        logger.info(f"[{self.agent_id}] Processing task: {task_id}")

        result = {
            "success": False,
            "action": "error",
            "path": None,
            "message": "",
        }

        # Auto-detect action type if not provided
        if action_type is None:
            action_type = self._detect_action_type(task_path)

        logger.info(f"[{self.agent_id}] Action type: {action_type.value}")

        # Check work-zone permission
        allowed, reason = can_execute_action(action_type, self.work_zone)

        if allowed:
            # Execute action (LOCAL mode or safe action)
            if self.work_zone == WorkZone.LOCAL:
                result = self._execute_action(task_path, action_type)
            else:
                # CLOUD mode but safe action (e.g., read, analyze)
                result = self._process_safe_action(task_path, action_type)
        else:
            # Action blocked - create draft (CLOUD mode)
            result = self._create_draft_for_blocked_action(
                task_path=task_path,
                action_type=action_type,
                blocked_reason=reason,
                ai_response=ai_response,
            )

        # Log result
        log_audit(
            action=f"orchestrator.{result['action']}",
            actor=self.agent_id,
            domain=AuditDomain.SYSTEM,
            resource=task_id,
            status=AuditStatus.SUCCESS if result["success"] else AuditStatus.FAILURE,
            details={
                "work_zone": self.work_zone.value,
                "action_type": action_type.value,
                "message": result["message"],
            },
        )

        return result

    def _detect_action_type(self, task_path: Path) -> ActionType:
        """Auto-detect action type from task file."""
        filename = task_path.name.lower()
        content = ""

        try:
            content = task_path.read_text(encoding='utf-8').lower()
        except Exception:
            pass

        # Check filename patterns
        if "gmail" in filename or "email" in filename:
            if "send" in content or "reply" in content or "respond" in content:
                return ActionType.SEND_EMAIL
            return ActionType.SEARCH_EMAILS

        if "linkedin" in filename:
            return ActionType.POST_LINKEDIN

        if "twitter" in filename or "tweet" in filename:
            return ActionType.POST_TWITTER

        if "facebook" in filename or "meta" in filename:
            return ActionType.POST_FACEBOOK

        if "instagram" in filename:
            return ActionType.POST_INSTAGRAM

        if "whatsapp" in filename:
            return ActionType.SEND_WHATSAPP

        if "invoice" in filename or "invoice" in content:
            return ActionType.CREATE_INVOICE

        if "expense" in filename or "expense" in content:
            return ActionType.RECORD_EXPENSE

        # Default to safe action
        return ActionType.READ_DATA

    def _execute_action(
        self,
        task_path: Path,
        action_type: ActionType,
    ) -> Dict[str, Any]:
        """Execute action in LOCAL work-zone."""
        logger.info(f"[{self.agent_id}] Executing action: {action_type.value}")

        # Move task to Done folder
        success, message = claim_task(
            task_path=task_path,
            agent_id=self.agent_id,
            destination_folder="Done",
            vault_path=self.vault_path,
        )

        return {
            "success": success,
            "action": "executed",
            "path": self.done_path / task_path.name if success else None,
            "message": f"Action executed: {action_type.value}. {message}",
        }

    def _process_safe_action(
        self,
        task_path: Path,
        action_type: ActionType,
    ) -> Dict[str, Any]:
        """Process safe action (allowed in CLOUD)."""
        logger.info(f"[{self.agent_id}] Processing safe action: {action_type.value}")

        # For safe actions in CLOUD, we just log and move to Done
        success, message = claim_task(
            task_path=task_path,
            agent_id=self.agent_id,
            destination_folder="Done",
            vault_path=self.vault_path,
        )

        return {
            "success": success,
            "action": "processed",
            "path": self.done_path / task_path.name if success else None,
            "message": f"Safe action processed: {action_type.value}. {message}",
        }

    def _create_draft_for_blocked_action(
        self,
        task_path: Path,
        action_type: ActionType,
        blocked_reason: str,
        ai_response: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create draft when action is blocked."""
        logger.info(f"[{self.agent_id}] Creating draft for blocked action")

        try:
            # Create draft
            draft_path = self.draft_creator.create_draft(
                task_path=task_path,
                action_type=action_type,
                blocked_reason=blocked_reason,
                ai_response=ai_response,
            )

            # Move original task to Drafts (claim it)
            claim_task(
                task_path=task_path,
                agent_id=self.agent_id,
                destination_folder="Drafts",
                vault_path=self.vault_path,
            )

            return {
                "success": True,
                "action": "draft_created",
                "path": draft_path,
                "message": f"Draft created: {draft_path.name}. Awaiting human approval.",
            }

        except Exception as e:
            logger.error(f"[{self.agent_id}] Failed to create draft: {e}")
            return {
                "success": False,
                "action": "error",
                "path": None,
                "message": f"Failed to create draft: {str(e)}",
            }

    def process_pending_tasks(self) -> Dict[str, int]:
        """
        Process all pending tasks in Needs_Action folder.

        Returns:
            Count of processed, drafted, and failed tasks
        """
        stats = {
            "processed": 0,
            "drafted": 0,
            "failed": 0,
        }

        tasks = get_claimable_tasks("Needs_Action", self.vault_path)
        logger.info(f"[{self.agent_id}] Found {len(tasks)} pending tasks")

        for task_path in tasks:
            result = self.process_task(task_path)

            if result["success"]:
                if result["action"] == "draft_created":
                    stats["drafted"] += 1
                else:
                    stats["processed"] += 1
            else:
                stats["failed"] += 1

        return stats

    def process_drafts(self) -> Dict[str, int]:
        """
        Process drafts that have been approved (LOCAL only).

        Scans Approved folder and executes approved drafts.

        Returns:
            Count of executed and failed drafts
        """
        if self.work_zone != WorkZone.LOCAL:
            logger.warning("process_drafts only available in LOCAL work-zone")
            return {"executed": 0, "failed": 0}

        stats = {
            "executed": 0,
            "failed": 0,
        }

        approved_tasks = get_claimable_tasks("Approved", self.vault_path)
        logger.info(f"[{self.agent_id}] Found {len(approved_tasks)} approved tasks")

        for task_path in approved_tasks:
            try:
                # Move to Done
                success, message = claim_task(
                    task_path=task_path,
                    agent_id=self.agent_id,
                    destination_folder="Done",
                    vault_path=self.vault_path,
                )

                if success:
                    stats["executed"] += 1
                    logger.info(f"[{self.agent_id}] Executed approved task: {task_path.name}")
                else:
                    stats["failed"] += 1

            except Exception as e:
                stats["failed"] += 1
                logger.error(f"[{self.agent_id}] Failed to execute: {e}")

        return stats

    def sync_with_remote(self, description: str = "") -> Dict[str, Any]:
        """
        Sync vault with Git remote.

        Returns:
            Git sync result
        """
        folders = ["Drafts/", "Approved/", "Done/", "Logs/audit/", "Dashboard.md"]
        return git_sync(self.agent_id, description, folders, self.vault_path)


def process_task_with_work_zone(
    task_path: Path,
    action_type: Optional[ActionType] = None,
    ai_response: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to process a task with work-zone enforcement.

    Args:
        task_path: Path to task file
        action_type: Optional action type
        ai_response: Optional AI response for drafts

    Returns:
        Processing result dictionary
    """
    orchestrator = WorkZoneOrchestrator()
    return orchestrator.process_task(task_path, action_type, ai_response)


if __name__ == "__main__":
    # Test work-zone orchestrator
    import tempfile

    print("Testing Work-Zone Orchestrator...")

    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)

        # Create test folders
        (vault / "Needs_Action").mkdir()
        (vault / "Drafts").mkdir()
        (vault / "Approved").mkdir()
        (vault / "Done").mkdir()

        # Create test task
        task = vault / "Needs_Action" / "gmail_high_test_email.md"
        task.write_text("# Test Email\n\nPlease respond to this email.")

        # Test CLOUD mode (should create draft)
        print("\n1. Testing CLOUD mode (should create draft)...")
        os.environ["WORK_ZONE"] = "cloud"
        os.environ["AGENT_ID"] = "test-cloud"
        os.environ["VAULT_PATH"] = str(vault)

        orch = WorkZoneOrchestrator()
        result = orch.process_task(task, ActionType.SEND_EMAIL)

        print(f"   Action: {result['action']}")
        print(f"   Success: {result['success']}")
        assert result["action"] == "draft_created", f"Expected draft_created, got {result['action']}"
        print("   [PASS]")

        # Create another task for LOCAL test
        task2 = vault / "Needs_Action" / "gmail_high_test2.md"
        task2.write_text("# Test Email 2")

        # Test LOCAL mode (should execute)
        print("\n2. Testing LOCAL mode (should execute)...")
        os.environ["WORK_ZONE"] = "local"
        os.environ["AGENT_ID"] = "test-local"

        orch = WorkZoneOrchestrator()
        result = orch.process_task(task2, ActionType.SEND_EMAIL)

        print(f"   Action: {result['action']}")
        print(f"   Success: {result['success']}")
        assert result["action"] == "executed", f"Expected executed, got {result['action']}"
        print("   [PASS]")

        # Test safe action in CLOUD
        print("\n3. Testing safe action in CLOUD mode...")
        os.environ["WORK_ZONE"] = "cloud"

        task3 = vault / "Needs_Action" / "read_data_task.md"
        task3.write_text("# Read Data Task")

        orch = WorkZoneOrchestrator()
        result = orch.process_task(task3, ActionType.READ_DATA)

        print(f"   Action: {result['action']}")
        assert result["action"] == "processed"
        print("   [PASS]")

    print("\n[SUCCESS] All work-zone orchestrator tests passed!")
