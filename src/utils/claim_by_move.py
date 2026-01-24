"""
Platinum Tier Claim-by-Move Implementation

Implements atomic task claiming using filesystem move operation to prevent
race conditions between Cloud and Local agents.

The claim-by-move pattern uses the atomicity of filesystem rename operations
to ensure that only one agent can successfully claim a task.

Features:
- Atomic task claiming using os.rename
- Race condition prevention
- Audit logging for all claims
- Batch claiming support
- Graceful error handling

Usage:
    from src.utils.claim_by_move import claim_task, claim_tasks_batch

    # Claim a single task
    success, message = claim_task(
        task_path=Path("Vault/Needs_Action/task1.md"),
        agent_id="cloud-oracle-001",
        destination_folder="Drafts"
    )

    # Claim multiple tasks
    results = claim_tasks_batch(
        task_paths=[Path("Vault/Needs_Action/task1.md"), ...],
        agent_id="cloud-oracle-001",
        destination_folder="Drafts"
    )
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, List, Optional

from src.utils.audit_logger import (
    log_audit,
    AuditDomain,
    AuditStatus,
)
from src.utils.config import load_config


# Configure logging
logger = logging.getLogger(__name__)


class ClaimResult:
    """Result of a claim operation."""
    SUCCESS = "success"
    ALREADY_CLAIMED = "already_claimed"
    ERROR = "error"


def get_vault_path() -> Path:
    """Get the vault path from configuration."""
    config = load_config()
    return config["vault_path"]


def claim_task(
    task_path: Path,
    agent_id: str,
    destination_folder: str,
    vault_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """
    Atomically claim a task by moving it to the destination folder.

    Uses os.rename which is atomic on most filesystems (POSIX and Windows).
    If the file has already been moved by another agent, FileNotFoundError
    is raised and the claim fails gracefully.

    Args:
        task_path: Path to task file (e.g., Vault/Needs_Action/task.md)
        agent_id: Agent identifier (e.g., "cloud-oracle-001")
        destination_folder: Destination folder name (e.g., "Drafts", "Approved")
        vault_path: Optional vault root path

    Returns:
        (success: bool, message: str)

    Example:
        success, msg = claim_task(
            Path("Vault/Needs_Action/task1.md"),
            "cloud-oracle-001",
            "Drafts"
        )
        # If success: msg = "Claimed task: task1.md → Drafts/"
        # If failed: msg = "Task already claimed: task1.md"
    """
    # Resolve paths
    if vault_path is None:
        vault_path = get_vault_path()

    # Ensure task_path is absolute
    if not task_path.is_absolute():
        task_path = vault_path / task_path

    # Compute destination path
    # Destination is relative to vault root
    if destination_folder.startswith("/") or ":" in destination_folder:
        # Absolute path provided
        dest_folder = Path(destination_folder)
    else:
        # Relative to vault
        dest_folder = vault_path / destination_folder

    # Ensure destination folder exists
    dest_folder.mkdir(parents=True, exist_ok=True)

    # Full destination path
    dest_path = dest_folder / task_path.name

    try:
        # Atomic rename (only succeeds if source exists)
        # This is atomic on POSIX (rename) and Windows (MoveFile)
        os.rename(task_path, dest_path)

        # Successfully claimed
        message = f"Claimed task: {task_path.name} → {destination_folder}/"

        # Log successful claim
        log_audit(
            action="task.claimed",
            actor=agent_id,
            domain=AuditDomain.SYSTEM,
            resource=task_path.stem,
            status=AuditStatus.SUCCESS,
            details={
                "source_folder": task_path.parent.name,
                "destination_folder": destination_folder,
                "source_path": str(task_path),
                "destination_path": str(dest_path),
            },
        )

        logger.info(f"[{agent_id}] {message}")
        return (True, message)

    except FileNotFoundError:
        # Another agent already moved the file
        message = f"Task already claimed: {task_path.name}"

        # Log failed claim (race condition)
        log_audit(
            action="task.claim_failed",
            actor=agent_id,
            domain=AuditDomain.SYSTEM,
            resource=task_path.stem,
            status=AuditStatus.FAILURE,
            details={
                "reason": "already_claimed",
                "source_folder": task_path.parent.name,
                "destination_folder": destination_folder,
            },
        )

        logger.warning(f"[{agent_id}] {message}")
        return (False, message)

    except PermissionError as e:
        # Permission denied
        message = f"Permission denied claiming task: {task_path.name} - {str(e)}"

        log_audit(
            action="task.claim_error",
            actor=agent_id,
            domain=AuditDomain.SYSTEM,
            resource=task_path.stem,
            status=AuditStatus.FAILURE,
            details={
                "error": "permission_denied",
                "message": str(e),
            },
        )

        logger.error(f"[{agent_id}] {message}")
        return (False, message)

    except Exception as e:
        # Unexpected error
        message = f"Error claiming task {task_path.name}: {str(e)}"

        log_audit(
            action="task.claim_error",
            actor=agent_id,
            domain=AuditDomain.SYSTEM,
            resource=task_path.stem,
            status=AuditStatus.FAILURE,
            details={
                "error": type(e).__name__,
                "message": str(e),
            },
        )

        logger.error(f"[{agent_id}] {message}")
        return (False, message)


def claim_tasks_batch(
    task_paths: List[Path],
    agent_id: str,
    destination_folder: str,
    vault_path: Optional[Path] = None,
) -> Dict[str, List[Path]]:
    """
    Claim multiple tasks atomically.

    Attempts to claim each task in the list. Returns a summary of results.

    Args:
        task_paths: List of paths to task files
        agent_id: Agent identifier
        destination_folder: Destination folder name
        vault_path: Optional vault root path

    Returns:
        {
            "claimed": list[Path],        # Successfully claimed
            "already_claimed": list[Path], # Claimed by another agent
            "failed": list[Path],          # Failed due to errors
        }

    Example:
        results = claim_tasks_batch(
            [Path("task1.md"), Path("task2.md"), Path("task3.md")],
            "cloud-oracle-001",
            "Drafts"
        )
        print(f"Claimed: {len(results['claimed'])}")
        print(f"Already claimed: {len(results['already_claimed'])}")
    """
    results = {
        "claimed": [],
        "already_claimed": [],
        "failed": [],
    }

    for task_path in task_paths:
        success, message = claim_task(
            task_path=task_path,
            agent_id=agent_id,
            destination_folder=destination_folder,
            vault_path=vault_path,
        )

        if success:
            results["claimed"].append(task_path)
        elif "already claimed" in message.lower():
            results["already_claimed"].append(task_path)
        else:
            results["failed"].append(task_path)

    # Log batch summary
    logger.info(
        f"[{agent_id}] Batch claim complete: "
        f"{len(results['claimed'])} claimed, "
        f"{len(results['already_claimed'])} already claimed, "
        f"{len(results['failed'])} failed"
    )

    return results


def unclaim_task(
    task_path: Path,
    agent_id: str,
    source_folder: str,
    destination_folder: str = "Needs_Action",
    vault_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """
    Unclaim a task by moving it back to the original folder.

    Useful for returning a task that cannot be processed.

    Args:
        task_path: Path to task file
        agent_id: Agent identifier
        source_folder: Current folder of the task
        destination_folder: Folder to return task to (default: Needs_Action)
        vault_path: Optional vault root path

    Returns:
        (success: bool, message: str)
    """
    if vault_path is None:
        vault_path = get_vault_path()

    # Build full source path
    if not task_path.is_absolute():
        full_source = vault_path / source_folder / task_path.name
    else:
        full_source = task_path

    try:
        success, message = claim_task(
            task_path=full_source,
            agent_id=agent_id,
            destination_folder=destination_folder,
            vault_path=vault_path,
        )

        if success:
            message = f"Unclaimed task: {task_path.name} → {destination_folder}/"

        return (success, message)

    except Exception as e:
        message = f"Error unclaiming task: {str(e)}"
        logger.error(f"[{agent_id}] {message}")
        return (False, message)


def get_claimable_tasks(
    folder: str = "Needs_Action",
    vault_path: Optional[Path] = None,
    pattern: str = "*.md",
) -> List[Path]:
    """
    Get list of tasks available for claiming in a folder.

    Args:
        folder: Folder to scan (default: Needs_Action)
        vault_path: Optional vault root path
        pattern: Glob pattern for task files (default: *.md)

    Returns:
        List of Path objects for claimable tasks
    """
    if vault_path is None:
        vault_path = get_vault_path()

    folder_path = vault_path / folder

    if not folder_path.exists():
        logger.warning(f"Folder does not exist: {folder_path}")
        return []

    # Get all matching files
    tasks = list(folder_path.glob(pattern))

    # Filter out special files
    tasks = [
        t for t in tasks
        if not t.name.startswith(".")  # Hidden files
        and not t.name.startswith("_")  # System files
        and t.name not in ["INBOX.md", "README.md", ".gitkeep"]
    ]

    # Sort by modification time (oldest first)
    tasks.sort(key=lambda p: p.stat().st_mtime)

    return tasks


def move_task(
    task_path: Path,
    destination_folder: str,
    agent_id: str,
    vault_path: Optional[Path] = None,
) -> Tuple[bool, str]:
    """
    Move a task to a new folder (wrapper around claim_task).

    This is a convenience function that works the same as claim_task
    but with a more intuitive name for moving tasks through the workflow.

    Args:
        task_path: Path to task file
        destination_folder: Destination folder name
        agent_id: Agent identifier
        vault_path: Optional vault root path

    Returns:
        (success: bool, message: str)
    """
    return claim_task(
        task_path=task_path,
        agent_id=agent_id,
        destination_folder=destination_folder,
        vault_path=vault_path,
    )


if __name__ == "__main__":
    # Test claim-by-move functionality
    import tempfile
    import threading
    import time

    print("Testing Claim-by-Move Implementation...")

    # Create temporary test directory
    with tempfile.TemporaryDirectory() as tmpdir:
        vault = Path(tmpdir)

        # Create test folders
        needs_action = vault / "Needs_Action"
        drafts = vault / "Drafts"
        needs_action.mkdir()
        drafts.mkdir()

        # Create test task
        test_task = needs_action / "test_task.md"
        test_task.write_text("# Test Task\n\nThis is a test.")

        print("\n1. Testing single claim...")
        success, msg = claim_task(test_task, "test-agent", "Drafts", vault)
        print(f"   Result: {msg}")
        assert success, "Claim should succeed"
        assert (drafts / "test_task.md").exists(), "Task should be in Drafts"
        assert not test_task.exists(), "Task should not be in Needs_Action"
        print("   [PASS]")

        # Test claiming already-claimed task
        print("\n2. Testing claim of already-claimed task...")
        success, msg = claim_task(test_task, "another-agent", "Drafts", vault)
        print(f"   Result: {msg}")
        assert not success, "Claim should fail"
        assert "already claimed" in msg.lower()
        print("   [PASS]")

        # Test race condition simulation
        print("\n3. Testing race condition...")

        # Create new task
        race_task = needs_action / "race_task.md"
        race_task.write_text("# Race Task")

        results = []

        def claim_worker(agent_id):
            time.sleep(0.001)  # Tiny delay to increase race chance
            success, msg = claim_task(race_task, agent_id, "Drafts", vault)
            results.append((agent_id, success))

        # Start two threads trying to claim same task
        t1 = threading.Thread(target=claim_worker, args=("agent-1",))
        t2 = threading.Thread(target=claim_worker, args=("agent-2",))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        # Exactly one should succeed
        successes = [r for r in results if r[1]]
        print(f"   Results: {results}")
        assert len(successes) == 1, f"Expected 1 success, got {len(successes)}"
        print(f"   Winner: {successes[0][0]}")
        print("   [PASS]")

        # Test batch claiming
        print("\n4. Testing batch claim...")

        # Create multiple tasks
        for i in range(5):
            task = needs_action / f"batch_task_{i}.md"
            task.write_text(f"# Batch Task {i}")

        tasks = list(needs_action.glob("batch_task_*.md"))
        batch_results = claim_tasks_batch(tasks, "batch-agent", "Drafts", vault)

        print(f"   Claimed: {len(batch_results['claimed'])}")
        print(f"   Already claimed: {len(batch_results['already_claimed'])}")
        print(f"   Failed: {len(batch_results['failed'])}")
        assert len(batch_results['claimed']) == 5
        print("   [PASS]")

        # Test get_claimable_tasks
        print("\n5. Testing get_claimable_tasks...")

        # Create some more tasks
        for i in range(3):
            task = needs_action / f"new_task_{i}.md"
            task.write_text(f"# New Task {i}")

        claimable = get_claimable_tasks("Needs_Action", vault)
        print(f"   Found {len(claimable)} claimable tasks")
        assert len(claimable) == 3
        print("   [PASS]")

    print("\n[SUCCESS] All claim-by-move tests passed!")
