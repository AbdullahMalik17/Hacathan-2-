import unittest
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from orchestrator import DigitalFTEOrchestrator

class TestPlatinumLogic(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_platinum")
        self.vault_path = self.test_dir / "Vault"
        self.needs_action = self.vault_path / "Needs_Action"
        self.in_progress_cloud = self.vault_path / "In_Progress" / "cloud"
        self.in_progress_local = self.vault_path / "In_Progress" / "local"
        
        for p in [self.needs_action, self.in_progress_cloud, self.in_progress_local]:
            p.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_claim_by_move(self):
        # Create a task
        task_file = self.needs_action / "test_task.md"
        task_file.write_text("Test content")
        
        # 1. Initialize Cloud Orchestrator
        with patch('orchestrator.VAULT_PATH', self.vault_path), \
             patch('orchestrator.FTE_ROLE', 'cloud'), \
             patch('orchestrator.IN_PROGRESS_PATH', self.in_progress_cloud):
            
            orch_cloud = DigitalFTEOrchestrator(dry_run=True)
            
            # Claim task as cloud
            claimed_path = orch_cloud._claim_task(task_file)
            
            self.assertIsNotNone(claimed_path)
            self.assertTrue(claimed_path.exists())
            self.assertTrue("In_Progress" in str(claimed_path) and "cloud" in str(claimed_path))
            self.assertFalse(task_file.exists()) # Should be moved

        # 2. Try to claim same task as local
        with patch('orchestrator.VAULT_PATH', self.vault_path), \
             patch('orchestrator.FTE_ROLE', 'local'), \
             patch('orchestrator.IN_PROGRESS_PATH', self.in_progress_local):
            
            orch_local = DigitalFTEOrchestrator(dry_run=True)
            
            # Local tries to claim from Needs_Action (where it used to be)
            failed_claim = orch_local._claim_task(task_file)
            self.assertIsNone(failed_claim)

    def test_cloud_forced_approval(self):
        # This tests the logic in email_sender.py
        from mcp_servers import email_sender
        
        # Mock paths
        email_sender.PENDING_PATH = self.test_dir / "Pending"
        email_sender.PENDING_PATH.mkdir(exist_ok=True)
        
        # Scenario: Cloud tries to send email with requires_approval=False
        with patch.dict(os.environ, {"FTE_ROLE": "cloud"}):
            # We don't call the actual tool (it's a Tool object), we call the logic
            result = email_sender._send_email_logic(
                to="test@e.com",
                subject="Test",
                body="Body",
                requires_approval=False # Trying to bypass
            )
            
            self.assertIn("queued for approval", result)
            # Verify file created despite requires_approval=False
            files = list(email_sender.PENDING_PATH.glob("*.md"))
            self.assertEqual(len(files), 1)

if __name__ == "__main__":
    unittest.main()
