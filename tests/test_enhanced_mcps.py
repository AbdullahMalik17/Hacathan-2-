import unittest
from unittest.mock import patch, MagicMock
import sys
import json
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Mock fastmcp before importing modules
sys.modules["fastmcp"] = MagicMock()
from src.mcp_servers import odoo_server, meta_social_connector, twitter_connector, google_calendar_server

class TestEnhancedMCPs(unittest.TestCase):
    
    def test_odoo_enhancements(self):
        """Test new Odoo tools exist."""
        self.assertTrue(hasattr(odoo_server, "list_products"))
        self.assertTrue(hasattr(odoo_server, "get_partner_details"))

    def test_meta_enhancements(self):
        """Test new Meta tools exist."""
        self.assertTrue(hasattr(meta_social_connector, "get_page_info"))

    def test_twitter_enhancements(self):
        """Test new Twitter tools exist."""
        self.assertTrue(hasattr(twitter_connector, "get_user_info"))

    def test_google_calendar_implementation(self):
        """Test Google Calendar server exists and has basic tools."""
        self.assertTrue(hasattr(google_calendar_server, "list_events"))
        self.assertTrue(hasattr(google_calendar_server, "create_event"))
        self.assertTrue(hasattr(google_calendar_server, "update_event"))
        self.assertTrue(hasattr(google_calendar_server, "delete_event"))

    @patch("src.mcp_servers.google_calendar_server.get_calendar_service")
    def test_calendar_list_events(self, mock_service):
        """Test list_events logic."""
        # Mock the service chain: service.events().list().execute()
        mock_list = MagicMock()
        mock_execute = MagicMock()
        
        mock_service.return_value.events.return_value.list.return_value = mock_list
        mock_list.execute.return_value = {
            "items": [
                {
                    "id": "123",
                    "summary": "Test Event",
                    "start": {"dateTime": "2023-01-01T10:00:00Z"},
                    "end": {"dateTime": "2023-01-01T11:00:00Z"}
                }
            ]
        }
        
        result = google_calendar_server._list_events_logic()
        data = json.loads(result)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["summary"], "Test Event")

if __name__ == "__main__":
    unittest.main()
