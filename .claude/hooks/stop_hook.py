#!/usr/bin/env python3
"""
Ralph Wiggum Stop Hook for Claude Code

This hook intercepts Claude Code's exit and checks if tasks are completed.
If tasks remain in Needs_Action, it re-injects the prompt to continue work.

Usage:
    Configure in .claude/settings.local.json:
    {
        "hooks": {
            "Stop": ["python", ".claude/hooks/stop_hook.py"]
        }
    }
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
STATE_FILE = PROJECT_ROOT / "config" / "hook_state.json"
MAX_REINJECTIONS = 5


def get_pending_tasks() -> list:
    """Get list of pending tasks."""
    if not NEEDS_ACTION_PATH.exists():
        return []
    return list(NEEDS_ACTION_PATH.glob("*.md"))


def load_state() -> dict:
    """Load hook state from file."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"reinjection_count": 0, "last_run": None}


def save_state(state: dict):
    """Save hook state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def main():
    """Main hook logic."""
    # Read hook input from stdin (Claude Code sends context)
    input_data = sys.stdin.read() if not sys.stdin.isatty() else ""

    state = load_state()
    pending_tasks = get_pending_tasks()

    # Check if we should allow exit
    if not pending_tasks:
        # No pending tasks, allow exit
        state["reinjection_count"] = 0
        save_state(state)
        print("All tasks completed. Exiting normally.")
        sys.exit(0)

    # Check reinjection limit
    if state["reinjection_count"] >= MAX_REINJECTIONS:
        print(f"Maximum reinjections ({MAX_REINJECTIONS}) reached.")
        print(f"Remaining tasks: {len(pending_tasks)}")
        state["reinjection_count"] = 0
        save_state(state)
        sys.exit(0)

    # Tasks remain - signal to continue
    state["reinjection_count"] += 1
    state["last_run"] = datetime.now().isoformat()
    save_state(state)

    print(f"Tasks remaining: {len(pending_tasks)}")
    print(f"Reinjection {state['reinjection_count']}/{MAX_REINJECTIONS}")
    print("Continue processing tasks...")

    # Return non-zero to signal Claude Code to continue
    # (This depends on how Claude Code hooks are configured)
    sys.exit(1)


if __name__ == "__main__":
    main()
