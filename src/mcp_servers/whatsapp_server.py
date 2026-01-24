"""
WhatsApp MCP Server - Secure Messaging Integration

Provides MCP tools for WhatsApp:
- Send messages (queues for Watcher)
- Check status

Architecture: This MCP does NOT drive the browser directly.
It creates task files in Vault/WhatsApp_Queue that the Watcher executes.
This prevents browser conflict and session locking issues.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

from fastmcp import FastMCP

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils.audit_logger import log_audit, AuditDomain, AuditStatus

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Configuration
VAULT_PATH = PROJECT_ROOT / "Vault"
QUEUE_PATH = VAULT_PATH / "WhatsApp_Queue"
PENDING_PATH = VAULT_PATH / "Pending_Approval"

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WhatsAppMCP")

# Ensure directories
QUEUE_PATH.mkdir(parents=True, exist_ok=True)
PENDING_PATH.mkdir(parents=True, exist_ok=True)

# Initialize MCP
mcp = FastMCP("WhatsApp")

@mcp.tool()
def send_whatsapp_message(to: str, message: str, requires_approval: bool = True) -> str:
    """
    Queue a WhatsApp message to be sent by the active Watcher.

    Args:
        to: Recipient name (must match contact name in phone exactly)
        message: Text content
        requires_approval: If True, requires human approval first (default: True)

    Returns:
        Status message
    """
    return _send_logic(to, message, requires_approval)

def _send_logic(to: str, message: str, requires_approval: bool = True) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_to = "".join(c if c.isalnum() else "_" for c in to)
    
    if requires_approval:
        filename = f"WHATSAPP_{timestamp}_to_{safe_to}.md"
        filepath = PENDING_PATH / filename
        
        content = f"""---
type: whatsapp_message
status: pending
created: {datetime.now().isoformat()}
to: {to}
---

# WhatsApp Approval

**To:** {to}

## Message
{message}

---
To approve, move to `Vault/WhatsApp_Queue/` renamed as `SEND_to_{to}_{timestamp}.md`
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        log_audit(
            action="whatsapp.queue_approval",
            actor="whatsapp_mcp",
            domain=AuditDomain.PERSONAL,
            resource=to,
            status=AuditStatus.PENDING,
            approval_required=True
        )
        return f"Message queued for approval: {filename}"

    else:
        # Direct send (for trusted agents/contacts)
        filename = f"SEND_to_{safe_to}_{timestamp}.md"
        filepath = QUEUE_PATH / filename
        
        content = f"""---
type: whatsapp_send
to: {to}
created: {datetime.now().isoformat()}
---

{message}
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        log_audit(
            action="whatsapp.queue_send",
            actor="whatsapp_mcp",
            domain=AuditDomain.PERSONAL,
            resource=to,
            status=AuditStatus.SUCCESS
        )
        return f"Message queued for sending: {filename}"

if __name__ == "__main__":
    mcp.run()
