import os
import sys
import base64
import json
import logging
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from fastmcp import FastMCP
from jinja2 import Environment, FileSystemLoader

# Import utilities
# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))
from src.utils.google_auth import get_gmail_service

# Configuration
VAULT_PATH = PROJECT_ROOT / "Vault"
PENDING_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
LOGS_PATH = VAULT_PATH / "Logs"
AUDIT_LOG = LOGS_PATH / "email_audit_log.md"
TEMPLATES_DIR = PROJECT_ROOT / "src" / "templates" / "email"
CONFIG_PATH = PROJECT_ROOT / "config"
CREDENTIALS_FILE = CONFIG_PATH / "credentials.json"
TOKEN_FILE = CONFIG_PATH / "token_email.json" # Separate token for sending
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Rate Limiting Config
MAX_HOURLY = 10
MAX_DAILY = 100

# Initialize Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EmailSenderMCP")

# Ensure directories
PENDING_PATH.mkdir(parents=True, exist_ok=True)
APPROVED_PATH.mkdir(parents=True, exist_ok=True)
LOGS_PATH.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

# Initialize MCP
mcp = FastMCP("Email Sender")

def log_audit(recipient: str, subject: str, outcome: str, message_id: str = None, error: str = None):
    """Log email attempts to audit log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"| {timestamp} | {recipient} | {subject} | {outcome} | {message_id or ''} | {error or ''} |\n"
    
    try:
        if not AUDIT_LOG.exists():
            with open(AUDIT_LOG, "w") as f:
                f.write("# Email Audit Log\n\n")
                f.write("| Timestamp | Recipient | Subject | Outcome | Message ID | Error |\n")
                f.write("|-----------|-----------|---------|---------|------------|-------|\n")
        
        with open(AUDIT_LOG, "a") as f:
            f.write(entry)
    except Exception as e:
        logger.error(f"Failed to write audit log: {e}")

def check_rate_limits() -> bool:
    """Check if we are within rate limits."""
    # Simplified implementation: count lines in audit log for today
    if not AUDIT_LOG.exists():
        return True
    
    today = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().strftime("%Y-%m-%d %H")
    
    daily_count = 0
    hourly_count = 0
    
    try:
        with open(AUDIT_LOG, "r") as f:
            for line in f:
                if line.startswith("|"):
                    parts = line.split("|")
                    if len(parts) > 2:
                        ts = parts[1].strip()
                        if ts.startswith(today):
                            daily_count += 1
                        if ts.startswith(current_hour):
                            hourly_count += 1
                            
        if daily_count >= MAX_DAILY:
            logger.warning(f"Daily rate limit exceeded ({daily_count}/{MAX_DAILY})")
            return False
        if hourly_count >= MAX_HOURLY:
            logger.warning(f"Hourly rate limit exceeded ({hourly_count}/{MAX_HOURLY})")
            return False
            
        return True
    except Exception:
        # If log read fails, fail safe (allow send? or block? Block is safer)
        return False

def _send_gmail(to: str, subject: str, body: str, cc: List[str] = None, bcc: List[str] = None) -> Dict:
    """Internal function to send email via Gmail API."""
    try:
        service = get_gmail_service(CREDENTIALS_FILE, TOKEN_FILE, SCOPES)
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        if cc:
            message['cc'] = ", ".join(cc)
        if bcc:
            message['bcc'] = ", ".join(bcc)
            
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {'raw': raw}
        
        message = service.users().messages().send(userId="me", body=body).execute()
        return message
    except Exception as e:
        logger.error(f"Gmail Send Error: {e}")
        raise e

@mcp.tool()
def send_email(to: str, subject: str, body: str, requires_approval: bool = False) -> str:
    """
    Send an email or queue it for approval.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        requires_approval: If True, saves to Pending_Approval instead of sending
    """
    if requires_approval:
        filename = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = PENDING_PATH / filename
        
        content = f"""---
type: email_approval
status: pending
created: {datetime.now().isoformat()}
to: {to}
subject: {subject}
---

# Email Approval Request

**To:** {to}
**Subject:** {subject}

## Body

{body}

---
To approve, move this file to `Vault/Approved/`.
"""
        with open(filepath, "w") as f:
            f.write(content)
            
        log_audit(to, subject, "PENDING_APPROVAL", details=f"Saved to {filename}")
        return f"Email queued for approval at {filepath}"

    # Check limits
    if not check_rate_limits():
        error = "Rate limit exceeded"
        log_audit(to, subject, "FAILED", error=error)
        return f"Error: {error}"

    try:
        result = _send_gmail(to, subject, body)
        msg_id = result.get('id')
        log_audit(to, subject, "SUCCESS", message_id=msg_id)
        return f"Email sent successfully. ID: {msg_id}"
    except Exception as e:
        log_audit(to, subject, "FAILED", error=str(e))
        return f"Error sending email: {str(e)}"

@mcp.tool()
def send_from_template(template_name: str, to: str, variables: Dict[str, str], requires_approval: bool = False) -> str:
    """
    Send an email using a Jinja2 template.
    
    Args:
        template_name: Name of the template file in src/templates/email (e.g., 'welcome.j2')
        to: Recipient email
        variables: Dictionary of variables to fill in the template
        requires_approval: Whether to queue for approval
    """
    try:
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        template = env.get_template(template_name)
        
        # Render body
        # Note: We assume the template renders the BODY. 
        # Subject usually needs to be handled. 
        # For this prototype, we'll assume the template might include frontmatter or we pass subject separate?
        # The spec says: send_from_template(template_id, to, variables).
        # Let's assume the template contains the subject in the first line or we pass it?
        # I'll update the signature to accept 'subject' or extract it.
        # Simple approach: The tool doesn't take subject, so maybe the template renders it?
        # Or I add subject argument. I'll add 'subject' to variables or argument.
        # But for compliance with Spec FR-002: send_from_template(template_id, to, variables)
        
        # I'll try to extract subject from variables or template block if possible.
        # Let's assume 'subject' is in variables.
        
        subject = variables.get('subject', 'No Subject')
        body = template.render(**variables)
        
        return send_email(to, subject, body, requires_approval)
        
    except Exception as e:
        return f"Template Error: {str(e)}"

if __name__ == "__main__":
    mcp.run()
