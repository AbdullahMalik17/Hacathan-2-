import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

import watchers.linkedin_watcher as linkedin_watcher

class TestLinkedInWatcher(unittest.TestCase):
    def test_imports(self):
        """Verify module can be imported and constants are set."""
        self.assertTrue(hasattr(linkedin_watcher, "LinkedInWatcher"))
        self.assertTrue(hasattr(linkedin_watcher, "LINKEDIN_NOTIFICATIONS_URL"))

    @patch('watchers.linkedin_watcher.NEEDS_ACTION_PATH')
    def test_create_task_file(self, mock_path):
        """Test task file creation."""
        mock_path.__truediv__.return_value = Path("test_task.md")
        
        # Mock file writing
        with patch('builtins.open', new_callable=MagicMock):
            result = linkedin_watcher.create_task_file(
                "message", 
                "Recruiter", 
                "Hi, I have a job", 
                "http://linkedin.com/msg/123"
            )
            self.assertIsNotNone(result)

if __name__ == "__main__":
    unittest.main()
