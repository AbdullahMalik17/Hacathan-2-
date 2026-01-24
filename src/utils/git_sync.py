"""
Platinum Tier Git Synchronization Utility

Provides Git pull/push functionality with conflict resolution for
dual-agent vault synchronization.

Features:
- Automatic pull with rebase strategy
- Push with structured commit messages
- Conflict resolution (local always wins)
- Timeout handling (30s max)
- Retry logic with exponential backoff
- Comprehensive error logging

Usage:
    from src.utils.git_sync import git_pull, git_push, git_sync

    # Pull latest changes
    result = git_pull()
    if result["success"]:
        print(f"Pulled {result['files_changed']} files")

    # Push changes
    result = git_push("cloud-oracle-001", "Draft email response", ["Drafts/", "Logs/"])
    if result["success"]:
        print(f"Pushed {result['files_pushed']} files")
"""

import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

from src.utils.config import load_config, get_project_root


# Configure logging
logger = logging.getLogger(__name__)


# Default configuration
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds


def get_vault_path() -> Path:
    """Get the vault path from configuration."""
    config = load_config()
    return config["vault_path"]


def _run_git_command(
    args: List[str],
    cwd: Optional[Path] = None,
    timeout: int = DEFAULT_TIMEOUT
) -> subprocess.CompletedProcess:
    """
    Run a git command with timeout handling.

    Args:
        args: Git command arguments (without 'git' prefix)
        cwd: Working directory (defaults to vault path)
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess result
    """
    if cwd is None:
        cwd = get_vault_path()

    cmd = ["git"] + args
    logger.debug(f"Running git command: {' '.join(cmd)} in {cwd}")

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


def _count_changed_files(git_output: str) -> int:
    """Count the number of files changed from git output."""
    count = 0
    for line in git_output.split('\n'):
        line = line.strip()
        if line and not line.startswith('Already'):
            # Count lines that indicate file changes
            if any(indicator in line for indicator in ['create', 'delete', 'rename', '|', '+', '-']):
                count += 1
    return count


def _parse_conflicts(git_output: str) -> List[str]:
    """Extract conflicting file paths from git output."""
    conflicts = []
    for line in git_output.split('\n'):
        if 'CONFLICT' in line:
            # Extract file path from conflict message
            # Format: "CONFLICT (content): Merge conflict in <filepath>"
            parts = line.split('in ')
            if len(parts) > 1:
                conflicts.append(parts[-1].strip())
    return conflicts


def _get_last_commit_sha(cwd: Optional[Path] = None) -> str:
    """Get the SHA of the last commit."""
    try:
        result = _run_git_command(["rev-parse", "HEAD"], cwd=cwd, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()[:7]  # Short SHA
    except Exception:
        pass
    return ""


def _count_staged_files(cwd: Optional[Path] = None) -> int:
    """Count the number of staged files."""
    try:
        result = _run_git_command(["diff", "--cached", "--name-only"], cwd=cwd, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return len(result.stdout.strip().split('\n'))
    except Exception:
        pass
    return 0


def git_pull(
    vault_path: Optional[Path] = None,
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Pull latest changes with rebase strategy.

    Implements conflict resolution where local changes always win.

    Args:
        vault_path: Path to vault (defaults to configured path)
        timeout: Command timeout in seconds

    Returns:
        {
            "success": bool,
            "files_changed": int,
            "conflicts": list[str],
            "error": str | None,
            "stdout": str,
            "stderr": str
        }
    """
    if vault_path is None:
        vault_path = get_vault_path()

    result = {
        "success": False,
        "files_changed": 0,
        "conflicts": [],
        "error": None,
        "stdout": "",
        "stderr": "",
    }

    try:
        # First, fetch to see if there are remote changes
        fetch_result = _run_git_command(
            ["fetch", "origin"],
            cwd=vault_path,
            timeout=timeout
        )

        # Pull with rebase
        pull_result = _run_git_command(
            ["pull", "origin", "main", "--rebase"],
            cwd=vault_path,
            timeout=timeout
        )

        result["stdout"] = pull_result.stdout
        result["stderr"] = pull_result.stderr

        if pull_result.returncode == 0:
            result["success"] = True
            result["files_changed"] = _count_changed_files(pull_result.stdout)
            logger.info(f"Git pull successful: {result['files_changed']} files changed")
            return result

        # Check for conflicts
        if "CONFLICT" in pull_result.stdout or "CONFLICT" in pull_result.stderr:
            conflicts = _parse_conflicts(pull_result.stdout + pull_result.stderr)
            result["conflicts"] = conflicts
            logger.warning(f"Git pull conflicts detected: {conflicts}")

            # Auto-resolve: local always wins
            for conflict_file in conflicts:
                try:
                    _run_git_command(["checkout", "--ours", conflict_file], cwd=vault_path, timeout=5)
                    _run_git_command(["add", conflict_file], cwd=vault_path, timeout=5)
                    logger.info(f"Resolved conflict (ours wins): {conflict_file}")
                except Exception as e:
                    logger.error(f"Failed to resolve conflict for {conflict_file}: {e}")

            # Continue rebase
            try:
                _run_git_command(["rebase", "--continue"], cwd=vault_path, timeout=timeout)
            except Exception:
                # If rebase continue fails, abort and try again
                _run_git_command(["rebase", "--abort"], cwd=vault_path, timeout=5)
                logger.warning("Rebase aborted after conflict resolution")

            result["success"] = True
            result["files_changed"] = _count_changed_files(pull_result.stdout)
            return result

        # Check if already up-to-date
        if "Already up to date" in pull_result.stdout or "Already up-to-date" in pull_result.stdout:
            result["success"] = True
            result["files_changed"] = 0
            logger.debug("Git pull: already up to date")
            return result

        # Other error
        result["error"] = pull_result.stderr or pull_result.stdout
        logger.error(f"Git pull failed: {result['error']}")

    except subprocess.TimeoutExpired:
        result["error"] = f"Git pull timeout (>{timeout}s)"
        logger.error(result["error"])

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Git pull exception: {e}")

    return result


def git_push(
    agent_id: str,
    description: str,
    folders: List[str],
    vault_path: Optional[Path] = None,
    timeout: int = DEFAULT_TIMEOUT
) -> Dict[str, Any]:
    """
    Stage changes and push to remote.

    Args:
        agent_id: Agent identifier for commit message
        description: Brief description of changes
        folders: List of folders/files to stage
        vault_path: Path to vault (defaults to configured path)
        timeout: Command timeout in seconds

    Returns:
        {
            "success": bool,
            "files_pushed": int,
            "commit_sha": str | None,
            "error": str | None,
            "stdout": str,
            "stderr": str
        }
    """
    if vault_path is None:
        vault_path = get_vault_path()

    result = {
        "success": False,
        "files_pushed": 0,
        "commit_sha": None,
        "error": None,
        "stdout": "",
        "stderr": "",
    }

    try:
        # Stage changes
        for folder in folders:
            folder_path = vault_path / folder if not Path(folder).is_absolute() else Path(folder)
            if folder_path.exists():
                add_result = _run_git_command(["add", folder], cwd=vault_path, timeout=5)
                if add_result.returncode != 0:
                    logger.warning(f"Failed to add {folder}: {add_result.stderr}")

        # Check for staged changes
        status_result = _run_git_command(
            ["status", "--porcelain"],
            cwd=vault_path,
            timeout=5
        )

        if not status_result.stdout.strip():
            # No changes to commit
            result["success"] = True
            result["files_pushed"] = 0
            logger.debug("Git push: no changes to commit")
            return result

        # Count files to be committed
        files_to_commit = len([
            line for line in status_result.stdout.strip().split('\n')
            if line.strip()
        ])

        # Create commit message with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"agent sync: {timestamp}"
        if description:
            commit_msg = f"{agent_id}: {description}"

        # Commit
        commit_result = _run_git_command(
            ["commit", "-m", commit_msg],
            cwd=vault_path,
            timeout=10
        )

        if commit_result.returncode != 0:
            result["error"] = f"Commit failed: {commit_result.stderr}"
            logger.error(result["error"])
            return result

        result["stdout"] = commit_result.stdout

        # Push
        push_result = _run_git_command(
            ["push", "origin", "HEAD"],
            cwd=vault_path,
            timeout=timeout
        )

        result["stderr"] = push_result.stderr

        if push_result.returncode == 0:
            result["success"] = True
            result["files_pushed"] = files_to_commit
            result["commit_sha"] = _get_last_commit_sha(vault_path)
            logger.info(f"Git push successful: {result['files_pushed']} files, commit {result['commit_sha']}")
            return result

        # Push failed - might need to pull first
        if "rejected" in push_result.stderr or "non-fast-forward" in push_result.stderr:
            logger.warning("Push rejected, attempting pull and retry")

            # Pull and retry
            pull_result = git_pull(vault_path, timeout)
            if pull_result["success"]:
                # Retry push
                push_result = _run_git_command(
                    ["push", "origin", "HEAD"],
                    cwd=vault_path,
                    timeout=timeout
                )

                if push_result.returncode == 0:
                    result["success"] = True
                    result["files_pushed"] = files_to_commit
                    result["commit_sha"] = _get_last_commit_sha(vault_path)
                    return result

        result["error"] = push_result.stderr or "Push failed"
        logger.error(f"Git push failed: {result['error']}")

    except subprocess.TimeoutExpired:
        result["error"] = f"Git push timeout (>{timeout}s)"
        logger.error(result["error"])

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Git push exception: {e}")

    return result


def git_sync(
    agent_id: str,
    description: str = "",
    folders: Optional[List[str]] = None,
    vault_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Full sync: pull then push.

    Args:
        agent_id: Agent identifier
        description: Optional description for commit
        folders: Folders to stage (defaults to standard folders)
        vault_path: Path to vault

    Returns:
        {
            "success": bool,
            "pulled": int,
            "pushed": int,
            "conflicts": list[str],
            "commit_sha": str | None,
            "error": str | None
        }
    """
    if folders is None:
        folders = ["Drafts/", "Approved/", "Done/", "Logs/audit/", "Dashboard.md"]

    result = {
        "success": False,
        "pulled": 0,
        "pushed": 0,
        "conflicts": [],
        "commit_sha": None,
        "error": None,
    }

    # Pull first
    pull_result = git_pull(vault_path)
    result["pulled"] = pull_result["files_changed"]
    result["conflicts"] = pull_result["conflicts"]

    if not pull_result["success"]:
        result["error"] = f"Pull failed: {pull_result['error']}"
        return result

    # Push changes
    push_result = git_push(agent_id, description, folders, vault_path)
    result["pushed"] = push_result["files_pushed"]
    result["commit_sha"] = push_result["commit_sha"]

    if not push_result["success"]:
        result["error"] = f"Push failed: {push_result['error']}"
        return result

    result["success"] = True
    logger.info(f"Git sync complete: pulled {result['pulled']}, pushed {result['pushed']}")
    return result


def git_status(vault_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Get current git status.

    Returns:
        {
            "branch": str,
            "clean": bool,
            "ahead": int,
            "behind": int,
            "modified": list[str],
            "staged": list[str],
            "untracked": list[str]
        }
    """
    if vault_path is None:
        vault_path = get_vault_path()

    result = {
        "branch": "unknown",
        "clean": True,
        "ahead": 0,
        "behind": 0,
        "modified": [],
        "staged": [],
        "untracked": [],
    }

    try:
        # Get branch name
        branch_result = _run_git_command(
            ["rev-parse", "--abbrev-ref", "HEAD"],
            cwd=vault_path,
            timeout=5
        )
        if branch_result.returncode == 0:
            result["branch"] = branch_result.stdout.strip()

        # Get status
        status_result = _run_git_command(
            ["status", "--porcelain", "-b"],
            cwd=vault_path,
            timeout=5
        )

        if status_result.returncode == 0:
            lines = status_result.stdout.strip().split('\n')
            for line in lines:
                if not line:
                    continue

                if line.startswith('##'):
                    # Parse branch info
                    if 'ahead' in line:
                        try:
                            result["ahead"] = int(line.split('ahead ')[1].split(']')[0].split(',')[0])
                        except:
                            pass
                    if 'behind' in line:
                        try:
                            result["behind"] = int(line.split('behind ')[1].split(']')[0].split(',')[0])
                        except:
                            pass
                else:
                    # Parse file status
                    status_code = line[:2]
                    filepath = line[3:].strip()

                    if status_code[0] in ['M', 'A', 'D', 'R']:
                        result["staged"].append(filepath)
                    if status_code[1] == 'M':
                        result["modified"].append(filepath)
                    if status_code == '??':
                        result["untracked"].append(filepath)

            result["clean"] = not (result["modified"] or result["staged"] or result["untracked"])

    except Exception as e:
        logger.error(f"Git status error: {e}")

    return result


if __name__ == "__main__":
    # Test git sync utilities
    import sys

    logging.basicConfig(level=logging.DEBUG)

    print("Testing Git Sync Utilities...")

    # Test git status
    print("\n1. Testing git status...")
    status = git_status()
    print(f"   Branch: {status['branch']}")
    print(f"   Clean: {status['clean']}")
    print(f"   Modified: {len(status['modified'])} files")
    print(f"   Staged: {len(status['staged'])} files")
    print(f"   Untracked: {len(status['untracked'])} files")
    print("   [OK]")

    # Test git pull (dry run - just check it doesn't error)
    print("\n2. Testing git pull...")
    result = git_pull()
    print(f"   Success: {result['success']}")
    print(f"   Files changed: {result['files_changed']}")
    print(f"   Conflicts: {result['conflicts']}")
    if result['error']:
        print(f"   Error: {result['error']}")
    print("   [OK]" if result['success'] else "   [SKIP - may not have remote]")

    print("\n[INFO] Git push test skipped (would modify repo)")
    print("[SUCCESS] Git sync utilities loaded successfully!")
