import unittest
import os
import shutil
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from watchers.filesystem_watcher import FileHandler
from reports.ceo_briefing import calculate_roi, generate_briefing_report

class TestSprint2(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_sprint2")
        self.test_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch('time.sleep', return_value=None)
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.stat')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('watchers.filesystem_watcher.log_action')
    def test_fs_watcher_rate_limiting(self, mock_log, mock_open, mock_stat, mock_exists, mock_sleep):
        # Setup handler with low rate limit for testing
        handler = FileHandler(rate_limit=2)
        
        # Mock stat
        mock_stat.return_value.st_size = 100
        
        # Mock task creation to not actually write files
        with patch('watchers.filesystem_watcher.create_task_file') as mock_create:
            mock_create.return_value = Path("dummy.md")
            
            # Simulate 3 events
            mock_event = MagicMock()
            mock_event.is_directory = False
            mock_event.src_path = "test_file.txt"
            
            # 1st event - allowed
            mock_event.src_path = "file1.txt"
            handler.on_created(mock_event)
            self.assertEqual(len(handler.task_history), 1)
            
            # 2nd event - allowed
            mock_event.src_path = "file2.txt"
            handler.on_created(mock_event)
            self.assertEqual(len(handler.task_history), 2)
            
            # 3rd event - should be blocked by rate limit
            mock_event.src_path = "file3.txt"
            handler.on_created(mock_event)
            self.assertEqual(len(handler.task_history), 2)

    def test_roi_calculation(self):
        test_entries = [
            {"action": "file_detected", "result": "success"},
            {"action": "email_sent", "result": "success"},
            {"action": "unknown", "result": "success"},
            {"action": "error_recovery", "result": "success"}
        ]
        # ROI_VALUES: file_detected=1.0, email_sent=2.0, error_recovery=5.0, unknown=0.5
        # Total = 1 + 2 + 0.5 + 5 = 8.5
        roi = calculate_roi(test_entries)
        self.assertEqual(roi, 8.5)

    @patch('reports.ceo_briefing.get_ai_narrative')
    def test_briefing_generation(self, mock_ai):
        mock_ai.return_value = "## AI Narrative Summary\nEverything is great."
        
        from datetime import datetime
        report = generate_briefing_report(
            start_date=datetime(2026, 1, 1),
            end_date=datetime(2026, 1, 7),
            entries=[],
            sources={"Gmail": 5, "Filesystem": 2},
            actions={"email_sent": 5, "file_detected": 2},
            errors=[],
            pending=[]
        )
        
        self.assertIn("CEO Weekly Briefing", report)
        self.assertIn("AI Narrative Summary", report)
        self.assertIn("Everything is great", report)
        self.assertIn("Estimated ROI", report)

if __name__ == "__main__":
    unittest.main()
