"""
Google Calendar MCP Server - Calendar Management

Provides MCP tools for Google Calendar:
- List events
- Create events
- Update events
- Delete events
- Check availability

Uses Google Calendar API.
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from fastmcp import FastMCP

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils.google_auth import get_calendar_service
from utils.audit_logger import log_audit, AuditDomain, AuditStatus

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Configuration
CONFIG_PATH = PROJECT_ROOT / "config"
CREDENTIALS_FILE = CONFIG_PATH / "credentials.json"
TOKEN_FILE = CONFIG_PATH / "token_calendar.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GoogleCalendarMCP")

# Initialize MCP
mcp = FastMCP("Google Calendar")


@mcp.tool()
def list_events(
    calendar_id: str = 'primary',
    max_results: int = 10,
    time_min: str = None,
    time_max: str = None
) -> str:
    """
    List upcoming events from a calendar.

    Args:
        calendar_id: Calendar ID (default: 'primary')
        max_results: Maximum number of events to return
        time_min: Start time (ISO format), defaults to now
        time_max: End time (ISO format)

    Returns:
        JSON string of events
    """
    return _list_events_logic(calendar_id, max_results, time_min, time_max)

def _list_events_logic(
    calendar_id: str = 'primary',
    max_results: int = 10,
    time_min: str = None,
    time_max: str = None
) -> str:
    try:
        service = get_calendar_service(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        
        if not time_min:
            time_min = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        processed_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            processed_events.append({
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'start': start,
                'end': end,
                'location': event.get('location'),
                'description': event.get('description'),
                'link': event.get('htmlLink')
            })
            
        log_audit(
            action="calendar.list_events",
            actor="calendar_mcp",
            domain=AuditDomain.PERSONAL,
            resource=calendar_id,
            status=AuditStatus.SUCCESS,
            details={"count": len(events)}
        )
        
        return json.dumps(processed_events, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing events: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = None,
    location: str = None,
    attendees: List[str] = None,
    calendar_id: str = 'primary'
) -> str:
    """
    Create a new event in the calendar.

    Args:
        summary: Event title
        start_time: Start time (ISO format, e.g., '2023-01-01T10:00:00')
        end_time: End time (ISO format)
        description: Event description
        location: Event location
        attendees: List of attendee email addresses
        calendar_id: Calendar ID (default: 'primary')

    Returns:
        JSON string with created event details
    """
    try:
        service = get_calendar_service(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC', # Adjust as needed or make configurable
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
            
        event = service.events().insert(calendarId=calendar_id, body=event).execute()
        
        log_audit(
            action="calendar.create_event",
            actor="calendar_mcp",
            domain=AuditDomain.PERSONAL,
            resource=calendar_id,
            status=AuditStatus.SUCCESS,
            details={"summary": summary, "event_id": event.get('id')}
        )
        
        return json.dumps({
            "message": "Event created successfully",
            "id": event.get('id'),
            "link": event.get('htmlLink')
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def update_event(
    event_id: str,
    calendar_id: str = 'primary',
    summary: str = None,
    description: str = None,
    location: str = None
) -> str:
    """
    Update an existing event.

    Args:
        event_id: Event ID to update
        calendar_id: Calendar ID (default: 'primary')
        summary: New title (optional)
        description: New description (optional)
        location: New location (optional)

    Returns:
        JSON string with updated event details
    """
    try:
        service = get_calendar_service(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        
        # First retrieve the event
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        if summary:
            event['summary'] = summary
        if description:
            event['description'] = description
        if location:
            event['location'] = location
            
        updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        
        log_audit(
            action="calendar.update_event",
            actor="calendar_mcp",
            domain=AuditDomain.PERSONAL,
            resource=calendar_id,
            status=AuditStatus.SUCCESS,
            details={"event_id": event_id}
        )
        
        return json.dumps({
            "message": "Event updated successfully",
            "link": updated_event.get('htmlLink')
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error updating event: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def delete_event(event_id: str, calendar_id: str = 'primary') -> str:
    """
    Delete an event from the calendar.

    Args:
        event_id: Event ID to delete
        calendar_id: Calendar ID (default: 'primary')

    Returns:
        JSON string with result
    """
    try:
        service = get_calendar_service(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        
        log_audit(
            action="calendar.delete_event",
            actor="calendar_mcp",
            domain=AuditDomain.PERSONAL,
            resource=calendar_id,
            status=AuditStatus.SUCCESS,
            details={"event_id": event_id}
        )
        
        return json.dumps({"message": "Event deleted successfully"}, indent=2)
        
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
