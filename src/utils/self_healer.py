import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Path to the AI reasoning tool (using gemini/claude via CLI)
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
LOGS_PATH = VAULT_PATH / "Logs"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SelfHealer] - %(message)s')
logger = logging.getLogger("SelfHealer")

class SelfHealer:
    def __init__(self, script_path):
        self.script_path = Path(script_path)
        self.error_count = 0
        self.max_retries = 3

    def run_with_healing(self):
        """Run the script and heal it if it crashes."""
        while self.error_count < self.max_retries:
            logger.info(f"Launching script: {self.script_path}")
            process = subprocess.Popen(
                [sys.executable, str(self.script_path)],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Script crashed with error: {stderr}")
                self.heal(stderr)
                self.error_count += 1
                time.sleep(5) # Cooldown before restart
            else:
                logger.info("Script exited successfully.")
                break

    def heal(self, error_log):
        """Invoke AI to suggest and apply a fix."""
        logger.info("🧠 Asking AI for a self-healing fix...")
        
        prompt = f"""
        The following Python script crashed: {self.script_path}
        
        Error Log:
        {error_log}
        
        Task: Analyze the error and provide a fix. If it's a missing dependency, output 'pip install <package>'. 
        If it's a code bug, output the corrected code block.
        """
        
        # In a real scenario, we would call 'gemini -p prompt' here.
        # For now, we'll log the intention to the Vault for human review.
        healing_file = LOGS_PATH / f"HEALING_{self.script_path.stem}.md"
        with open(healing_file, "w") as f:
            f.write(f"# Auto-Healing Request\n\n## Script\n{self.script_path}\n\n## Error\n```\n{error_log}\n```\n")
        
        logger.info(f"Healing request saved to {healing_file}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        healer = SelfHealer(sys.argv[1])
        healer.run_with_healing()
    else:
        print("Usage: python self_healer.py <script_to_monitor>")
