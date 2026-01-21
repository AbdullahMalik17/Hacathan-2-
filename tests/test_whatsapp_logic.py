import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import json
import os
import shutil

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

import watchers.whatsapp_watcher as whatsapp_watcher
from utils.contacts import add_contact

class TestWhatsAppLogic(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_whatsapp")
        self.test_dir.mkdir(exist_ok=True)
        self.config_dir = self.test_dir / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Override paths
        self.patcher1 = patch('utils.contacts.CONTACTS_FILE', self.config_dir / "known_contacts.json")
        self.patcher1.start()
        
        # Add a known contact
        add_contact("Alice", {"priority": "high", "auto_reply": True})

    def tearDown(self):
        self.patcher1.stop()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_determine_priority(self):
        p = whatsapp_watcher.determine_priority("I have a question", is_known=True)
        self.assertEqual(p, "high")
        p = whatsapp_watcher.determine_priority("I have a question", is_known=False)
        self.assertEqual(p, "medium")

    def test_escalation_logic(self):
        msg_data = {
            "sender": "Unknown Stranger",
            "message": "Send me the invoice NOW",
            "is_known": False,
            "chat_name": "Unknown Stranger"
        }
        
        with patch('watchers.whatsapp_watcher.NEEDS_ACTION_PATH', self.test_dir):
            filepath = whatsapp_watcher.create_task_file(msg_data)
            self.assertIn("ESCALATION", filepath.name)
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("ESCALATION", content)
                self.assertIn("No", content)

        msg_data["sender"] = "Alice"
        msg_data["is_known"] = True
        msg_data["chat_name"] = "Alice"
        
        with patch('watchers.whatsapp_watcher.NEEDS_ACTION_PATH', self.test_dir):
            filepath = whatsapp_watcher.create_task_file(msg_data)
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Yes", content)

if __name__ == "__main__":
    unittest.main()