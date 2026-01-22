"""
Platinum Tier Work-Zone Enforcement Framework

Implements work-zone restrictions to prevent Cloud agent from executing
sensitive actions. Only the Local agent (with human oversight) can
execute actions like sending emails, posting to social media, or
processing financial transactions.

Work-Zones:
- CLOUD: Draft-only mode (24/7 VM) - Cannot execute sensitive actions
- LOCAL: Full execution mode (user's machine) - Can execute all actions

Features:
- Action type classification
- Work-zone permission checking
- Audit logging for blocked executions
- Decorator for easy enforcement

Usage:
    from src.utils.work_zone import (
        can_execute_action,
        ActionType,
        WorkZone,
        require_local_work_zone,
    )

    # Check permission
    allowed, reason = can_execute_action(ActionType.SEND_EMAIL, WorkZone.CLOUD)
    if not allowed:
        print(f"Blocked: {reason}")

    # Use decorator
    @require_local_work_zone
    def send_email(to, subject, body):
        # Only executes in LOCAL work-zone
        pass
"""

import os
import logging
from enum import Enum
from typing import Tuple, Set, Optional, Callable
from functools import wraps

from src.utils.config import WorkZone, get_work_zone, load_config
from src.utils.audit_logger import log_audit, AuditDomain, AuditStatus


# Configure logging
logger = logging.getLogger(__name__)


class ActionType(Enum):
    """
    Action types for work-zone enforcement.

    Sensitive actions require LOCAL work-zone (human approval).
    Safe actions are allowed in both CLOUD and LOCAL.
    """

    # Sensitive actions (require LOCAL work-zone)
    SEND_EMAIL = "send_email"
    POST_SOCIAL_MEDIA = "post_social_media"
    POST_FACEBOOK = "post_facebook"
    POST_INSTAGRAM = "post_instagram"
    POST_TWITTER = "post_twitter"
    POST_LINKEDIN = "post_linkedin"
    CREATE_INVOICE = "create_invoice"
    RECORD_EXPENSE = "record_expense"
    SEND_WHATSAPP = "send_whatsapp"
    FINANCIAL_TRANSACTION = "financial_transaction"
    DELETE_FILE = "delete_file"
    EXECUTE_COMMAND = "execute_command"

    # Safe actions (allowed in CLOUD)
    READ_DATA = "read_data"
    SEARCH_EMAILS = "search_emails"
    LIST_CONTACTS = "list_contacts"
    READ_FILE = "read_file"
    CREATE_DRAFT = "create_draft"
    ANALYZE_DATA = "analyze_data"
    GENERATE_RESPONSE = "generate_response"
    UPDATE_DASHBOARD = "update_dashboard"
    LOG_AUDIT = "log_audit"
    GIT_SYNC = "git_sync"


# Sensitive actions that require Local work-zone
SENSITIVE_ACTIONS: Set[ActionType] = {
    ActionType.SEND_EMAIL,
    ActionType.POST_SOCIAL_MEDIA,
    ActionType.POST_FACEBOOK,
    ActionType.POST_INSTAGRAM,
    ActionType.POST_TWITTER,
    ActionType.POST_LINKEDIN,
    ActionType.CREATE_INVOICE,
    ActionType.RECORD_EXPENSE,
    ActionType.SEND_WHATSAPP,
    ActionType.FINANCIAL_TRANSACTION,
    ActionType.DELETE_FILE,
    ActionType.EXECUTE_COMMAND,
}

# Safe actions allowed in Cloud work-zone
SAFE_ACTIONS: Set[ActionType] = {
    ActionType.READ_DATA,
    ActionType.SEARCH_EMAILS,
    ActionType.LIST_CONTACTS,
    ActionType.READ_FILE,
    ActionType.CREATE_DRAFT,
    ActionType.ANALYZE_DATA,
    ActionType.GENERATE_RESPONSE,
    ActionType.UPDATE_DASHBOARD,
    ActionType.LOG_AUDIT,
    ActionType.GIT_SYNC,
}


class WorkZoneError(Exception):
    """Error raised when action is blocked by work-zone restrictions."""

    def __init__(self, action: ActionType, work_zone: WorkZone, message: str):
        self.action = action
        self.work_zone = work_zone
        self.message = message
        super().__init__(message)


def can_execute_action(
    action: ActionType,
    work_zone: Optional[WorkZone] = None,
) -> Tuple[bool, str]:
    """
    Check if action can be executed in current work-zone.

    Args:
        action: Action type to execute
        work_zone: Work-zone to check (defaults to current from env)

    Returns:
        (allowed: bool, reason: str)

    Example:
        allowed, reason = can_execute_action(ActionType.SEND_EMAIL, WorkZone.CLOUD)
        # Returns: (False, "Action 'send_email' requires LOCAL work-zone...")
    """
    if work_zone is None:
        work_zone = get_work_zone()

    # Check if action is sensitive
    if action in SENSITIVE_ACTIONS:
        if work_zone == WorkZone.CLOUD:
            reason = (
                f"Action '{action.value}' requires LOCAL work-zone "
                f"(human approval required). Current work-zone: {work_zone.value}. "
                f"Action will be converted to draft for human review."
            )
            return (False, reason)

    # Action is allowed
    reason = f"Action '{action.value}' permitted in {work_zone.value} work-zone"
    return (True, reason)


def is_sensitive_action(action: ActionType) -> bool:
    """Check if an action is considered sensitive."""
    return action in SENSITIVE_ACTIONS


def is_safe_action(action: ActionType) -> bool:
    """Check if an action is considered safe."""
    return action in SAFE_ACTIONS


def get_current_work_zone() -> WorkZone:
    """Get the current work-zone from environment."""
    return get_work_zone()


def log_execution_blocked(
    task_id: str,
    action: ActionType,
    work_zone: WorkZone,
    agent_id: str,
    details: Optional[dict] = None,
) -> None:
    """
    Log when execution is blocked by work-zone restrictions.

    Args:
        task_id: Task identifier
        action: Action that was blocked
        work_zone: Current work-zone
        agent_id: Agent that attempted the action
        details: Additional context
    """
    log_details = {
        "action": action.value,
        "work_zone": work_zone.value,
        "reason": "work_zone_restriction",
        "is_sensitive": is_sensitive_action(action),
    }

    if details:
        log_details.update(details)

    log_audit(
        action="execution.blocked",
        actor=agent_id,
        domain=AuditDomain.SYSTEM,
        resource=task_id,
        status=AuditStatus.FAILURE,
        details=log_details,
        error=f"Action '{action.value}' blocked in {work_zone.value} work-zone",
    )

    logger.warning(
        f"[{agent_id}] Execution blocked: {action.value} "
        f"not allowed in {work_zone.value} work-zone"
    )


def require_local_work_zone(func: Callable) -> Callable:
    """
    Decorator to enforce LOCAL work-zone requirement.

    Functions decorated with this will raise WorkZoneError if
    called in CLOUD work-zone.

    Usage:
        @require_local_work_zone
        def send_email(to, subject, body):
            # This will only execute in LOCAL work-zone
            pass

    Raises:
        WorkZoneError: If called in CLOUD work-zone
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        work_zone = get_work_zone()

        if work_zone == WorkZone.CLOUD:
            action_name = func.__name__
            raise WorkZoneError(
                action=ActionType.EXECUTE_COMMAND,
                work_zone=work_zone,
                message=(
                    f"Function '{action_name}' requires LOCAL work-zone. "
                    f"Current work-zone: {work_zone.value}"
                ),
            )

        return func(*args, **kwargs)

    return wrapper


def enforce_work_zone(
    action: ActionType,
    task_id: str,
    agent_id: str,
    work_zone: Optional[WorkZone] = None,
) -> Tuple[bool, str]:
    """
    Enforce work-zone restrictions and log blocked executions.

    This is the main entry point for work-zone enforcement.

    Args:
        action: Action to check
        task_id: Task identifier
        agent_id: Agent attempting the action
        work_zone: Work-zone to check (defaults to current)

    Returns:
        (allowed: bool, reason: str)

    Example:
        allowed, reason = enforce_work_zone(
            ActionType.SEND_EMAIL,
            "task-123",
            "cloud-oracle-001"
        )
        if not allowed:
            create_draft_instead(task, reason)
    """
    if work_zone is None:
        work_zone = get_work_zone()

    allowed, reason = can_execute_action(action, work_zone)

    if not allowed:
        log_execution_blocked(
            task_id=task_id,
            action=action,
            work_zone=work_zone,
            agent_id=agent_id,
        )

    return (allowed, reason)


def get_action_type_from_string(action_str: str) -> ActionType:
    """
    Convert action string to ActionType enum.

    Args:
        action_str: Action string (e.g., "send_email", "post_linkedin")

    Returns:
        ActionType enum value

    Example:
        action = get_action_type_from_string("send_email")
        # Returns: ActionType.SEND_EMAIL
    """
    # Normalize string
    action_lower = action_str.lower().strip()

    # Direct match
    try:
        return ActionType(action_lower)
    except ValueError:
        pass

    # Pattern matching for common variations
    if "email" in action_lower and "send" in action_lower:
        return ActionType.SEND_EMAIL
    elif "email" in action_lower and ("search" in action_lower or "read" in action_lower):
        return ActionType.SEARCH_EMAILS
    elif "facebook" in action_lower or "fb" in action_lower:
        return ActionType.POST_FACEBOOK
    elif "instagram" in action_lower or "ig" in action_lower:
        return ActionType.POST_INSTAGRAM
    elif "twitter" in action_lower or "tweet" in action_lower:
        return ActionType.POST_TWITTER
    elif "linkedin" in action_lower:
        return ActionType.POST_LINKEDIN
    elif "social" in action_lower and "post" in action_lower:
        return ActionType.POST_SOCIAL_MEDIA
    elif "invoice" in action_lower:
        return ActionType.CREATE_INVOICE
    elif "expense" in action_lower:
        return ActionType.RECORD_EXPENSE
    elif "whatsapp" in action_lower:
        return ActionType.SEND_WHATSAPP
    elif "payment" in action_lower or "financial" in action_lower or "transaction" in action_lower:
        return ActionType.FINANCIAL_TRANSACTION
    elif "delete" in action_lower:
        return ActionType.DELETE_FILE
    elif "draft" in action_lower:
        return ActionType.CREATE_DRAFT
    elif "read" in action_lower:
        return ActionType.READ_DATA

    # Default to safe action
    return ActionType.READ_DATA


def get_work_zone_summary(work_zone: Optional[WorkZone] = None) -> dict:
    """
    Get summary of what's allowed in the specified work-zone.

    Args:
        work_zone: Work-zone to summarize (defaults to current)

    Returns:
        Dictionary with allowed and blocked action lists
    """
    if work_zone is None:
        work_zone = get_work_zone()

    summary = {
        "work_zone": work_zone.value,
        "allowed_actions": [],
        "blocked_actions": [],
        "execution_mode": "draft_only" if work_zone == WorkZone.CLOUD else "full_execution",
    }

    for action in ActionType:
        allowed, _ = can_execute_action(action, work_zone)
        if allowed:
            summary["allowed_actions"].append(action.value)
        else:
            summary["blocked_actions"].append(action.value)

    return summary


if __name__ == "__main__":
    # Test work-zone enforcement
    print("Testing Work-Zone Enforcement Framework...")

    # Test 1: Cloud blocks sensitive actions
    print("\n1. Testing CLOUD work-zone blocks sensitive actions...")
    os.environ["WORK_ZONE"] = "cloud"

    for action in [ActionType.SEND_EMAIL, ActionType.POST_LINKEDIN, ActionType.CREATE_INVOICE]:
        allowed, reason = can_execute_action(action, WorkZone.CLOUD)
        print(f"   {action.value}: allowed={allowed}")
        assert not allowed, f"{action.value} should be blocked in CLOUD"

    print("   [PASS]")

    # Test 2: Cloud allows safe actions
    print("\n2. Testing CLOUD work-zone allows safe actions...")
    for action in [ActionType.READ_DATA, ActionType.CREATE_DRAFT, ActionType.GIT_SYNC]:
        allowed, reason = can_execute_action(action, WorkZone.CLOUD)
        print(f"   {action.value}: allowed={allowed}")
        assert allowed, f"{action.value} should be allowed in CLOUD"

    print("   [PASS]")

    # Test 3: Local allows all actions
    print("\n3. Testing LOCAL work-zone allows all actions...")
    os.environ["WORK_ZONE"] = "local"

    for action in [ActionType.SEND_EMAIL, ActionType.POST_LINKEDIN, ActionType.CREATE_INVOICE]:
        allowed, reason = can_execute_action(action, WorkZone.LOCAL)
        print(f"   {action.value}: allowed={allowed}")
        assert allowed, f"{action.value} should be allowed in LOCAL"

    print("   [PASS]")

    # Test 4: Action type detection
    print("\n4. Testing action type detection from strings...")
    test_cases = [
        ("send_email", ActionType.SEND_EMAIL),
        ("post to linkedin", ActionType.POST_LINKEDIN),
        ("create invoice", ActionType.CREATE_INVOICE),
        ("read email", ActionType.SEARCH_EMAILS),
    ]

    for string, expected in test_cases:
        result = get_action_type_from_string(string)
        print(f"   '{string}' → {result.value}")
        assert result == expected, f"Expected {expected}, got {result}"

    print("   [PASS]")

    # Test 5: Decorator
    print("\n5. Testing @require_local_work_zone decorator...")

    @require_local_work_zone
    def test_local_function():
        return "executed"

    os.environ["WORK_ZONE"] = "local"
    result = test_local_function()
    assert result == "executed"
    print("   LOCAL: executed successfully")

    os.environ["WORK_ZONE"] = "cloud"
    try:
        test_local_function()
        assert False, "Should have raised WorkZoneError"
    except WorkZoneError as e:
        print(f"   CLOUD: blocked as expected - {e.message[:50]}...")

    print("   [PASS]")

    # Test 6: Work-zone summary
    print("\n6. Testing work-zone summary...")
    summary = get_work_zone_summary(WorkZone.CLOUD)
    print(f"   CLOUD - Allowed: {len(summary['allowed_actions'])}, Blocked: {len(summary['blocked_actions'])}")
    assert len(summary['blocked_actions']) > 0
    print("   [PASS]")

    print("\n[SUCCESS] All work-zone enforcement tests passed!")
