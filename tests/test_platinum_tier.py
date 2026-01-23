"""
Platinum Tier Integration Tests

Tests for the dual-agent architecture:
- Work-zone enforcement
- Claim-by-move pattern
- Draft creation
- Cloud/Local agent integration
- Git sync functionality
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import load_config, WorkZone
from src.utils.work_zone import (
    ActionType,
    can_execute_action,
    is_sensitive_action,
    get_action_type_from_string,
)
from src.utils.claim_by_move import claim_task, get_claimable_tasks
from src.utils.draft_creator import DraftCreator, create_draft
from src.utils.orchestrator_work_zone import WorkZoneOrchestrator


class TestWorkZoneEnforcement:
    """Tests for work-zone permission enforcement."""

    def test_cloud_blocks_send_email(self, monkeypatch):
        """Cloud work-zone should block send_email action."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        allowed, reason = can_execute_action(ActionType.SEND_EMAIL, WorkZone.CLOUD)
        assert not allowed
        assert "LOCAL" in reason

    def test_cloud_blocks_post_social(self, monkeypatch):
        """Cloud work-zone should block social media posting."""
        monkeypatch.setenv("WORK_ZONE", "cloud")

        for action in [
            ActionType.POST_LINKEDIN,
            ActionType.POST_TWITTER,
            ActionType.POST_FACEBOOK,
            ActionType.POST_INSTAGRAM,
        ]:
            allowed, _ = can_execute_action(action, WorkZone.CLOUD)
            assert not allowed, f"{action.value} should be blocked in CLOUD"

    def test_cloud_blocks_financial(self, monkeypatch):
        """Cloud work-zone should block financial actions."""
        monkeypatch.setenv("WORK_ZONE", "cloud")

        for action in [ActionType.CREATE_INVOICE, ActionType.RECORD_EXPENSE]:
            allowed, _ = can_execute_action(action, WorkZone.CLOUD)
            assert not allowed, f"{action.value} should be blocked in CLOUD"

    def test_cloud_allows_safe_actions(self, monkeypatch):
        """Cloud work-zone should allow safe actions."""
        monkeypatch.setenv("WORK_ZONE", "cloud")

        for action in [
            ActionType.READ_DATA,
            ActionType.CREATE_DRAFT,
            ActionType.ANALYZE_DATA,
            ActionType.GIT_SYNC,
        ]:
            allowed, _ = can_execute_action(action, WorkZone.CLOUD)
            assert allowed, f"{action.value} should be allowed in CLOUD"

    def test_local_allows_all(self, monkeypatch):
        """Local work-zone should allow all actions."""
        monkeypatch.setenv("WORK_ZONE", "local")

        for action in ActionType:
            allowed, _ = can_execute_action(action, WorkZone.LOCAL)
            assert allowed, f"{action.value} should be allowed in LOCAL"

    def test_sensitive_action_classification(self):
        """Verify sensitive actions are classified correctly."""
        sensitive = [
            ActionType.SEND_EMAIL,
            ActionType.POST_LINKEDIN,
            ActionType.CREATE_INVOICE,
            ActionType.SEND_WHATSAPP,
        ]

        for action in sensitive:
            assert is_sensitive_action(action), f"{action.value} should be sensitive"

        safe = [
            ActionType.READ_DATA,
            ActionType.CREATE_DRAFT,
            ActionType.GIT_SYNC,
        ]

        for action in safe:
            assert not is_sensitive_action(action), f"{action.value} should not be sensitive"


class TestClaimByMove:
    """Tests for atomic task claiming."""

    def test_claim_moves_file(self, tmp_path):
        """Claim should move file to destination."""
        # Setup
        needs_action = tmp_path / "Needs_Action"
        drafts = tmp_path / "Drafts"
        needs_action.mkdir()
        drafts.mkdir()

        task = needs_action / "test_task.md"
        task.write_text("# Test Task")

        # Claim
        success, msg = claim_task(task, "test-agent", "Drafts", tmp_path)

        assert success
        assert (drafts / "test_task.md").exists()
        assert not task.exists()

    def test_double_claim_fails(self, tmp_path):
        """Second claim attempt should fail."""
        # Setup
        needs_action = tmp_path / "Needs_Action"
        drafts = tmp_path / "Drafts"
        needs_action.mkdir()
        drafts.mkdir()

        task = needs_action / "test_task.md"
        task.write_text("# Test Task")

        # First claim
        success1, _ = claim_task(task, "agent-1", "Drafts", tmp_path)
        assert success1

        # Second claim (same path, file no longer exists)
        success2, msg = claim_task(task, "agent-2", "Drafts", tmp_path)
        assert not success2
        assert "already claimed" in msg.lower()

    def test_get_claimable_tasks(self, tmp_path):
        """Should list claimable tasks."""
        needs_action = tmp_path / "Needs_Action"
        needs_action.mkdir()

        # Create test tasks
        for i in range(5):
            (needs_action / f"task_{i}.md").write_text(f"# Task {i}")

        # Create files to exclude
        (needs_action / "README.md").write_text("# README")
        (needs_action / ".gitkeep").write_text("")

        tasks = get_claimable_tasks("Needs_Action", tmp_path)

        assert len(tasks) == 5
        assert all("README" not in t.name for t in tasks)


class TestDraftCreation:
    """Tests for draft creation."""

    def test_draft_created_with_frontmatter(self, tmp_path, monkeypatch):
        """Draft should have YAML frontmatter."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("AGENT_ID", "test-cloud")
        monkeypatch.setenv("VAULT_PATH", str(tmp_path))

        drafts = tmp_path / "Drafts"
        needs_action = tmp_path / "Needs_Action"
        drafts.mkdir()
        needs_action.mkdir()

        task = needs_action / "gmail_high_test.md"
        task.write_text("# Test Email Task")

        creator = DraftCreator(agent_id="test-cloud", vault_path=tmp_path)
        draft_path = creator.create_draft(
            task_path=task,
            action_type=ActionType.SEND_EMAIL,
            blocked_reason="Blocked in CLOUD",
        )

        content = draft_path.read_text()

        assert "---" in content  # YAML frontmatter
        assert "status: draft" in content
        assert "SEND_EMAIL" in content.upper() or "send_email" in content

    def test_draft_includes_original_task(self, tmp_path, monkeypatch):
        """Draft should include original task content."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("AGENT_ID", "test-cloud")
        monkeypatch.setenv("VAULT_PATH", str(tmp_path))

        drafts = tmp_path / "Drafts"
        needs_action = tmp_path / "Needs_Action"
        drafts.mkdir()
        needs_action.mkdir()

        task = needs_action / "test_task.md"
        original_content = "# Original Task\n\nThis is the original content."
        task.write_text(original_content)

        creator = DraftCreator(agent_id="test-cloud", vault_path=tmp_path)
        draft_path = creator.create_draft(
            task_path=task,
            action_type=ActionType.SEND_EMAIL,
            blocked_reason="Blocked",
        )

        draft_content = draft_path.read_text()
        assert "Original Task" in draft_content

    def test_draft_includes_ai_response(self, tmp_path, monkeypatch):
        """Draft should include AI response when provided."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("AGENT_ID", "test-cloud")
        monkeypatch.setenv("VAULT_PATH", str(tmp_path))

        drafts = tmp_path / "Drafts"
        needs_action = tmp_path / "Needs_Action"
        drafts.mkdir()
        needs_action.mkdir()

        task = needs_action / "test_task.md"
        task.write_text("# Test")

        ai_response = "Dear User,\n\nThank you for your email.\n\nBest regards"

        creator = DraftCreator(agent_id="test-cloud", vault_path=tmp_path)
        draft_path = creator.create_draft(
            task_path=task,
            action_type=ActionType.SEND_EMAIL,
            blocked_reason="Blocked",
            ai_response=ai_response,
        )

        draft_content = draft_path.read_text()
        assert "Dear User" in draft_content


class TestOrchestratorWorkZone:
    """Tests for work-zone aware orchestrator."""

    def test_cloud_creates_draft_for_email(self, tmp_path, monkeypatch):
        """Cloud orchestrator should create draft for email action."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("AGENT_ID", "test-cloud")
        monkeypatch.setenv("VAULT_PATH", str(tmp_path))

        # Setup folders
        for folder in ["Needs_Action", "Drafts", "Done", "Approved", "Pending_Approval"]:
            (tmp_path / folder).mkdir()

        task = tmp_path / "Needs_Action" / "gmail_test.md"
        task.write_text("# Email Task")

        orch = WorkZoneOrchestrator()
        result = orch.process_task(task, ActionType.SEND_EMAIL)

        assert result["success"]
        assert result["action"] == "draft_created"
        assert result["path"] is not None

    def test_local_executes_email(self, tmp_path, monkeypatch):
        """Local orchestrator should execute email action."""
        monkeypatch.setenv("WORK_ZONE", "local")
        monkeypatch.setenv("AGENT_ID", "test-local")
        monkeypatch.setenv("VAULT_PATH", str(tmp_path))

        # Setup folders
        for folder in ["Needs_Action", "Drafts", "Done", "Approved", "Pending_Approval"]:
            (tmp_path / folder).mkdir()

        task = tmp_path / "Needs_Action" / "gmail_test.md"
        task.write_text("# Email Task")

        orch = WorkZoneOrchestrator()
        result = orch.process_task(task, ActionType.SEND_EMAIL)

        assert result["success"]
        assert result["action"] == "executed"

    def test_cloud_processes_safe_action(self, tmp_path, monkeypatch):
        """Cloud orchestrator should process safe actions directly."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("AGENT_ID", "test-cloud")
        monkeypatch.setenv("VAULT_PATH", str(tmp_path))

        # Setup folders
        for folder in ["Needs_Action", "Drafts", "Done", "Approved", "Pending_Approval"]:
            (tmp_path / folder).mkdir()

        task = tmp_path / "Needs_Action" / "read_data_task.md"
        task.write_text("# Read Data Task")

        orch = WorkZoneOrchestrator()
        result = orch.process_task(task, ActionType.READ_DATA)

        assert result["success"]
        assert result["action"] == "processed"

    def test_action_type_detection(self, tmp_path, monkeypatch):
        """Orchestrator should detect action type from filename."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("AGENT_ID", "test-cloud")
        monkeypatch.setenv("VAULT_PATH", str(tmp_path))

        # Setup
        for folder in ["Needs_Action", "Drafts", "Done", "Approved", "Pending_Approval"]:
            (tmp_path / folder).mkdir()

        orch = WorkZoneOrchestrator()

        # Test email detection
        task1 = tmp_path / "Needs_Action" / "gmail_high_test.md"
        task1.write_text("# Email\n\nPlease reply to this.")
        detected = orch._detect_action_type(task1)
        assert detected == ActionType.SEND_EMAIL

        # Test LinkedIn detection
        task2 = tmp_path / "Needs_Action" / "linkedin_post.md"
        task2.write_text("# LinkedIn Post")
        detected = orch._detect_action_type(task2)
        assert detected == ActionType.POST_LINKEDIN


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_full_workflow_cloud_to_local(self, tmp_path, monkeypatch):
        """Test complete workflow: Cloud draft → Local approval → Execution."""
        # Setup vault
        for folder in ["Needs_Action", "Drafts", "Approved", "Done", "Pending_Approval"]:
            (tmp_path / folder).mkdir()

        # === CLOUD PHASE ===
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("AGENT_ID", "cloud-test")
        monkeypatch.setenv("VAULT_PATH", str(tmp_path))

        # Create incoming task
        task = tmp_path / "Needs_Action" / "gmail_high_urgent_reply.md"
        task.write_text("# Urgent Email\n\nPlease reply to the CEO.")

        # Cloud processes task (should create draft)
        cloud_orch = WorkZoneOrchestrator()
        cloud_result = cloud_orch.process_task(task, ActionType.SEND_EMAIL)

        assert cloud_result["success"]
        assert cloud_result["action"] == "draft_created"
        draft_path = cloud_result["path"]
        assert draft_path.exists()

        # === HUMAN APPROVAL (simulated) ===
        # Move draft to Approved folder
        approved_path = tmp_path / "Approved" / draft_path.name
        draft_path.rename(approved_path)

        # === LOCAL PHASE ===
        monkeypatch.setenv("WORK_ZONE", "local")
        monkeypatch.setenv("AGENT_ID", "local-test")

        # Local processes approved task
        local_orch = WorkZoneOrchestrator()
        local_result = local_orch.process_drafts()

        assert local_result["executed"] == 1
        assert local_result["failed"] == 0

        # Verify task is in Done
        done_tasks = list((tmp_path / "Done").glob("*.md"))
        assert len(done_tasks) == 1


class TestConfigurationValidation:
    """Tests for configuration validation."""

    def test_cloud_config_no_mcp(self, monkeypatch):
        """Cloud config should have MCP servers disabled."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("EMAIL_MCP_ENABLED", "false")
        monkeypatch.setenv("ODOO_MCP_ENABLED", "false")

        config = load_config()
        assert config["work_zone"] == WorkZone.CLOUD
        assert not config["mcp_servers"]["email"]["enabled"]
        assert not config["mcp_servers"]["odoo"]["enabled"]

    def test_local_config_with_mcp(self, monkeypatch):
        """Local config should have MCP servers enabled."""
        monkeypatch.setenv("WORK_ZONE", "local")
        monkeypatch.setenv("EMAIL_MCP_ENABLED", "true")
        monkeypatch.setenv("ODOO_MCP_ENABLED", "true")

        config = load_config()
        assert config["work_zone"] == WorkZone.LOCAL
        assert config["mcp_servers"]["email"]["enabled"]
        assert config["mcp_servers"]["odoo"]["enabled"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
