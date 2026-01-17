import os
import sys
import json
import time
import subprocess
import argparse
import logging
import shutil
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"
CONFIG_PATH = PROJECT_ROOT / "config"
LINKEDIN_QUEUE_PATH = VAULT_PATH / "LinkedIn_Queue"

# Default settings
DEFAULT_MAX_ITERATIONS = 5
DEFAULT_POLL_INTERVAL = 10

# Multi-agent fallback configuration
AI_AGENTS = [
    {
        "name": "gemini",
        "commands": [
            "gemini",
            "gemini.cmd",
            os.path.expandvars(r"%APPDATA%\\npm\\gemini.cmd"),
        ],
        "prompt_flag": "",
        "enabled": True
    },
    {
        "name": "claude",
        "commands": [
            "claude",
            "claude.cmd",
            os.path.expandvars(r"%APPDATA%\\npm\\claude.cmd"),
        ],
        "prompt_flag": "-p",
        "enabled": True
    },
    {
        "name": "qwen",
        "commands": [
            "qwen",
            "qwen.cmd",
            os.path.expandvars(r"%APPDATA%\\npm\\qwen.cmd"),
        ],
        "prompt_flag": "-p",
        "enabled": True
    },
    {
        "name": "copilot",
        "commands": [
            "github-copilot-cli",
            "copilot",
            "copilot.cmd",
        ],
        "prompt_flag": "-p",
        "enabled": True
    }
]

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Orchestrator")


class DigitalFTEOrchestrator:
    """Main orchestrator for the Digital FTE system."""

    def __init__(
        self,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        dry_run: bool = False
    ):
        self.max_iterations = max_iterations
        self.poll_interval = poll_interval
        self.dry_run = dry_run
        self.iteration_count = 0
        self.processed_tasks = set()
        
        # Verify agents
        self.available_agents = self._find_available_agents()

        # Ensure directories exist
        self._ensure_directories()

        # Load Company Handbook
        self.handbook = self._load_handbook()

        logger.info("=" * 60)
        logger.info("Digital FTE Orchestrator Initialized (Supervisor Mode)")
        logger.info(f"  Vault Path: {VAULT_PATH}")
        logger.info(f"  Poll Interval: {poll_interval}s")
        logger.info(f"  Dry Run: {dry_run}")
        
        if self.available_agents:
            names = [a['name'] for a in self.available_agents]
            logger.info(f"  Active Agents: {', '.join(names)}")
        else:
            logger.critical("  NO AGENTS FOUND! System cannot function.")

        logger.info("=" * 60)

    def _find_available_agents(self):
        """Find all available AI agents on the system."""
        import shutil
        available = []

        for agent in AI_AGENTS:
            if not agent["enabled"]:
                continue

            for cmd in agent["commands"]:
                cmd_path = shutil.which(cmd)
                if cmd_path:
                    available.append({
                        "name": agent["name"],
                        "command": cmd_path,
                        "prompt_flag": agent["prompt_flag"]
                    })
                    break
                elif os.path.exists(cmd):
                    available.append({
                        "name": agent["name"],
                        "command": cmd,
                        "prompt_flag": agent["prompt_flag"]
                    })
                    break
        return available

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for path in [NEEDS_ACTION_PATH, PENDING_APPROVAL_PATH,
                     APPROVED_PATH, DONE_PATH, LOGS_PATH, LINKEDIN_QUEUE_PATH]:
            path.mkdir(parents=True, exist_ok=True)

    def _load_handbook(self) -> str:
        """Load the Company Handbook for context."""
        handbook_path = VAULT_PATH / "Company_Handbook.md"
        if handbook_path.exists():
            return handbook_path.read_text(encoding='utf-8')
        return ""

    def get_pending_tasks(self) -> List[Path]:
        """Get list of tasks in Needs_Action folder."""
        tasks = []
        if NEEDS_ACTION_PATH.exists():
            tasks = list(NEEDS_ACTION_PATH.glob("*.md"))
        return sorted(tasks, key=lambda x: x.stat().st_mtime)

    def get_approved_tasks(self) -> List[Path]:
        """Get list of approved tasks ready for execution."""
        tasks = []
        if APPROVED_PATH.exists():
            tasks = list(APPROVED_PATH.glob("*.md"))
        return sorted(tasks, key=lambda x: x.stat().st_mtime)

    def build_supervisor_prompt(self, task_path: Path) -> str:
        """Build the structured prompt for the Agent."""
        task_content = task_path.read_text(encoding='utf-8')

        prompt = f"""You are a JSON generator. You do not speak. You do not greet. You only output valid JSON.

Input Task: {task_path.name}
Content: {task_content[:1000]}...

Handbook Rules:
{self.handbook[:500]}...

Task: Analyze if this needs human approval.
Output format:
{{
  "decision": "APPROVE" or "NEEDS_APPROVAL",
  "target_folder": "Done" or "Pending_Approval", 
  "analysis": "reasoning"
}}
JSON ONLY.
"""
        return prompt

    def invoke_agent(self, prompt: str, task_path: Path) -> tuple[bool, Dict, str]:
        """
        Invoke an AI agent and parse its JSON response.
        Returns: (success, json_data, agent_name)
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would invoke AI agent for: {task_path.name}")
            return True, {"target_folder": "Done", "analysis": "Dry run"}, "dry_run"

        if not self.available_agents:
            logger.error("No agents available.")
            return False, {}, "none"

        for ai_agent in self.available_agents:
            agent_name = ai_agent["name"]
            command = ai_agent["command"]
            prompt_flag = ai_agent["prompt_flag"]

            try:
                logger.info(f"Invoking {agent_name.upper()}...")
                
                cmd = [command, prompt]
                if prompt_flag:
                    cmd = [command, prompt_flag, prompt]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(PROJECT_ROOT),
                    shell=(os.name == 'nt'),
                    encoding='utf-8',
                    errors='replace'
                )

                if result.returncode == 0:
                    # Parse JSON output
                    output = result.stdout.strip()
                    # Clean markdown code blocks if present
                    output = re.sub(r'^```json\s*', '', output)
                    output = re.sub(r'^```\s*', '', output)
                    output = re.sub(r'\s*```$', '', output)
                    
                    try:
                        data = json.loads(output)
                        logger.info(f"{agent_name.upper()} returned valid JSON.")
                        return True, data, agent_name
                    except json.JSONDecodeError:
                        logger.warning(f"{agent_name.upper()} output invalid JSON: {output[:100]}...")
                        # Continue to next agent if JSON fails
                else:
                    logger.warning(f"{agent_name.upper()} failed (code {result.returncode}): {result.stderr[:200]}")

            except Exception as e:
                logger.warning(f"{agent_name.upper()} error: {e}")

        return False, {}, "all_failed"

    def process_task(self, task_path: Path) -> bool:
        """Process a task using Supervisor pattern."""
        task_id = task_path.name
        logger.info(f"Processing Task: {task_id}")

        prompt = self.build_supervisor_prompt(task_path)
        success, decision_data, agent = self.invoke_agent(prompt, task_path)

        if not success:
            logger.error(f"Failed to get decision for {task_id}")
            return False

        # Execute decision
        target_folder = decision_data.get("target_folder")
        analysis = decision_data.get("analysis", "No analysis provided")
        
        logger.info(f"Agent Decision: Move to {target_folder}")
        logger.info(f"Analysis: {analysis}")

        if target_folder == "Done":
            self._move_task(task_path, DONE_PATH)
            self._log_action("task_completed", {"task": task_id, "agent": agent, "analysis": analysis})
            return True
        elif target_folder == "Pending_Approval":
            self._move_task(task_path, PENDING_APPROVAL_PATH)
            self._log_action("task_needs_approval", {"task": task_id, "agent": agent, "analysis": analysis})
            return True
        else:
            logger.warning(f"Unknown target folder: {target_folder}")
            return False

    def _move_task(self, src: Path, dest_dir: Path):
        """Move task file to destination."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Move {src.name} -> {dest_dir}")
            return
            
        try:
            dest = dest_dir / src.name
            shutil.move(str(src), str(dest))
            logger.info(f"Moved {src.name} to {dest_dir.name}")
        except Exception as e:
            logger.error(f"Failed to move file: {e}")

    def process_approved_tasks(self):
        """Process tasks that have been approved."""
        approved_tasks = self.get_approved_tasks()
        for task_path in approved_tasks:
            logger.info(f"Executing Approved Task: {task_path.name}")
            # For now, approved tasks just go to Done, 
            # but this is where we'd hook in specific execution logic (like LinkedIn posting)
            
            if task_path.name.startswith("LinkedIn_"):
                self._process_linkedin(task_path)
            
            self._move_task(task_path, DONE_PATH)
            self._log_action("approved_task_executed", {"task": task_path.name})

    def _process_linkedin(self, task_path: Path):
        """Process approved LinkedIn post by calling linkedin_poster."""
        logger.info(f"Processing LinkedIn post: {task_path.name}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would post to LinkedIn: {task_path.name}")
            return True

        try:
            # Import here to avoid circular dependencies
            sys.path.insert(0, str(PROJECT_ROOT / "src"))
            from linkedin.linkedin_poster import LinkedInPoster

            # Read post content
            content = task_path.read_text(encoding='utf-8')

            # Extract actual post content from approval template
            # Look for content between "## Proposed LinkedIn Post" and "---"
            import re
            match = re.search(r'## Proposed LinkedIn Post\n\n(.*?)\n\n---', content, re.DOTALL)
            if match:
                post_content = match.group(1).strip()
            else:
                # Fallback: use entire content
                post_content = content

            # Post to LinkedIn using async
            import asyncio

            async def post():
                poster = LinkedInPoster()
                result = await poster.create_post(post_content)
                return result

            # Run async function
            result = asyncio.run(post())

            logger.info(f"LinkedIn post successful: {result}")
            self._log_action("linkedin_posted", {
                "task": task_path.name,
                "result": result
            })

            return True

        except Exception as e:
            logger.error(f"Failed to post to LinkedIn: {e}")
            self._log_action("linkedin_error", {
                "task": task_path.name,
                "error": str(e)
            })
            return False

    def process_linkedin_queue(self):
        """Process LinkedIn queue using scheduler."""
        try:
            # Import here to avoid circular dependencies
            sys.path.insert(0, str(PROJECT_ROOT / "src"))
            from linkedin.linkedin_scheduler import run_scheduler

            logger.info("Running LinkedIn scheduler...")
            run_scheduler(test_mode=self.dry_run)

        except Exception as e:
            logger.error(f"LinkedIn scheduler error: {e}")

    def _log_action(self, action: str, details: Dict[str, Any]):
        """Log action."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "actor": "orchestrator",
            **details
        }
        log_file = LOGS_PATH / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                logs = []
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    def run(self):
        """Main loop."""
        logger.info("Starting Supervisor Loop...")
        while True:
            try:
                # Process LinkedIn queue (scheduler)
                self.process_linkedin_queue()

                # Process pending tasks
                pending = self.get_pending_tasks()
                if pending:
                    logger.info(f"Found {len(pending)} pending tasks")
                    for task in pending:
                        self.process_task(task)

                # Process approved tasks (including LinkedIn posts)
                self.process_approved_tasks()

                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Loop error: {e}")
                time.sleep(10)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    orch = DigitalFTEOrchestrator(dry_run=args.dry_run)
    orch.run()

if __name__ == "__main__":
    main()