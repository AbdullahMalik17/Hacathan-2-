"""
Digital FTE Orchestrator - The Ralph Wiggum Loop

This orchestrator continuously monitors the vault for tasks and
uses Claude Code to process them. The "Ralph Wiggum" pattern
prevents lazy agent behavior by re-injecting the prompt if
tasks aren't completed.

Usage:
    python orchestrator.py                    # Normal mode
    python orchestrator.py --dry-run          # Test without executing
    python orchestrator.py --max-iterations 5 # Limit iterations
"""

import os
import sys
import json
import time
import subprocess
import argparse
import logging
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
DEFAULT_MAX_ITERATIONS = 10
DEFAULT_POLL_INTERVAL = 30  # seconds

# Multi-agent fallback configuration
# Order: Claude (default) -> Gemini -> Qwen -> Copilot -> OpenCode
AI_AGENTS = [
    {
        "name": "claude",
        "commands": [
            "claude",
            "claude.cmd",
            os.path.expandvars(r"%APPDATA%\npm\claude.cmd"),
        ],
        "prompt_flag": "-p",
        "enabled": True
    },
    {
        "name": "gemini",
        "commands": [
            "gemini",
            "gemini.cmd",
            os.path.expandvars(r"%APPDATA%\npm\gemini.cmd"),
        ],
        "prompt_flag": "-p",
        "enabled": True
    },
    {
        "name": "qwen",
        "commands": [
            "qwen",
            "qwen.cmd",
            os.path.expandvars(r"%APPDATA%\npm\qwen.cmd"),
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
        "prompt_flag": "",  # Copilot may use different syntax
        "enabled": True
    },
    {
        "name": "opencode",
        "commands": [
            "opencode",
            "opencode.cmd",
            "aider",  # Alternative open-source coding assistant
            "aider.cmd",
        ],
        "prompt_flag": "--message",
        "enabled": True
    }
]


def find_available_agents():
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


AVAILABLE_AGENTS = find_available_agents()

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

        # Ensure directories exist
        self._ensure_directories()

        # Load Company Handbook
        self.handbook = self._load_handbook()

        logger.info("=" * 60)
        logger.info("Digital FTE Orchestrator Initialized")
        logger.info(f"  Vault Path: {VAULT_PATH}")
        logger.info(f"  Max Iterations: {max_iterations}")
        logger.info(f"  Poll Interval: {poll_interval}s")
        logger.info(f"  Dry Run: {dry_run}")

        # Log available AI agents
        if AVAILABLE_AGENTS:
            agent_names = [a["name"] for a in AVAILABLE_AGENTS]
            logger.info(f"  AI Agents: {', '.join(agent_names)} (fallback order)")
        else:
            logger.warning("  AI Agents: NONE FOUND - install claude, gemini, qwen, copilot, or aider")

        logger.info("=" * 60)

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

    def create_plan_file(self, task_path: Path) -> Path:
        """Create a Plan.md file for a task."""
        task_content = task_path.read_text(encoding='utf-8')
        task_name = task_path.stem

        plan_content = f"""# Plan: {task_name}

## Task Reference
- **Source File:** {task_path.name}
- **Created:** {datetime.now().isoformat()}
- **Status:** Planning

---

## Original Task
{task_content[:500]}{"..." if len(task_content) > 500 else ""}

---

## Analysis
_Claude Code will fill this section_

---

## Execution Steps
- [ ] Step 1: Analyze the task
- [ ] Step 2: Determine required actions
- [ ] Step 3: Check against Company Handbook rules
- [ ] Step 4: Execute or request approval
- [ ] Step 5: Log results and move to Done

---

## Approval Required
- [ ] No - Auto-approve based on handbook rules
- [ ] Yes - Requires human approval

---

## Notes
_Additional context and decisions_

"""

        plan_path = task_path.parent / f"Plan_{task_name}.md"
        plan_path.write_text(plan_content, encoding='utf-8')
        return plan_path

    def build_claude_prompt(self, task_path: Path) -> str:
        """Build the prompt for Claude Code."""
        task_content = task_path.read_text(encoding='utf-8')

        prompt = f"""You are the Digital FTE assistant. Process the following task according to the Company Handbook rules.

## Company Handbook (Rules & Guidelines)
{self.handbook[:3000]}

---

## Current Task
**File:** {task_path.name}
**Location:** {task_path}

{task_content}

---

## Instructions
1. Analyze this task thoroughly
2. Determine the appropriate action based on the handbook
3. If the action requires human approval (per handbook rules), create an approval request file in Vault/Pending_Approval/
4. If auto-approved, execute the action and move the file to Vault/Done/
5. Log all decisions and actions

## Output
Provide a clear summary of:
- What you analyzed
- What decision you made
- What action you took
- Where the file was moved

Remember: Follow the handbook rules strictly. When in doubt, request human approval.
"""
        return prompt

    def invoke_agent(self, prompt: str, task_path: Path, agent: dict = None) -> tuple[bool, str]:
        """
        Invoke an AI agent with the given prompt.

        Args:
            prompt: The prompt to send to the agent
            task_path: Path to the task file
            agent: Specific agent to use (optional, uses fallback if None)

        Returns:
            Tuple of (success: bool, agent_name: str)
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would invoke AI agent with prompt for: {task_path.name}")
            return True, "dry_run"

        # Write prompt to temp file
        prompt_file = CONFIG_PATH / "current_prompt.txt"
        prompt_file.write_text(prompt, encoding='utf-8')

        # Get list of agents to try
        agents_to_try = [agent] if agent else AVAILABLE_AGENTS

        if not agents_to_try:
            logger.error("No AI agents available! Install one of: claude, gemini, qwen, copilot, opencode/aider")
            return False, "none"

        for ai_agent in agents_to_try:
            agent_name = ai_agent["name"]
            command = ai_agent["command"]
            prompt_flag = ai_agent["prompt_flag"]

            try:
                logger.info(f"Trying {agent_name.upper()} for task: {task_path.name}")

                # Build command
                if prompt_flag:
                    cmd = [command, prompt_flag, prompt]
                else:
                    cmd = [command, prompt]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    cwd=str(PROJECT_ROOT),
                    shell=(os.name == 'nt')  # Use shell on Windows
                )

                if result.returncode == 0:
                    logger.info(f"{agent_name.upper()} completed successfully")
                    logger.debug(f"Output: {result.stdout[:500]}")
                    self._log_action("agent_success", {
                        "agent": agent_name,
                        "task": task_path.name
                    })
                    return True, agent_name
                else:
                    logger.warning(f"{agent_name.upper()} failed: {result.stderr[:200]}")
                    # Try next agent

            except subprocess.TimeoutExpired:
                logger.warning(f"{agent_name.upper()} timed out, trying next agent...")
            except FileNotFoundError:
                logger.warning(f"{agent_name.upper()} not found, trying next agent...")
            except Exception as e:
                logger.warning(f"{agent_name.upper()} error: {e}, trying next agent...")

        # All agents failed
        logger.error("All AI agents failed to process the task")
        self._log_action("all_agents_failed", {"task": task_path.name})
        return False, "all_failed"

    def invoke_claude(self, prompt: str, task_path: Path) -> bool:
        """Invoke AI agent with fallback (backward compatible method)."""
        success, agent_name = self.invoke_agent(prompt, task_path)
        return success

    def process_task(self, task_path: Path) -> bool:
        """Process a single task through the Ralph Wiggum loop."""
        task_id = task_path.name
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing Task: {task_id}")
        logger.info(f"{'='*50}")

        iteration = 0
        task_completed = False

        while iteration < self.max_iterations and not task_completed:
            iteration += 1
            self.iteration_count += 1

            logger.info(f"Iteration {iteration}/{self.max_iterations}")

            # Build prompt and invoke Claude
            prompt = self.build_claude_prompt(task_path)
            success = self.invoke_claude(prompt, task_path)

            if not success:
                logger.warning(f"Claude invocation failed, retrying...")
                time.sleep(5)
                continue

            # Check if task is completed (moved to Done)
            task_completed = self._check_task_completed(task_path)

            if not task_completed:
                # Check if moved to Pending_Approval
                if self._check_pending_approval(task_path):
                    logger.info(f"Task moved to Pending_Approval, waiting for human...")
                    task_completed = True  # Exit loop, human will handle
                else:
                    logger.info("Task not completed, re-injecting prompt (Ralph Wiggum loop)")
                    time.sleep(2)

        if task_completed:
            self.processed_tasks.add(task_id)
            self._log_action("task_completed", {
                "task": task_id,
                "iterations": iteration
            })
            return True
        else:
            logger.warning(f"Task {task_id} not completed after {self.max_iterations} iterations")
            self._log_action("task_failed", {
                "task": task_id,
                "iterations": iteration,
                "reason": "max_iterations_exceeded"
            })
            return False

    def _check_task_completed(self, original_path: Path) -> bool:
        """Check if task has been moved to Done folder."""
        done_path = DONE_PATH / original_path.name
        return done_path.exists() or not original_path.exists()

    def _check_pending_approval(self, original_path: Path) -> bool:
        """Check if task has been moved to Pending_Approval folder."""
        pending_path = PENDING_APPROVAL_PATH / original_path.name
        return pending_path.exists()

    def process_approved_tasks(self):
        """Process tasks that have been approved by humans."""
        approved_tasks = self.get_approved_tasks()

        for task_path in approved_tasks:
            # Check if this is a LinkedIn post
            if task_path.name.startswith("LinkedIn_"):
                self._process_approved_linkedin_post(task_path)
                continue

            logger.info(f"Processing approved task: {task_path.name}")

            # Build execution prompt
            prompt = f"""Execute this pre-approved task. The human has approved this action.

Task file: {task_path}
Content:
{task_path.read_text(encoding='utf-8')}

Execute the approved action and move the file to Vault/Done/ when complete.
"""

            success = self.invoke_claude(prompt, task_path)

            if success:
                self._log_action("approved_task_executed", {
                    "task": task_path.name,
                    "result": "success"
                })

    def _process_approved_linkedin_post(self, task_path: Path):
        """Process an approved LinkedIn post."""
        logger.info(f"Processing approved LinkedIn post: {task_path.name}")

        if self.dry_run:
            logger.info(f"[DRY RUN] Would post to LinkedIn: {task_path.name}")
            return

        try:
            # Import LinkedIn poster
            from linkedin.linkedin_poster import LinkedInPoster
            import asyncio

            async def post_to_linkedin():
                poster = LinkedInPoster()
                await poster.start()
                try:
                    count = await poster.process_approved_posts()
                    return count
                finally:
                    await poster.stop()

            # Run async LinkedIn posting
            count = asyncio.run(post_to_linkedin())

            self._log_action("linkedin_post_executed", {
                "task": task_path.name,
                "posts_published": count,
                "result": "success"
            })

        except ImportError as e:
            logger.error(f"LinkedIn module not available: {e}")
            self._log_action("linkedin_post_failed", {
                "task": task_path.name,
                "error": "module_not_found"
            })
        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            self._log_action("linkedin_post_failed", {
                "task": task_path.name,
                "error": str(e)
            })

    def process_linkedin_queue(self):
        """Process LinkedIn queue and generate content."""
        try:
            from linkedin.content_generator import ContentGenerator

            generator = ContentGenerator()

            # Process manual posts from queue
            queue_count = generator.process_queue()
            if queue_count > 0:
                logger.info(f"Processed {queue_count} LinkedIn queue items")
                self._log_action("linkedin_queue_processed", {
                    "items": queue_count
                })

        except ImportError:
            logger.debug("LinkedIn module not available, skipping queue processing")
        except Exception as e:
            logger.error(f"Error processing LinkedIn queue: {e}")

    def _log_action(self, action: str, details: Dict[str, Any]):
        """Log action to daily log file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "actor": "orchestrator",
            "iteration_count": self.iteration_count,
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

    def run(self):
        """Main orchestrator loop."""
        logger.info("Starting Digital FTE Orchestrator main loop...")

        while True:
            try:
                # Process new tasks in Needs_Action
                pending_tasks = self.get_pending_tasks()
                logger.info(f"Found {len(pending_tasks)} pending tasks")

                for task_path in pending_tasks:
                    if task_path.name not in self.processed_tasks:
                        self.process_task(task_path)

                # Process LinkedIn queue
                self.process_linkedin_queue()

                # Process approved tasks (including LinkedIn posts)
                self.process_approved_tasks()

                # Sleep before next poll
                logger.debug(f"Sleeping for {self.poll_interval} seconds...")
                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                logger.info("Orchestrator stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self._log_action("error", {"error": str(e)})
                time.sleep(10)


def main():
    """Entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Digital FTE Orchestrator - Ralph Wiggum Loop"
    )
    parser.add_argument(
        "--max-iterations", "-m",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
        help=f"Maximum iterations per task (default: {DEFAULT_MAX_ITERATIONS})"
    )
    parser.add_argument(
        "--poll-interval", "-p",
        type=int,
        default=DEFAULT_POLL_INTERVAL,
        help=f"Seconds between polls (default: {DEFAULT_POLL_INTERVAL})"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Run without executing Claude Code"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process tasks once and exit (no loop)"
    )

    args = parser.parse_args()

    orchestrator = DigitalFTEOrchestrator(
        max_iterations=args.max_iterations,
        poll_interval=args.poll_interval,
        dry_run=args.dry_run
    )

    if args.once:
        # Process once and exit
        pending = orchestrator.get_pending_tasks()
        for task in pending:
            orchestrator.process_task(task)
        orchestrator.process_linkedin_queue()
        orchestrator.process_approved_tasks()
    else:
        # Run continuous loop
        orchestrator.run()


if __name__ == "__main__":
    main()
