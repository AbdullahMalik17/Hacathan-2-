import unittest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from mcp_servers import whatsapp_server

class TestWhatsAppMCP(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_whatsapp_mcp")
        self.queue_path = self.test_dir / "Queue"
        self.pending_path = self.test_dir / "Pending"
        self.queue_path.mkdir(parents=True, exist_ok=True)
        self.pending_path.mkdir(parents=True, exist_ok=True)
        
        # Override paths
        whatsapp_server.QUEUE_PATH = self.queue_path
        whatsapp_server.PENDING_PATH = self.pending_path

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_send_approval(self):
        result = whatsapp_server._send_logic("Alice", "Hello", requires_approval=True)
        self.assertIn("queued for approval", result)
        
        files = list(self.pending_path.glob("*.md"))
        self.assertEqual(len(files), 1)
        self.assertIn("Alice", files[0].name)

    def test_send_direct(self):
        result = whatsapp_server._send_logic("Bob", "Urgent", requires_approval=False)
        self.assertIn("queued for sending", result)
        
        files = list(self.queue_path.glob("SEND_*.md"))
        self.assertEqual(len(files), 1)
        self.assertIn("Bob", files[0].name)

if __name__ == "__main__":
    unittest.main()
