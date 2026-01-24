"""
Vault Sync Utility - Digital FTE Platinum Tier

Handles synchronization of the Obsidian Vault between Cloud and Local
instances using Git. Ensures state is shared while keeping secrets local.
"""

import os
import subprocess
import logging
import time
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "300")) # 5 minutes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VaultSync")

class VaultSync:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def run_git(self, args: list):
        """Run a git command and return result."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Git error: {e.stderr}")
            return None

    def sync(self):
        """Perform full sync (Commit -> Pull -> Push)."""
        logger.info("Starting Vault sync...")
        
        # 1. Status check
        status = self.run_git(["status", "--porcelain", str(VAULT_PATH)])
        if status:
            logger.info("Changes detected in Vault, committing...")
            self.run_git(["add", str(VAULT_PATH)])
            self.run_git(["commit", "-m", f"agent sync: {time.strftime('%Y-%m-%d %H:%M:%S')}"])
        
        # 2. Rebase pull to keep history clean
        logger.info("Pulling latest changes...")
        self.run_git(["pull", "--rebase", "origin", "main"])
        
        # 3. Push
        logger.info("Pushing updates...")
        try:
            self.run_git(["push", "origin", "main"])
            logger.info("Sync complete!")
        except Exception:
            logger.error("Failed to push. May require manual conflict resolution.")

def main():
    sync_manager = VaultSync(PROJECT_ROOT)
    
    logger.info("=" * 50)
    logger.info("Vault Sync Utility Started")
    logger.info(f"Sync Interval: {SYNC_INTERVAL}s")
    logger.info("=" * 50)

    while True:
        try:
            sync_manager.sync()
        except Exception as e:
            logger.error(f"Sync loop error: {e}")
        
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()
