import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import shutil
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Mock configuration before importing
with patch.dict(os.environ, {"GMAIL_TOKEN": "mock_token"}):
    from src.mcp_servers import email_sender

class TestEmailMCP(unittest.TestCase):
    def setUp(self):
        # Setup paths
        self.test_dir = Path("test_vault")
        self.pending_dir = self.test_dir / "Pending_Approval"
        self.logs_dir = self.test_dir / "Logs"
        self.audit_log = self.logs_dir / "email_audit_log.md"
        self.templates_dir = PROJECT_ROOT / "src" / "templates" / "email"
        
        # Override module paths
        email_sender.PENDING_PATH = self.pending_dir
        email_sender.AUDIT_LOG = self.audit_log
        
        # Create directories
        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Create dummy template
        with open(self.templates_dir / "test_template.j2", "w") as f:
            f.write("Hello {{ name }}")

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        # Remove dummy template
        if (self.templates_dir / "test_template.j2").exists():
            os.remove(self.templates_dir / "test_template.j2")

    @patch("src.mcp_servers.email_sender._send_gmail")
    @patch("src.mcp_servers.email_sender.check_rate_limits")
    def test_recipient_limit(self, mock_rate, mock_send):
        mock_rate.return_value = True
        mock_send.return_value = {'id': '123'}

        # Case 1: Within limit (1 + 2 + 1 = 4)
        result = email_sender._send_email_logic(
            to="test@example.com",
            subject="Test",
            body="Body",
            cc=["cc1@example.com", "cc2@example.com"],
            bcc=["bcc1@example.com"]
        )
        self.assertIn("sent successfully", result)
        mock_send.assert_called_once()

        # Case 2: Exceeded limit (1 + 3 + 2 = 6)
        mock_send.reset_mock()
        result = email_sender._send_email_logic(
            to="test@example.com",
            subject="Test",
            body="Body",
            cc=["1@e.com", "2@e.com", "3@e.com"],
            bcc=["4@e.com", "5@e.com"]
        )
        self.assertIn("Recipient limit exceeded", result)
        mock_send.assert_not_called()

    @patch("src.mcp_servers.email_sender._send_email_logic")
    def test_template_validation(self, mock_send):
        # Case 1: Missing subject
        result = email_sender._send_template_logic(
            template_name="test_template.j2",
            to="test@example.com",
            variables={"name": "Alice"}
        )
        self.assertIn("subject' is required", result)

        # Case 2: Valid
        mock_send.return_value = "Success"
        result = email_sender._send_template_logic(
            template_name="test_template.j2",
            to="test@example.com",
            variables={"name": "Alice", "subject": "Welcome"}
        )
        # Verify send_email was called with correct subject
        mock_send.assert_called_with(
            "test@example.com", 
            "Welcome", 
            "Hello Alice", 
            requires_approval=False
        )

    def test_approval_workflow(self):
        result = email_sender._send_email_logic(
            to="boss@example.com",
            subject="Raise",
            body="Give me money",
            requires_approval=True
        )
        
        self.assertIn("queued for approval", result)
        
        # Verify file creation
        files = list(self.pending_dir.glob("*.md"))
        self.assertEqual(len(files), 1)
        
        with open(files[0], "r") as f:
            content = f.read()
            self.assertIn("status: pending", content)
            self.assertIn("Give me money", content)

if __name__ == "__main__":
    unittest.main()
