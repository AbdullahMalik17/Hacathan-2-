"""
Filesystem Watcher - Digital FTE Sensory System

This script monitors a designated folder for new files and creates
markdown task files in the Obsidian vault for processing.

Setup:
1. Install watchdog: pip install watchdog
2. Configure WATCH_FOLDER environment variable or use default
3. Run the script
"""

import os
import sys
import json
import time
import logging
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent
except ImportError:
    print("Watchdog not installed. Run:")
    print("pip install watchdog")
    sys.exit(1)

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
CONFIG_PATH = PROJECT_ROOT / "config"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"

# Default watch folder - can be overridden by environment variable
DEFAULT_WATCH_FOLDER = PROJECT_ROOT / "DropFolder"
WATCH_FOLDER = Path(os.getenv("WATCH_FOLDER", str(DEFAULT_WATCH_FOLDER)))

# Configuration
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
DEBOUNCE_SECONDS = int(os.getenv("FILE_DEBOUNCE", "5"))  # Wait for file to finish copying

# File type configurations
FILE_TYPE_ACTIONS = {
    ".pdf": ["Review document", "Extract key information", "File appropriately"],
    ".docx": ["Review document", "Check for action items", "Respond if needed"],
    ".xlsx": ["Review spreadsheet", "Analyze data", "Summarize findings"],
    ".csv": ["Review data file", "Import if needed", "Process records"],
    ".png": ["Review image", "Identify content", "File appropriately"],
    ".jpg": ["Review image", "Identify content", "File appropriately"],
    ".jpeg": ["Review image", "Identify content", "File appropriately"],
    ".txt": ["Read content", "Extract action items", "Process accordingly"],
    ".msg": ["Review email", "Extract action items", "Respond if needed"],
    ".eml": ["Review email", "Extract action items", "Respond if needed"],
}

# Files to ignore
IGNORE_PATTERNS = [
    "~$",       # Office temp files
    ".tmp",     # Temp files
    ".part",    # Partial downloads
    ".crdownload",  # Chrome downloads
    "Thumbs.db",    # Windows thumbnails
    ".DS_Store",    # macOS metadata
    "desktop.ini",  # Windows folder config
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FilesystemWatcher")


def ensure_directories():
    """Ensure all required directories exist."""
    for path in [NEEDS_ACTION_PATH, LOGS_PATH, WATCH_FOLDER]:
        path.mkdir(parents=True, exist_ok=True)


def should_ignore_file(filepath: Path) -> bool:
    """Check if file should be ignored."""
    filename = filepath.name

    for pattern in IGNORE_PATTERNS:
        if pattern in filename or filename.startswith(pattern):
            return True

    # Ignore hidden files
    if filename.startswith("."):
        return True

    return False


def get_file_type_category(filepath: Path) -> str:
    """Categorize file by type."""
    ext = filepath.suffix.lower()

    categories = {
        "document": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt"],
        "spreadsheet": [".xlsx", ".xls", ".csv", ".ods"],
        "image": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"],
        "email": [".msg", ".eml"],
        "archive": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "presentation": [".pptx", ".ppt", ".odp"],
    }

    for category, extensions in categories.items():
        if ext in extensions:
            return category

    return "other"


def get_suggested_actions(filepath: Path) -> list:
    """Get suggested actions based on file type."""
    ext = filepath.suffix.lower()
    return FILE_TYPE_ACTIONS.get(ext, ["Review file", "Determine purpose", "Process accordingly"])


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def create_task_file(filepath: Path) -> Optional[Path]:
    """Create a markdown task file for the new file."""
    try:
        # Get file metadata
        stat = filepath.stat()
        file_size = format_file_size(stat.st_size)
        file_type = get_file_type_category(filepath)
        mime_type, _ = mimetypes.guess_type(str(filepath))
        created_time = datetime.fromtimestamp(stat.st_ctime)
        modified_time = datetime.fromtimestamp(stat.st_mtime)

        # Get suggested actions
        actions = get_suggested_actions(filepath)

        # Determine priority based on file type
        priority = "medium"
        if file_type in ["email", "document"]:
            priority = "high"
        elif file_type == "spreadsheet":
            priority = "high"

        priority_emoji = {"high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "🟡")

        # Generate task filename
        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        safe_name = "".join(c if c.isalnum() or c in " -_" else "" for c in filepath.stem)[:40]
        task_filename = f"{time_str}_file_{priority}_{safe_name}.md"
        task_filepath = NEEDS_ACTION_PATH / task_filename

        # Create markdown content
        content = f"""# {priority_emoji} New File: {filepath.name}

## Metadata
- **Source:** Filesystem Watcher
- **File Name:** {filepath.name}
- **File Path:** {filepath}
- **File Type:** {file_type.title()} ({filepath.suffix})
- **MIME Type:** {mime_type or "Unknown"}
- **File Size:** {file_size}
- **Created:** {created_time.isoformat()}
- **Modified:** {modified_time.isoformat()}
- **Priority:** {priority.upper()}
- **Task Created:** {datetime.now().isoformat()}

---

## File Location
```
{filepath}
```

---

## Suggested Actions
"""
        for i, action in enumerate(actions, 1):
            content += f"- [ ] {action}\n"

        content += f"""
---

## Decision Required
- [ ] **Process file** - Handle according to file type
- [ ] **Move to archive** - File for future reference
- [ ] **Forward to human** - Requires manual review
- [ ] **Delete** - File is not needed

---

## Notes
_Add any notes about this file here_

---

## Quick Actions
- Open file location: `explorer "{filepath.parent}"`
- Open file: `start "" "{filepath}"`

"""

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would create task for: {filepath.name}")
            return None

        with open(task_filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created task file: {task_filepath}")
        return task_filepath

    except Exception as e:
        logger.error(f"Error creating task file: {e}")
        return None


def log_action(action: str, details: Dict[str, Any]):
    """Log action to daily log file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "actor": "filesystem_watcher",
        **details
    }

    log_file = LOGS_PATH / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text())
        except json.JSONDecodeError:
            logs = []

    logs.append(log_entry)
    log_file.write_text(json.dumps(logs, indent=2))


class FileHandler(FileSystemEventHandler):
    """Handler for file system events."""

    def __init__(self):
        self.processed_files: Dict[str, float] = {}  # filepath -> timestamp
        super().__init__()

    def on_created(self, event):
        """Handle file creation events."""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Check if should ignore
        if should_ignore_file(filepath):
            logger.debug(f"Ignoring file: {filepath.name}")
            return

        # Debounce - wait for file to finish copying
        file_key = str(filepath)
        current_time = time.time()

        if file_key in self.processed_files:
            if current_time - self.processed_files[file_key] < DEBOUNCE_SECONDS:
                return

        # Wait a bit for file to finish writing
        time.sleep(DEBOUNCE_SECONDS)

        # Verify file still exists and is complete
        if not filepath.exists():
            logger.debug(f"File no longer exists: {filepath.name}")
            return

        try:
            # Try to open file to verify it's not locked
            with open(filepath, 'rb') as f:
                pass
        except (IOError, PermissionError):
            logger.debug(f"File still being written: {filepath.name}")
            return

        # Process the file
        logger.info(f"New file detected: {filepath.name}")
        self.processed_files[file_key] = current_time

        task_file = create_task_file(filepath)

        if task_file:
            log_action("file_detected", {
                "file_name": filepath.name,
                "file_type": get_file_type_category(filepath),
                "file_size": filepath.stat().st_size,
                "task_file": str(task_file),
                "result": "success"
            })

        # Clean up old entries (keep last 100)
        if len(self.processed_files) > 100:
            sorted_files = sorted(self.processed_files.items(), key=lambda x: x[1])
            self.processed_files = dict(sorted_files[-100:])


def main():
    """Main entry point."""
    logger.info("=" * 50)
    logger.info("Filesystem Watcher Starting...")
    logger.info(f"Watch Folder: {WATCH_FOLDER}")
    logger.info(f"Dry Run: {DRY_RUN}")
    logger.info(f"Debounce: {DEBOUNCE_SECONDS}s")
    logger.info("=" * 50)

    ensure_directories()

    # Create observer
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_FOLDER), recursive=False)

    # Start observer
    observer.start()
    logger.info(f"Watching folder: {WATCH_FOLDER}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Filesystem Watcher...")
        observer.stop()

    observer.join()
    logger.info("Filesystem Watcher stopped")


if __name__ == "__main__":
    main()
