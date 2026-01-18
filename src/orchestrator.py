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

# Import audit logger
from utils.audit_logger import log_audit, AuditDomain, AuditStatus

# Import domain classification
from utils.domain_classifier import classify_task, ClassificationConfidence
from models.task import Task, TaskDomain, TaskPriority, TaskStatus, TaskSource

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
LOGS_PATH = VAULT_PATH / "Logs"
PLANS_PATH = VAULT_PATH / "Plans"
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
                     APPROVED_PATH, DONE_PATH, LOGS_PATH, PLANS_PATH, LINKEDIN_QUEUE_PATH]:
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

        # Audit log: Task processing started
        log_audit(
            action="orchestrator.process_task",
            actor="orchestrator",
            domain=AuditDomain.SYSTEM,
            resource=task_id,
            status=AuditStatus.PENDING,
            details={"task_file": str(task_path)}
        )

        # Check complexity and create plan if needed
        try:
            task_content = task_path.read_text(encoding='utf-8')

            # Classify task domain
            task_title = task_id.replace('_', ' ').replace('-', ' ')
            task_domain, domain_confidence = classify_task(
                title=task_title,
                description=task_content[:500],  # First 500 chars for classification
                tags=[]
            )

            logger.info(f"Task Domain: {task_domain.value} ({domain_confidence.value} confidence)")

            # Map TaskDomain to AuditDomain for audit logging
            audit_domain_map = {
                TaskDomain.PERSONAL: AuditDomain.PERSONAL,
                TaskDomain.BUSINESS: AuditDomain.BUSINESS,
                TaskDomain.BOTH: AuditDomain.BOTH
            }
            audit_domain = audit_domain_map.get(task_domain, AuditDomain.SYSTEM)

            # Update audit log with domain classification
            log_audit(
                action="orchestrator.classify_task",
                actor="orchestrator",
                domain=audit_domain,
                resource=task_id,
                status=AuditStatus.SUCCESS,
                details={
                    "task_domain": task_domain.value,
                    "confidence": domain_confidence.value
                }
            )

            complexity_info = self.detect_complexity(task_content, task_id)

            if complexity_info['is_complex']:
                logger.info(f"🎯 Complex task detected (score: {complexity_info['complexity_score']}/10)")
                logger.info(f"📋 Generating strategic plan...")

                # Create strategic plan
                plan_path = self.create_plan(task_path, complexity_info)

                if plan_path:
                    logger.info(f"✅ Plan created: {plan_path.name}")
                else:
                    logger.warning("⚠️  Plan creation failed, continuing without plan")
            else:
                logger.info(f"Simple task (complexity: {complexity_info['complexity_score']}/10)")

        except Exception as e:
            logger.warning(f"Complexity detection failed: {e}")
            # Continue processing even if complexity detection fails

        # Normal supervision prompt
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
            # Audit log: Task completed
            log_audit(
                action="orchestrator.task_completed",
                actor="orchestrator",
                domain=AuditDomain.SYSTEM,
                resource=task_id,
                status=AuditStatus.SUCCESS,
                details={"agent": agent, "target": "Done"}
            )
            return True
        elif target_folder == "Pending_Approval":
            self._move_task(task_path, PENDING_APPROVAL_PATH)
            self._log_action("task_needs_approval", {"task": task_id, "agent": agent, "analysis": analysis})
            # Audit log: Task needs approval
            log_audit(
                action="orchestrator.task_needs_approval",
                actor="orchestrator",
                domain=AuditDomain.SYSTEM,
                resource=task_id,
                status=AuditStatus.PENDING,
                details={"agent": agent, "target": "Pending_Approval"},
                approval_required=True
            )
            return True
        else:
            logger.warning(f"Unknown target folder: {target_folder}")
            # Audit log: Task processing failed
            log_audit(
                action="orchestrator.process_task",
                actor="orchestrator",
                domain=AuditDomain.SYSTEM,
                resource=task_id,
                status=AuditStatus.FAILURE,
                details={"error": f"Unknown target folder: {target_folder}"},
                error=f"Unknown target folder: {target_folder}"
            )
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

    def detect_complexity(self, task_content: str, task_name: str) -> Dict[str, Any]:
        """
        Detect if a task is complex and needs a strategic plan.

        Returns dict with:
        - is_complex: bool
        - complexity_score: int (0-10)
        - reasons: List[str]
        - task_type: str
        """
        complexity_score = 0
        reasons = []
        task_type = "simple"

        content_lower = task_content.lower()

        # Complexity indicators

        # 1. Technical keywords (2 points each)
        technical_keywords = [
            "implement", "architecture", "design", "integrate", "refactor",
            "api", "database", "authentication", "optimization", "algorithm"
        ]
        tech_matches = sum(1 for kw in technical_keywords if kw in content_lower)
        if tech_matches >= 2:
            complexity_score += 2
            reasons.append(f"Contains {tech_matches} technical keywords")
            task_type = "technical"

        # 2. Multi-step indicators (3 points)
        step_indicators = ["step", "phase", "stage", "first", "then", "after"]
        if sum(1 for ind in step_indicators if ind in content_lower) >= 2:
            complexity_score += 3
            reasons.append("Appears to be multi-step task")

        # 3. Research/decision keywords (2 points)
        decision_keywords = ["research", "analyze", "investigate", "compare", "decide", "choose", "evaluate"]
        if any(kw in content_lower for kw in decision_keywords):
            complexity_score += 2
            reasons.append("Requires research or decision-making")
            task_type = "research"

        # 4. Length indicator (1 point if >500 chars)
        if len(task_content) > 500:
            complexity_score += 1
            reasons.append("Lengthy task description")

        # 5. Question marks (indicates uncertainty - 1 point)
        if task_content.count('?') >= 2:
            complexity_score += 1
            reasons.append("Contains multiple questions")

        # 6. Code/technical markers (2 points)
        if any(marker in task_content for marker in ['```', 'function', 'class', 'module']):
            complexity_score += 2
            reasons.append("Contains code or technical specifications")

        # 7. Integration/system keywords (3 points)
        integration_keywords = ["integrate", "connect", "sync", "migration", "deployment"]
        if any(kw in content_lower for kw in integration_keywords):
            complexity_score += 3
            reasons.append("Involves system integration")
            task_type = "integration"

        # Determine if complex (threshold: 5+)
        is_complex = complexity_score >= 5

        return {
            "is_complex": is_complex,
            "complexity_score": complexity_score,
            "reasons": reasons,
            "task_type": task_type
        }

    def build_planning_prompt(self, task_path: Path, task_content: str) -> str:
        """Build prompt for strategic plan generation."""

        prompt = f"""You are a strategic planning AI. Generate a detailed implementation plan in markdown format.

Task File: {task_path.name}
Task Content:
{task_content[:1500]}

Generate a strategic plan with these exact sections:

# Strategic Plan: [Task Title]

## Problem Analysis
- What problem are we solving?
- Why is this important?
- What are the constraints?

## Approach & Strategy
- What's the overall approach?
- Why this approach over alternatives?
- What are the key technical decisions?

## Implementation Steps
1. [Step 1 with details]
2. [Step 2 with details]
3. [Step 3 with details]
...

## Success Criteria
- How do we know we're done?
- What are the acceptance criteria?
- How will we test/validate?

## Resources Needed
- Tools, libraries, APIs required
- Documentation references
- People/expertise needed

## Risk Assessment
- What could go wrong?
- Mitigation strategies
- Contingency plans

## Timeline Estimate
- Rough time estimates per step
- Total estimated duration
- Dependencies and blockers

---
*Generated by Digital FTE Orchestrator*
*Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

Output ONLY the markdown plan above. Do not add any other text."""

        return prompt

    def create_plan(self, task_path: Path, complexity_info: Dict[str, Any]) -> Optional[Path]:
        """
        Create a strategic Plan.md file for a complex task.

        Returns path to created plan file or None if failed.
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create plan for: {task_path.name}")
            return None

        try:
            task_content = task_path.read_text(encoding='utf-8')

            logger.info(f"Creating strategic plan for: {task_path.name}")
            logger.info(f"Complexity Score: {complexity_info['complexity_score']}/10")
            logger.info(f"Reasons: {', '.join(complexity_info['reasons'])}")

            # Build planning prompt
            prompt = self.build_planning_prompt(task_path, task_content)

            # Invoke AI agent for plan generation
            success, response_data, agent = self.invoke_agent(prompt, task_path)

            if not success:
                logger.warning("Failed to generate plan - continuing without plan")
                return None

            # Extract plan content
            # The response might be JSON or direct markdown
            if isinstance(response_data, dict):
                # If JSON, look for plan in various keys
                plan_content = response_data.get('plan') or response_data.get('content') or response_data.get('analysis') or str(response_data)
            else:
                plan_content = str(response_data)

            # Generate plan filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            task_type = complexity_info.get('task_type', 'general')

            # Extract brief description from task name (remove timestamp and metadata)
            brief_desc = re.sub(r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}_', '', task_path.stem)
            brief_desc = re.sub(r'_(high|medium|low|urgent)_', '_', brief_desc)
            brief_desc = brief_desc[:50]  # Limit length

            plan_filename = f"{timestamp}_{task_type}_{brief_desc}.plan.md"
            plan_path = PLANS_PATH / plan_filename

            # Write plan file
            plan_path.write_text(plan_content, encoding='utf-8')

            logger.info(f"Plan created: {plan_filename}")
            logger.info(f"Plan saved to: {plan_path}")

            # Log plan creation
            self._log_action("plan_created", {
                "task": task_path.name,
                "plan_file": plan_filename,
                "complexity_score": complexity_info['complexity_score'],
                "agent": agent,
                "task_type": task_type
            })

            # Audit log: Plan created
            log_audit(
                action="orchestrator.create_plan",
                actor=agent,
                domain=AuditDomain.SYSTEM,
                resource=plan_filename,
                status=AuditStatus.SUCCESS,
                details={
                    "task": task_path.name,
                    "complexity_score": complexity_info['complexity_score'],
                    "task_type": task_type
                }
            )

            # Add plan reference to task file
            self._add_plan_reference(task_path, plan_path)

            return plan_path

        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            return None

    def _add_plan_reference(self, task_path: Path, plan_path: Path):
        """Add reference to plan in task file."""
        try:
            content = task_path.read_text(encoding='utf-8')

            # Add plan reference at the top
            plan_reference = f"""
---
**📋 Strategic Plan Generated:** [{plan_path.name}](../Plans/{plan_path.name})
**Plan Location:** `Vault/Plans/{plan_path.name}`
---

"""
            # Insert after first header or at beginning
            if content.startswith('#'):
                lines = content.split('\n')
                # Find first non-header line
                insert_idx = 1
                for i, line in enumerate(lines[1:], 1):
                    if not line.startswith('#') and line.strip():
                        insert_idx = i
                        break
                lines.insert(insert_idx, plan_reference)
                content = '\n'.join(lines)
            else:
                content = plan_reference + content

            task_path.write_text(content, encoding='utf-8')
            logger.info(f"Added plan reference to task file")

        except Exception as e:
            logger.warning(f"Could not add plan reference to task: {e}")

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