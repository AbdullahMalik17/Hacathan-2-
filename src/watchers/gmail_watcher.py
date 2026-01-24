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
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',  # For labels
    'https://www.googleapis.com/auth/gmail.send'     # For auto-replies
]
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

# AI Exclusion Label
AI_EXCLUSION_LABEL = "NO_AI"  # Emails with this label will be skipped

# Importance classification (3-tier system)
IMPORTANCE_KEYWORDS = {
    "important": [
        # Security & Financial
        "urgent", "asap", "emergency", "security alert", "breach", "fraud",
        "payment due", "invoice due", "deadline today", "immediate action",
        # Business Critical
        "client emergency", "production down", "outage", "critical bug",
        "meeting today", "interview", "presentation",
        # Legal & Compliance
        "legal notice", "court", "lawsuit", "compliance", "audit"
    ],
    "medium": [
        "important", "invoice", "payment", "meeting", "client",
        "deadline", "question", "request", "update", "information",
        "follow-up", "review", "approval needed", "action required"
    ],
    "not_important": [
        "newsletter", "notification", "subscription", "digest", "weekly",
        "monthly report", "promotional", "unsubscribe", "marketing",
        "social media", "linkedin", "facebook", "twitter"
    ]
}

# Auto-reply configuration
AUTO_REPLY_ENABLED = os.getenv("AUTO_REPLY_ENABLED", "false").lower() == "true"
AUTO_REPLY_IMPORTANT_ONLY = True  # Only auto-reply to important emails

# Known sender domains (for importance scoring)
KNOWN_IMPORTANT_DOMAINS = {
    # Add your important domains here
    "client.com": "important",
    "bank.com": "important",
    "lawyer.com": "important",
    "malikmuhammadathar5@gmail.com" : "important",
    "[EMAIL_ADDRESS]" : "important",
    # Medium importance
    "vendor.com": "medium",
    "partner.com": "medium"
}

# Known senders file
KNOWN_SENDERS_FILE = CONFIG_PATH / "known_senders.json"

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


def load_known_senders() -> Dict[str, Dict[str, Any]]:
    """Load known sender reputation data."""
    if KNOWN_SENDERS_FILE.exists():
        with open(KNOWN_SENDERS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_known_senders(senders: Dict[str, Dict[str, Any]]):
    """Save known sender reputation data."""
    with open(KNOWN_SENDERS_FILE, 'w') as f:
        json.dump(senders, f, indent=2)


def update_sender_reputation(sender_email: str, importance: str):
    """Update sender reputation based on classification."""
    senders = load_known_senders()

    if sender_email not in senders:
        senders[sender_email] = {
            "first_seen": datetime.now().isoformat(),
            "email_count": 0,
            "importance_history": []
        }

    senders[sender_email]["email_count"] += 1
    senders[sender_email]["last_seen"] = datetime.now().isoformat()
    senders[sender_email]["importance_history"].append(importance)

    # Keep only last 10 classifications
    if len(senders[sender_email]["importance_history"]) > 10:
        senders[sender_email]["importance_history"] = senders[sender_email]["importance_history"][-10:]

    save_known_senders(senders)


def get_sender_domain(sender: str) -> str:
    """Extract domain from sender email."""
    if '<' in sender and '>' in sender:
        sender = sender[sender.find('<')+1:sender.find('>')]
    if '@' in sender:
        return sender.split('@')[1].lower()
    return ""


def determine_importance(subject: str, snippet: str, sender: str) -> str:
    """
    Determine email importance using 3-tier system:
    - important: Requires immediate attention and auto-reply
    - medium: Review within 24 hours
    - not_important: Can be archived or reviewed later
    """
    text = f"{subject} {snippet}".lower()

    # Check sender domain reputation
    domain = get_sender_domain(sender)
    if domain in KNOWN_IMPORTANT_DOMAINS:
        domain_importance = KNOWN_IMPORTANT_DOMAINS[domain]
        logger.debug(f"Domain {domain} marked as {domain_importance}")
        if domain_importance == "important":
            return "important"

    # Check known sender history
    sender_email = sender
    if '<' in sender and '>' in sender:
        sender_email = sender[sender.find('<')+1:sender.find('>')]

    known_senders = load_known_senders()
    if sender_email in known_senders:
        history = known_senders[sender_email].get("importance_history", [])
        if history:
            # If sender was important 3+ times out of last 10, consider important
            important_count = history.count("important")
            if important_count >= 3:
                logger.debug(f"Sender {sender_email} has {important_count}/10 important emails")
                return "important"

    # Keyword-based classification (prioritized)
    for importance, keywords in IMPORTANCE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            logger.debug(f"Matched keyword for {importance}: {text[:100]}")
            return importance

    # Default to medium
    return "medium"


def determine_priority(subject: str, snippet: str) -> str:
    """
    DEPRECATED: Use determine_importance() instead.
    Kept for backward compatibility.
    """
    text = f"{subject} {snippet}".lower()

    # Map old priority to new importance
    if any(kw in text for kw in IMPORTANCE_KEYWORDS.get("important", [])):
        return "urgent"
    elif any(kw in text for kw in IMPORTANCE_KEYWORDS.get("medium", [])):
        return "medium"
    else:
        return "low"


def get_priority_emoji(priority: str) -> str:
    """Get emoji for priority level."""
    return {
        "urgent": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢",
        "important": "🔴",
        "not_important": "🟢"
    }.get(priority, "🟡")


def has_exclusion_label(email_data: Dict[str, Any]) -> bool:
    """Check if email has the NO_AI label."""
    label_ids = email_data.get('labelIds', [])

    # Check if NO_AI label exists (case-insensitive match)
    for label_id in label_ids:
        if AI_EXCLUSION_LABEL.lower() in label_id.lower():
            return True

    return False


def generate_auto_reply(subject: str, sender: str, importance: str) -> str:
    """Generate automatic reply based on Company Handbook rules."""

    # Extract sender name
    sender_name = "there"
    if '<' in sender:
        sender_name = sender[:sender.find('<')].strip()

    reply_templates = {
        "important": f"""Hi {sender_name},

Thank you for your message regarding "{subject}".

I've received your email and marked it as high priority. I'm reviewing it now and will respond with a detailed reply within the next hour.

If this is extremely urgent, please feel free to call me directly.

Best regards,
Abdullah Junior
(Automated Response - Digital FTE)""",

        "medium": f"""Hi {sender_name},

Thank you for your email about "{subject}".

I've received your message and will review it shortly. You can expect a response within 24 hours.

If this requires immediate attention, please reply with "URGENT" in the subject line.

Best regards,
Abdullah Junior
(Automated Response - Digital FTE)"""
    }

    return reply_templates.get(importance, reply_templates["medium"])


def send_auto_reply(service, email_data: Dict[str, Any], importance: str) -> bool:
    """Send automatic reply to email."""
    try:
        headers = {h['name']: h['value'] for h in email_data['payload']['headers']}
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', '')
        message_id = headers.get('Message-ID', '')

        # Generate reply
        reply_body = generate_auto_reply(subject, sender, importance)

        # Create reply message
        from email.mime.text import MIMEText
        message = MIMEText(reply_body)
        message['to'] = sender
        message['subject'] = f"Re: {subject}"
        if message_id:
            message['In-Reply-To'] = message_id
            message['References'] = message_id

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send via Gmail API
        send_message = {'raw': raw_message}
        service.users().messages().send(userId='me', body=send_message).execute()

        logger.info(f"Auto-reply sent to: {sender}")
        return True

    except Exception as e:
        logger.error(f"Failed to send auto-reply: {e}")
        return False


def create_auto_reply_draft(service, email_data: Dict[str, Any], importance: str) -> Optional[str]:
    """Create draft reply for approval (safer than auto-send)."""
    try:
        headers = {h['name']: h['value'] for h in email_data['payload']['headers']}
        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', '')
        message_id = headers.get('Message-ID', '')

        # Generate reply
        reply_body = generate_auto_reply(subject, sender, importance)

        # Create draft message
        from email.mime.text import MIMEText
        message = MIMEText(reply_body)
        message['to'] = sender
        message['subject'] = f"Re: {subject}"
        if message_id:
            message['In-Reply-To'] = message_id
            message['References'] = message_id

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Create draft
        draft = {
            'message': {'raw': raw_message}
        }
        draft_obj = service.users().drafts().create(userId='me', body=draft).execute()

        logger.info(f"Draft created for: {sender} (ID: {draft_obj['id']})")
        return draft_obj['id']

    except Exception as e:
        logger.error(f"Failed to create draft: {e}")
        return None


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


def create_task_file(email_data: Dict[str, Any], importance: str = None) -> Optional[Path]:
    """Create a markdown task file for the email."""
    try:
        msg_id = email_data['id']
        headers = {h['name']: h['value'] for h in email_data['payload']['headers']}

        subject = headers.get('Subject', 'No Subject')
        sender = headers.get('From', 'Unknown')
        date = headers.get('Date', datetime.now().isoformat())
        snippet = email_data.get('snippet', '')

        # Determine importance (use provided or calculate)
        if importance is None:
            importance = determine_importance(subject, snippet, sender)

        importance_emoji = get_priority_emoji(importance)

        # Extract sender email for reputation tracking
        sender_email = sender
        if '<' in sender and '>' in sender:
            sender_email = sender[sender.find('<')+1:sender.find('>')]

        # Update sender reputation
        update_sender_reputation(sender_email, importance)

        # Extract body
        body = extract_email_body(email_data['payload'])

        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        safe_subject = "".join(c if c.isalnum() or c in " -_" else "" for c in subject)[:50]
        filename = f"{timestamp}_gmail_{importance}_{safe_subject}.md"
        filepath = NEEDS_ACTION_PATH / filename

        # Auto-reply suggestions
        auto_reply_section = ""
        if importance == "important":
            auto_reply_section = f"""
## 🤖 Auto-Reply Recommendation

**Status:** Ready to send automatic acknowledgment
**Template:** Important Email Response

> I've received your email and marked it as high priority.
> I'm reviewing it now and will respond within the next hour.

**Actions:**
- [ ] **Auto-send acknowledgment** (recommended for important emails)
- [ ] **Draft for approval** (creates draft in Gmail)
- [ ] **Skip auto-reply** (manual response only)

---
"""

        # Create markdown content
        content = f"""# {importance_emoji} Email: {subject}

## Metadata
- **Source:** Gmail
- **From:** {sender}
- **Date:** {date}
- **Importance:** {importance.upper()}
- **Message ID:** {msg_id}
- **Created:** {datetime.now().isoformat()}
- **Sender Reputation:** {get_sender_domain(sender)}

---

## Summary
{snippet}

---

## Full Content
{body}

---
{auto_reply_section}
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
    """Fetch new unread emails, excluding NO_AI labeled ones."""
    try:
        # Query for unread emails in inbox (removed is:important to catch all)
        # We'll determine importance ourselves
        results = service.users().messages().list(
            userId='me',
            q='is:unread in:inbox',
            maxResults=20  # Increased to catch more emails
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

                # Check for NO_AI label exclusion
                if has_exclusion_label(full_msg):
                    logger.info(f"Skipping email {msg['id']} - has {AI_EXCLUSION_LABEL} label")
                    processed_ids.add(msg['id'])  # Mark as processed to skip in future
                    continue

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
                sender = headers.get('From', 'Unknown')
                snippet = email.get('snippet', '')

                # Determine importance
                importance = determine_importance(subject, snippet, sender)

                logger.info(f"Processing [{importance.upper()}]: {subject} from {sender}")

                # Create task file
                filepath = create_task_file(email, importance)

                # Handle auto-reply for important emails
                draft_id = None
                if filepath and importance == "important":
                    if AUTO_REPLY_ENABLED:
                        # Create draft for approval (safer than auto-send)
                        draft_id = create_auto_reply_draft(service, email, importance)
                        if draft_id:
                            logger.info(f"✉️  Auto-reply draft created (ID: {draft_id})")
                    else:
                        logger.info(f"⏭️  Auto-reply disabled - skipping draft creation")

                if filepath:
                    processed_ids.add(msg_id)
                    log_action("email_processed", {
                        "message_id": msg_id,
                        "subject": subject,
                        "sender": sender,
                        "importance": importance,
                        "task_file": str(filepath),
                        "auto_reply_draft": draft_id,
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
