#!/usr/bin/env python3
"""
Task Completion Hook for Claude Code

This hook is triggered when Claude Code completes processing a task.
It handles file management and logging.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
LOGS_PATH = VAULT_PATH / "Logs"


def log_completion(task_name: str, result: str):
    """Log task completion."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": "task_completed",
        "task": task_name,
        "result": result
    }

    log_file = LOGS_PATH / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    LOGS_PATH.mkdir(parents=True, exist_ok=True)

    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text())
        except json.JSONDecodeError:
            logs = []

    logs.append(log_entry)
    log_file.write_text(json.dumps(logs, indent=2))


def main():
    """Process task completion."""
    # Read completion data from environment or stdin
    task_name = os.environ.get("TASK_NAME", "unknown")
    result = os.environ.get("TASK_RESULT", "completed")

    log_completion(task_name, result)
    print(f"Task '{task_name}' logged as {result}")


if __name__ == "__main__":
    main()
