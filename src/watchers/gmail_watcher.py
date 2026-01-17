"""
Gmail Watcher - Digital FTE Sensory System

This script monitors Gmail for new important emails and creates
markdown task files in the Obsidian vault for processing.

Setup:
1. Enable Gmail API in Google Cloud Console
2. Download credentials.json to config/ folder
3. Run once to authenticate and generate token.json
"""

import os
import sys
import json
import time
import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Required packages not installed. Run:")
    print("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
CONFIG_PATH = PROJECT_ROOT / "config"
CREDENTIALS_FILE = CONFIG_PATH / "credentials.json"
TOKEN_FILE = CONFIG_PATH / "token.json"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"

# Polling configuration
POLL_INTERVAL = int(os.getenv("GMAIL_POLL_INTERVAL", "60"))  # seconds
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# Priority keywords
PRIORITY_KEYWORDS = {
    "urgent": ["urgent", "asap", "emergency", "deadline today", "immediate"],
    "high": ["important", "invoice", "payment", "meeting", "client", "deadline"],
    "medium": ["question", "request", "update", "information", "follow-up"],
    "low": ["newsletter", "notification", "subscription", "digest", "weekly"]
}

# Setup logging (initially just console, file handler added in main())
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GmailWatcher")


def ensure_directories():
    """Ensure all required directories exist."""
    for path in [NEEDS_ACTION_PATH, LOGS_PATH, CONFIG_PATH]:
        path.mkdir(parents=True, exist_ok=True)


def get_gmail_service():
    """Authenticate and return Gmail API service."""
    creds = None

    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                logger.error(f"credentials.json not found at {CREDENTIALS_FILE}")
                logger.error("Download it from Google Cloud Console and place it in config/")
                sys.exit(1)

            logger.info("Starting OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        logger.info(f"Credentials saved to {TOKEN_FILE}")

    return build('gmail', 'v1', credentials=creds)


def determine_priority(subject: str, snippet: str) -> str:
    """Determine email priority based on keywords."""
    text = f"{subject} {snippet}".lower()

    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return priority

    return "medium"


def get_priority_emoji(priority: str) -> str:
    """Get emoji for priority level."""
    return {
        "urgent": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }.get(priority, "🟡")


def extract_email_body(payload: Dict[str, Any]) -> str:
    """Extract email body from payload."""
    body = ""

    if 'body' in payload and payload['body'].get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    elif 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if part['body'].get('data'):
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
            elif part['mimeType'] == 'multipart/alternative':
                body = extract_email_body(part)
                if body:
                    break

    # Truncate if too long
    if len(body) > 2000:
        body = body[:2000] + "\n\n... [truncated]"

    return body


def create_task_file(email_data: Dict[str, Any]) -> Optional[Path]:
    """Create a markdown task file for the email."""
    try:
        msg_id = email_data['id']
        headers = {h['name']: h['value'] for h in email_data['payload']['headers']}

        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown')
        date = headers.get('Date', datetime.now().isoformat())
        snippet = email_data.get('snippet', '')

        # Determine priority
        priority = determine_priority(subject, snippet)
        priority_emoji = get_priority_emoji(priority)

        # Extract body
        body = extract_email_body(email_data['payload'])

        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        safe_subject = "".join(c if c.isalnum() or c in " -_" else "" for c in subject)[:50]
        filename = f"{timestamp}_gmail_{priority}_{safe_subject}.md"
        filepath = NEEDS_ACTION_PATH / filename

        # Create markdown content
        content = f"""# {priority_emoji} Email: {subject}

## Metadata
- **Source:** Gmail
- **From:** {sender}
- **Date:** {date}
- **Priority:** {priority.upper()}
- **Message ID:** {msg_id}
- **Created:** {datetime.now().isoformat()}

---

## Summary
{snippet}

---

## Full Content
{body}

---

## Suggested Actions
- [ ] Read and understand the email
- [ ] Determine if response is needed
- [ ] Draft response (if applicable)
- [ ] Archive or follow up

---

## Decision Required
- [ ] **No action needed** - Archive this email
- [ ] **Reply needed** - Draft response for approval
- [ ] **Forward to human** - Requires human attention
- [ ] **Schedule follow-up** - Set reminder for later

---

## Notes
_Add any notes or context here_

"""

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would create: {filepath}")
            return None

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created task file: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Error creating task file: {e}")
        return None


def get_processed_ids() -> set:
    """Get set of already processed message IDs."""
    processed_file = CONFIG_PATH / "processed_emails.json"
    if processed_file.exists():
        with open(processed_file, 'r') as f:
            return set(json.load(f))
    return set()


def save_processed_ids(ids: set):
    """Save processed message IDs."""
    processed_file = CONFIG_PATH / "processed_emails.json"
    with open(processed_file, 'w') as f:
        json.dump(list(ids), f)


def fetch_new_emails(service) -> List[Dict[str, Any]]:
    """Fetch new unread important emails."""
    try:
        # Query for unread, important emails in inbox
        results = service.users().messages().list(
            userId='me',
            q='is:unread is:important in:inbox',
            maxResults=10
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            logger.debug("No new messages found")
            return []

        # Get processed IDs
        processed_ids = get_processed_ids()

        # Fetch full message details for new messages
        new_emails = []
        for msg in messages:
            if msg['id'] not in processed_ids:
                full_msg = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                new_emails.append(full_msg)

        return new_emails

    except HttpError as error:
        logger.error(f"Gmail API error: {error}")
        return []


def log_action(action: str, details: Dict[str, Any]):
    """Log action to daily log file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "actor": "gmail_watcher",
        **details
    }

    log_file = LOGS_PATH / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    # Load existing logs
    logs = []
    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(log_entry)

    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)


def main():
    """Main watcher loop."""
    logger.info("=" * 50)
    logger.info("Gmail Watcher Starting...")
    logger.info(f"Vault Path: {VAULT_PATH}")
    logger.info(f"Poll Interval: {POLL_INTERVAL} seconds")
    logger.info(f"Dry Run: {DRY_RUN}")
    logger.info("=" * 50)

    ensure_directories()

    # Add file handler after directories are created
    try:
        log_file = LOGS_PATH / f"gmail_watcher_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")
    except Exception as e:
        logger.warning(f"Could not create log file: {e}")

    try:
        service = get_gmail_service()
        logger.info("Successfully authenticated with Gmail API")
    except Exception as e:
        logger.error(f"Failed to authenticate: {e}")
        sys.exit(1)

    processed_ids = get_processed_ids()

    while True:
        try:
            logger.debug("Checking for new emails...")
            new_emails = fetch_new_emails(service)

            for email in new_emails:
                msg_id = email['id']
                headers = {h['name']: h['value'] for h in email['payload']['headers']}
                subject = headers.get('Subject', 'No Subject')

                logger.info(f"Processing: {subject}")

                filepath = create_task_file(email)

                if filepath:
                    processed_ids.add(msg_id)
                    log_action("email_processed", {
                        "message_id": msg_id,
                        "subject": subject,
                        "task_file": str(filepath),
                        "result": "success"
                    })

            # Save processed IDs
            save_processed_ids(processed_ids)

            # Clean up old IDs (keep last 1000)
            if len(processed_ids) > 1000:
                processed_ids = set(list(processed_ids)[-1000:])
                save_processed_ids(processed_ids)

        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            log_action("error", {
                "error": str(e),
                "result": "failure"
            })

        logger.debug(f"Sleeping for {POLL_INTERVAL} seconds...")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
