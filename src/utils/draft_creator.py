"""
Platinum Tier Draft Creator

Creates draft responses when Cloud agent cannot execute sensitive actions.
Drafts are saved to Vault/Drafts/ for human review and approval.

Features:
- AI-powered draft generation
- Structured draft format
- Audit logging
- Integration with orchestrator

Usage:
    from src.utils.draft_creator import create_draft, DraftCreator

    creator = DraftCreator(agent_id="cloud-oracle-001")
    draft_path = creator.create_draft(
        task_path=Path("Vault/Needs_Action/email_task.md"),
        action_type=ActionType.SEND_EMAIL,
        blocked_reason="Action blocked in CLOUD work-zone"
    )
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from src.utils.config import load_config, WorkZone
from src.utils.work_zone import ActionType
from src.utils.audit_logger import log_audit, AuditDomain, AuditStatus


# Configure logging
logger = logging.getLogger(__name__)


class DraftCreator:
    """Creates draft responses for blocked actions."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        vault_path: Optional[Path] = None,
    ):
        """
        Initialize draft creator.

        Args:
            agent_id: Agent identifier (defaults to config)
            vault_path: Path to vault (defaults to config)
        """
        config = load_config()

        self.agent_id = agent_id or config["agent_id"]
        self.vault_path = vault_path or config["vault_path"]
        self.drafts_path = self.vault_path / "Drafts"
        self.work_zone = config["work_zone"]

        # Ensure drafts folder exists
        self.drafts_path.mkdir(parents=True, exist_ok=True)

    def create_draft(
        self,
        task_path: Path,
        action_type: ActionType,
        blocked_reason: str,
        ai_response: Optional[str] = None,
    ) -> Path:
        """
        Create a draft response for a blocked action.

        Args:
            task_path: Path to original task file
            action_type: Type of action that was blocked
            blocked_reason: Reason the action was blocked
            ai_response: Optional AI-generated response

        Returns:
            Path to created draft file
        """
        logger.info(f"[{self.agent_id}] Creating draft for: {task_path.name}")

        # Read original task
        task_content = task_path.read_text(encoding='utf-8') if task_path.exists() else ""

        # Extract task metadata
        task_metadata = self._extract_task_metadata(task_path, task_content)

        # Generate draft filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        source = task_metadata.get("source", "unknown")
        priority = task_metadata.get("priority", "medium")
        slug = self._create_slug(task_path.stem)

        draft_filename = f"{timestamp}_{source}_{priority}_{slug}.md"
        draft_path = self.drafts_path / draft_filename

        # Build draft content
        draft_content = self._build_draft_content(
            task_path=task_path,
            task_content=task_content,
            task_metadata=task_metadata,
            action_type=action_type,
            blocked_reason=blocked_reason,
            ai_response=ai_response,
        )

        # Write draft file
        draft_path.write_text(draft_content, encoding='utf-8')

        # Log draft creation
        log_audit(
            action="draft.created",
            actor=self.agent_id,
            domain=AuditDomain.SYSTEM,
            resource=draft_filename,
            status=AuditStatus.SUCCESS,
            details={
                "original_task": task_path.name,
                "action_type": action_type.value,
                "work_zone": self.work_zone.value,
                "blocked_reason": blocked_reason,
            },
        )

        logger.info(f"[{self.agent_id}] Draft created: {draft_path.name}")
        return draft_path

    def _extract_task_metadata(
        self,
        task_path: Path,
        task_content: str,
    ) -> Dict[str, Any]:
        """Extract metadata from task file."""
        metadata = {
            "source": "unknown",
            "priority": "medium",
            "domain": "SYSTEM",
            "title": task_path.stem,
        }

        # Try to detect source from filename
        filename_lower = task_path.name.lower()
        if "gmail" in filename_lower or "email" in filename_lower:
            metadata["source"] = "gmail"
        elif "whatsapp" in filename_lower:
            metadata["source"] = "whatsapp"
        elif "linkedin" in filename_lower:
            metadata["source"] = "linkedin"
        elif "twitter" in filename_lower:
            metadata["source"] = "twitter"
        elif "facebook" in filename_lower or "meta" in filename_lower:
            metadata["source"] = "meta"

        # Try to detect priority
        if "urgent" in filename_lower or "high" in filename_lower:
            metadata["priority"] = "high"
        elif "low" in filename_lower:
            metadata["priority"] = "low"

        # Try to detect domain from content
        content_lower = task_content.lower()
        if "business" in content_lower or "invoice" in content_lower or "payment" in content_lower:
            metadata["domain"] = "BUSINESS"
        elif "personal" in content_lower:
            metadata["domain"] = "PERSONAL"

        return metadata

    def _create_slug(self, text: str, max_length: int = 30) -> str:
        """Create a URL-safe slug from text."""
        import re

        # Convert to lowercase and replace spaces/underscores with hyphens
        slug = text.lower()
        slug = re.sub(r'[_\s]+', '-', slug)

        # Remove non-alphanumeric characters (except hyphens)
        slug = re.sub(r'[^a-z0-9-]', '', slug)

        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)

        # Trim to max length
        slug = slug[:max_length].strip('-')

        return slug or "task"

    def _build_draft_content(
        self,
        task_path: Path,
        task_content: str,
        task_metadata: Dict[str, Any],
        action_type: ActionType,
        blocked_reason: str,
        ai_response: Optional[str] = None,
    ) -> str:
        """Build the draft file content."""
        now = datetime.now()
        draft_id = f"{now.strftime('%Y-%m-%d_%H%M')}_{task_metadata['source']}_{self._create_slug(task_path.stem)}"

        # Build YAML frontmatter
        frontmatter = f"""---
id: {draft_id}
source: {task_metadata['source']}
priority: {task_metadata['priority']}
domain: {task_metadata['domain']}
status: draft
action_type: {action_type.value}
work_zone: {self.work_zone.value}
created_at: {now.isoformat()}
claimed_by: {self.agent_id}
original_task: {task_path.name}
---
"""

        # Build body
        body = f"""# Draft: {task_metadata.get('title', task_path.stem)}

## Status

- **Status:** DRAFT (Awaiting Human Review)
- **Created By:** {self.agent_id} (Cloud Agent)
- **Created At:** {now.strftime('%Y-%m-%d %H:%M:%S')}
- **Action Type:** {action_type.value}

## Why This is a Draft

{blocked_reason}

> **Note:** The Cloud Agent cannot execute sensitive actions like sending emails,
> posting to social media, or processing financial transactions. This draft
> requires human review and approval on the Local Agent.

## Original Task

**File:** `{task_path.name}`

```markdown
{task_content[:2000]}
```

## Proposed Action

**Action Type:** `{action_type.value}`

"""

        # Add AI response if provided
        if ai_response:
            body += f"""### AI-Generated Response

{ai_response}

"""

        # Add approval section
        body += """## Required Approval

To approve and execute this draft:

1. [ ] Review the original task context
2. [ ] Review the proposed action/response
3. [ ] Verify all details are correct
4. [ ] Move this file to `Vault/Approved/` folder

### Quick Approval

```bash
# On Local machine
mv Vault/Drafts/{draft_file} Vault/Approved/
```

Or use Obsidian to drag the file to the Approved folder.

## Audit Trail

| Timestamp | Event | Agent |
|-----------|-------|-------|
| {timestamp} | Draft Created | {agent_id} |

---

*This draft was automatically generated by the Cloud Agent.*
*Human approval is required before execution.*
""".format(
            draft_file=f"{draft_id}.md",
            timestamp=now.strftime('%Y-%m-%d %H:%M:%S'),
            agent_id=self.agent_id,
        )

        return frontmatter + body


def create_draft(
    task_path: Path,
    action_type: ActionType,
    blocked_reason: str,
    agent_id: Optional[str] = None,
    ai_response: Optional[str] = None,
) -> Path:
    """
    Convenience function to create a draft.

    Args:
        task_path: Path to original task file
        action_type: Type of action that was blocked
        blocked_reason: Reason the action was blocked
        agent_id: Optional agent identifier
        ai_response: Optional AI-generated response

    Returns:
        Path to created draft file
    """
    creator = DraftCreator(agent_id=agent_id)
    return creator.create_draft(
        task_path=task_path,
        action_type=action_type,
        blocked_reason=blocked_reason,
        ai_response=ai_response,
    )


if __name__ == "__main__":
    # Test draft creator
    import tempfile

    print("Testing Draft Creator...")

    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)
        drafts = vault / "Drafts"
        needs_action = vault / "Needs_Action"
        drafts.mkdir()
        needs_action.mkdir()

        # Create test task
        task = needs_action / "gmail_high_Q4_report_request.md"
        task.write_text("""# Email: Q4 Report Request

From: john@company.com
Subject: Urgent - Q4 Report Needed

Hi,

Please send me the Q4 financial report by end of day.

Thanks,
John
""")

        # Test draft creation
        print("\n1. Testing draft creation...")
        os.environ["WORK_ZONE"] = "cloud"
        os.environ["AGENT_ID"] = "test-cloud-agent"
        os.environ["VAULT_PATH"] = str(vault)

        creator = DraftCreator(
            agent_id="test-cloud-agent",
            vault_path=vault,
        )

        draft_path = creator.create_draft(
            task_path=task,
            action_type=ActionType.SEND_EMAIL,
            blocked_reason="Action 'send_email' blocked in CLOUD work-zone",
            ai_response="Dear John,\n\nPlease find the Q4 report attached.\n\nBest regards",
        )

        print(f"   Draft created: {draft_path.name}")
        assert draft_path.exists()
        print("   [PASS]")

        # Verify draft content
        print("\n2. Verifying draft content...")
        content = draft_path.read_text()
        assert "status: draft" in content
        assert "SEND_EMAIL" in content.upper() or "send_email" in content
        assert "Awaiting Human Review" in content
        print("   [PASS]")

        # Test metadata extraction
        print("\n3. Testing metadata extraction...")
        metadata = creator._extract_task_metadata(task, task.read_text())
        print(f"   Source: {metadata['source']}")
        print(f"   Priority: {metadata['priority']}")
        assert metadata['source'] == 'gmail'
        assert metadata['priority'] == 'high'
        print("   [PASS]")

    print("\n[SUCCESS] All draft creator tests passed!")
