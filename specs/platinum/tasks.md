# Platinum Tier Implementation Tasks

**Version:** 1.0
**Date:** 2026-01-22
**Status:** Draft - Ready for Implementation
**Estimated Total Time:** 40-60 hours
**Target Completion:** 2026-01-29 (7 days)

---

## Table of Contents

1. [Task Organization](#1-task-organization)
2. [Phase 1: Foundation (8-12h)](#2-phase-1-foundation)
3. [Phase 2: Cloud Agent (10-15h)](#3-phase-2-cloud-agent)
4. [Phase 3: Work-Zone System (8-12h)](#4-phase-3-work-zone-system)
5. [Phase 4: Git Communication (6-10h)](#5-phase-4-git-communication)
6. [Phase 5: Testing & Validation (8-11h)](#6-phase-5-testing--validation)
7. [Phase 6: Documentation & Demo (0h - parallel)](#7-phase-6-documentation--demo)

---

## 1. Task Organization

### 1.1 Implementation Principles

**✅ DO:**
- Commit after every completed task
- Test each feature before moving to next
- Create small, atomic changes
- Document decisions in code comments
- Use existing Gold Tier code where possible

**❌ DON'T:**
- Refactor Gold Tier code unnecessarily
- Add features not in spec
- Skip testing for "simple" tasks
- Work on multiple phases in parallel

### 1.2 Task Format

Each task follows this structure:

```markdown
### T-XXX: Task Title

**Estimated Time:** X-Y hours
**Priority:** High / Medium / Low
**Dependencies:** T-AAA, T-BBB
**Phase:** N

**Objective:**
Clear description of what needs to be done.

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Implementation Steps:**
1. Step 1
2. Step 2

**Test Plan:**
- How to verify this works

**Files to Create/Modify:**
- `path/to/file1.py`
- `path/to/file2.py`
```

### 1.3 Dependency Graph

```
Phase 1 (Foundation)
    │
    ├──► T-101: Environment config
    ├──► T-102: Git sync utility
    ├──► T-103: Claim-by-move
    └──► T-104: Work-zone enforcer
         │
         ▼
Phase 2 (Cloud Agent)
    │
    ├──► T-201: Oracle VM setup
    ├──► T-202: Systemd service
    └──► T-203: Cloud config
         │
         ▼
Phase 3 (Work-Zone System)
    │
    ├──► T-301: Orchestrator mods
    ├──► T-302: Draft creation
    └──► T-303: Execution blocking
         │
         ▼
Phase 4 (Git Communication)
    │
    ├──► T-401: Auto-sync loop
    ├──► T-402: Conflict resolution
    └──► T-403: Dashboard updates
         │
         ▼
Phase 5 (Testing)
    │
    ├──► T-501: Unit tests
    ├──► T-502: Integration tests
    └──► T-503: End-to-end demo
         │
         ▼
Phase 6 (Documentation)
    │
    ├──► T-601: Deployment guide
    ├──► T-602: Operations manual
    └──► T-603: Demo script
```

---

## 2. Phase 1: Foundation (8-12h)

**Objective:** Set up core utilities for Platinum Tier architecture

**Deliverables:**
- Environment configuration system
- Git synchronization utility
- Claim-by-move implementation
- Work-zone enforcement framework

---

### T-101: Environment Configuration for Work-Zones

**Estimated Time:** 1-2 hours
**Priority:** High
**Dependencies:** None
**Phase:** 1

**Objective:**
Create environment configuration templates for Cloud and Local work-zones with proper secret isolation.

**Acceptance Criteria:**
- [ ] `.env.cloud.example` created with WORK_ZONE=cloud
- [ ] `.env.local.example` created with WORK_ZONE=local
- [ ] Cloud config has no MCP credentials
- [ ] Local config has all MCP credentials
- [ ] `.gitignore` updated to exclude .env files
- [ ] Validation: Running on cloud loads cloud config, local loads local config

**Implementation Steps:**
1. Copy `config/.env.example` to `config/.env.cloud.example`
2. Modify cloud config:
   - Set `WORK_ZONE=cloud`
   - Set `AGENT_ID=cloud-oracle-001`
   - Remove all MCP credentials (EMAIL_*, ODOO_*, META_*, TWITTER_*)
   - Set `EMAIL_MCP_ENABLED=false`
   - Set watchers: `GMAIL_ENABLED=true`, `FILESYSTEM_ENABLED=false`
3. Copy `config/.env.example` to `config/.env.local.example`
4. Modify local config:
   - Set `WORK_ZONE=local`
   - Set `AGENT_ID=local-laptop-001`
   - Keep all MCP credentials as placeholders
   - Set watchers: `GMAIL_ENABLED=false`, `FILESYSTEM_ENABLED=true`
5. Update `.gitignore`:
   ```
   .env
   .env.local
   .env.cloud
   *.key
   *.pem
   credentials.json
   secrets/
   ```
6. Create `src/utils/config.py`:
   ```python
   import os
   from enum import Enum
   from dotenv import load_dotenv

   class WorkZone(Enum):
       CLOUD = "cloud"
       LOCAL = "local"

   def load_config():
       """Load environment config based on WORK_ZONE."""
       load_dotenv()  # Load .env file
       work_zone_str = os.getenv("WORK_ZONE", "local")
       work_zone = WorkZone(work_zone_str)
       return {
           "work_zone": work_zone,
           "agent_id": os.getenv("AGENT_ID"),
           "vault_path": os.getenv("VAULT_PATH"),
           # ... other config
       }
   ```
7. Write validation script: `tests/test_config.py`

**Test Plan:**
```bash
# Test cloud config
export WORK_ZONE=cloud
python -c "from src.utils.config import load_config; print(load_config())"
# Expected: work_zone=CLOUD, no MCP credentials

# Test local config
export WORK_ZONE=local
python -c "from src.utils.config import load_config; print(load_config())"
# Expected: work_zone=LOCAL, MCP credentials present
```

**Files to Create:**
- `config/.env.cloud.example`
- `config/.env.local.example`
- `src/utils/config.py`
- `tests/test_config.py`

**Files to Modify:**
- `.gitignore` (add secret patterns)

---

### T-102: Git Synchronization Utility

**Estimated Time:** 2-3 hours
**Priority:** High
**Dependencies:** None
**Phase:** 1

**Objective:**
Implement Git pull/push utility with conflict resolution and error handling.

**Acceptance Criteria:**
- [ ] `git_sync.py` module created
- [ ] `git_pull()` function with rebase strategy
- [ ] `git_push()` function with structured commit messages
- [ ] Conflict auto-resolution (local always wins)
- [ ] Timeout handling (30s max)
- [ ] Error logging and retry logic
- [ ] Unit tests pass

**Implementation Steps:**
1. Create `src/utils/git_sync.py`
2. Implement `git_pull()`:
   ```python
   def git_pull() -> dict:
       """
       Pull latest changes with rebase.

       Returns:
           {
               "success": bool,
               "files_changed": int,
               "conflicts": list[str],
               "error": str | None
           }
       """
       try:
           result = subprocess.run(
               ["git", "pull", "origin", "main", "--rebase"],
               capture_output=True,
               text=True,
               timeout=30,
               cwd=VAULT_PATH,
           )

           if result.returncode == 0:
               return {
                   "success": True,
                   "files_changed": count_changed_files(result.stdout),
                   "conflicts": [],
                   "error": None,
               }
           elif "CONFLICT" in result.stdout:
               # Auto-resolve conflicts
               conflicts = parse_conflicts(result.stdout)
               for file in conflicts:
                   subprocess.run(["git", "checkout", "--ours", file], cwd=VAULT_PATH)
               subprocess.run(["git", "add", "."], cwd=VAULT_PATH)
               subprocess.run(["git", "rebase", "--continue"], cwd=VAULT_PATH)

               return {
                   "success": True,
                   "files_changed": count_changed_files(result.stdout),
                   "conflicts": conflicts,
                   "error": None,
               }
           else:
               return {
                   "success": False,
                   "files_changed": 0,
                   "conflicts": [],
                   "error": result.stderr,
               }
       except subprocess.TimeoutExpired:
           return {
               "success": False,
               "files_changed": 0,
               "conflicts": [],
               "error": "Git pull timeout (>30s)",
           }
       except Exception as e:
           return {
               "success": False,
               "files_changed": 0,
               "conflicts": [],
               "error": str(e),
           }
   ```
3. Implement `git_push()`:
   ```python
   def git_push(agent_id: str, description: str, folders: list[str]) -> dict:
       """
       Stage changes and push to remote.

       Args:
           agent_id: Agent identifier
           description: Brief description of changes
           folders: List of folders to stage

       Returns:
           {
               "success": bool,
               "files_pushed": int,
               "commit_sha": str | None,
               "error": str | None
           }
       """
       try:
           # Stage changes
           subprocess.run(["git", "add"] + folders, cwd=VAULT_PATH)

           # Check for changes
           status = subprocess.run(
               ["git", "status", "--porcelain"],
               capture_output=True,
               text=True,
               cwd=VAULT_PATH,
           )

           if not status.stdout.strip():
               return {
                   "success": True,
                   "files_pushed": 0,
                   "commit_sha": None,
                   "error": None,
               }

           # Commit
           timestamp = datetime.now().isoformat()
           commit_msg = f"{agent_id}: {description} - {timestamp}"
           subprocess.run(["git", "commit", "-m", commit_msg], cwd=VAULT_PATH)

           # Push
           result = subprocess.run(
               ["git", "push", "origin", "main"],
               capture_output=True,
               text=True,
               timeout=30,
               cwd=VAULT_PATH,
           )

           if result.returncode == 0:
               return {
                   "success": True,
                   "files_pushed": count_committed_files(),
                   "commit_sha": get_last_commit_sha(),
                   "error": None,
               }
           else:
               return {
                   "success": False,
                   "files_pushed": 0,
                   "commit_sha": None,
                   "error": result.stderr,
               }
       except subprocess.TimeoutExpired:
           return {
               "success": False,
               "files_pushed": 0,
               "commit_sha": None,
               "error": "Git push timeout (>30s)",
           }
       except Exception as e:
           return {
               "success": False,
               "files_pushed": 0,
               "commit_sha": None,
               "error": str(e),
           }
   ```
4. Implement helper functions:
   - `count_changed_files(git_output: str) -> int`
   - `parse_conflicts(git_output: str) -> list[str]`
   - `count_committed_files() -> int`
   - `get_last_commit_sha() -> str`
5. Add error recovery with retry:
   ```python
   from src.utils.error_recovery import retry_with_backoff, RetryConfig

   @retry_with_backoff(RetryConfig(max_retries=3, initial_delay=1.0))
   def git_pull_with_retry() -> dict:
       return git_pull()
   ```
6. Write unit tests: `tests/test_git_sync.py`
   - Test successful pull
   - Test conflict resolution
   - Test push with no changes
   - Test push with changes
   - Test timeout handling

**Test Plan:**
```bash
# Setup test repository
mkdir -p /tmp/test_vault
cd /tmp/test_vault
git init
echo "test" > test.txt
git add .
git commit -m "initial"

# Test pull
python -c "from src.utils.git_sync import git_pull; print(git_pull())"

# Create conflict
echo "local change" > test.txt
git add test.txt
git commit -m "local"

# Simulate remote change
echo "remote change" > test.txt
git add test.txt
git commit -m "remote"

# Test pull with conflict
python -c "from src.utils.git_sync import git_pull; print(git_pull())"
# Expected: conflicts auto-resolved, local wins

# Test push
python -c "from src.utils.git_sync import git_push; print(git_push('test-agent', 'test push', ['.']))"
# Expected: success, commit pushed
```

**Files to Create:**
- `src/utils/git_sync.py`
- `tests/test_git_sync.py`

---

### T-103: Claim-by-Move Implementation

**Estimated Time:** 2-3 hours
**Priority:** High
**Dependencies:** None
**Phase:** 1

**Objective:**
Implement atomic task claiming using filesystem move operation to prevent race conditions.

**Acceptance Criteria:**
- [ ] `claim_by_move.py` module created
- [ ] `claim_task()` function uses atomic rename
- [ ] Race condition test passes (concurrent claims)
- [ ] Handles FileNotFoundError gracefully
- [ ] Audit logging for claims
- [ ] Unit tests pass

**Implementation Steps:**
1. Create `src/utils/claim_by_move.py`
2. Implement `claim_task()`:
   ```python
   import os
   from pathlib import Path
   from src.utils.audit_logger import log_audit, AuditDomain, AuditStatus

   def claim_task(
       task_path: Path,
       agent_id: str,
       destination_folder: str,
   ) -> tuple[bool, str]:
       """
       Atomically claim task by moving to destination.

       Args:
           task_path: Path to task file (e.g., Vault/Needs_Action/task.md)
           agent_id: Agent identifier (e.g., "cloud-oracle-001")
           destination_folder: Folder name (e.g., "Drafts", "Approved")

       Returns:
           (success: bool, message: str)
       """
       try:
           # Compute destination path
           vault_root = task_path.parent.parent
           dest_path = vault_root / destination_folder / task_path.name

           # Atomic rename (only succeeds if source exists)
           # This is atomic on POSIX (Linux, macOS) and Windows (MoveFile)
           os.rename(task_path, dest_path)

           # Successfully claimed
           message = f"Claimed task: {task_path.name} → {destination_folder}/"

           # Log claim
           log_audit(
               event="TASK_CLAIMED",
               task_id=task_path.stem,
               agent_id=agent_id,
               status=AuditStatus.SUCCESS,
               details={
                   "source": task_path.parent.name,
                   "destination": destination_folder,
               },
           )

           return (True, message)

       except FileNotFoundError:
           # Another agent already moved the file
           message = f"Task already claimed: {task_path.name}"

           log_audit(
               event="TASK_CLAIM_FAILED",
               task_id=task_path.stem,
               agent_id=agent_id,
               status=AuditStatus.FAILED,
               details={
                   "reason": "already_claimed",
                   "source": task_path.parent.name,
               },
           )

           return (False, message)

       except Exception as e:
           # Unexpected error
           message = f"Error claiming task: {str(e)}"

           log_audit(
               event="TASK_CLAIM_ERROR",
               task_id=task_path.stem,
               agent_id=agent_id,
               status=AuditStatus.FAILED,
               details={
                   "error": str(e),
               },
           )

           return (False, message)
   ```
3. Add bulk claim function:
   ```python
   def claim_tasks_batch(
       task_paths: list[Path],
       agent_id: str,
       destination_folder: str,
   ) -> dict:
       """
       Claim multiple tasks atomically.

       Returns:
           {
               "claimed": list[Path],
               "failed": list[Path],
               "already_claimed": list[Path],
           }
       """
       results = {
           "claimed": [],
           "failed": [],
           "already_claimed": [],
       }

       for task_path in task_paths:
           success, message = claim_task(task_path, agent_id, destination_folder)

           if success:
               results["claimed"].append(task_path)
           elif "already claimed" in message:
               results["already_claimed"].append(task_path)
           else:
               results["failed"].append(task_path)

       return results
   ```
4. Write race condition test:
   ```python
   # tests/test_claim_by_move.py

   import threading 
   from pathlib import Path
   from src.utils.claim_by_move import claim_task

   def test_race_condition():
       """Test that only one agent can claim a task."""

       # Setup
       task_file = Path("Vault/Needs_Action/test_task.md")
       task_file.parent.mkdir(parents=True, exist_ok=True)
       task_file.write_text("test task")

       results = []

       def agent_claim(agent_id):
           success, msg = claim_task(task_file, agent_id, "Drafts")
           results.append((agent_id, success))

       # Run two agents concurrently
       thread1 = threading.Thread(target=agent_claim, args=("agent1",))
       thread2 = threading.Thread(target=agent_claim, args=("agent2",))

       thread1.start()
       thread2.start()

       thread1.join()
       thread2.join()

       # Verify: Only one agent succeeded
       successes = [r for r in results if r[1]]
       assert len(successes) == 1, f"Expected 1 success, got {len(successes)}"

       # Verify: File moved to Drafts/
       assert (Path("Vault/Drafts/test_task.md")).exists()
       assert not task_file.exists()
   ```

**Test Plan:**
```bash
# Unit tests
pytest tests/test_claim_by_move.py -v

# Manual test: Race condition
# Terminal 1
python -c "from src.utils.claim_by_move import claim_task; from pathlib import Path; print(claim_task(Path('Vault/Needs_Action/task1.md'), 'cloud', 'Drafts'))"

# Terminal 2 (run simultaneously)
python -c "from src.utils.claim_by_move import claim_task; from pathlib import Path; print(claim_task(Path('Vault/Needs_Action/task1.md'), 'local', 'Approved'))"

# Expected: Only one succeeds, other gets "already claimed"
```

**Files to Create:**
- `src/utils/claim_by_move.py`
- `tests/test_claim_by_move.py`

---

### T-104: Work-Zone Enforcement Framework

**Estimated Time:** 2-3 hours
**Priority:** High
**Dependencies:** T-101
**Phase:** 1

**Objective:**
Implement work-zone enforcement to prevent Cloud agent from executing sensitive actions.

**Acceptance Criteria:**
- [ ] `work_zone.py` module created
- [ ] `can_execute_action()` function enforces restrictions
- [ ] Cloud work-zone blocks email, social, financial actions
- [ ] Local work-zone allows all actions
- [ ] Audit logging for blocked executions
- [ ] Unit tests pass

**Implementation Steps:**
1. Create `src/utils/work_zone.py`
2. Define enums and constants:
   ```python
   from enum import Enum
   from typing import Tuple

   class WorkZone(Enum):
       CLOUD = "cloud"  # Draft mode only
       LOCAL = "local"  # Full execution

   class ActionType(Enum):
       # Sensitive actions (require LOCAL)
       SEND_EMAIL = "send_email"
       POST_SOCIAL_MEDIA = "post_social_media"
       CREATE_INVOICE = "create_invoice"
       RECORD_EXPENSE = "record_expense"
       SEND_WHATSAPP = "send_whatsapp"
       FINANCIAL_TRANSACTION = "financial_transaction"

       # Safe actions (allowed in CLOUD)
       READ_DATA = "read_data"
       SEARCH_EMAILS = "search_emails"
       LIST_CONTACTS = "list_contacts"

   # Sensitive actions that require Local work-zone
   SENSITIVE_ACTIONS = {
       ActionType.SEND_EMAIL,
       ActionType.POST_SOCIAL_MEDIA,
       ActionType.CREATE_INVOICE,
       ActionType.RECORD_EXPENSE,
       ActionType.SEND_WHATSAPP,
       ActionType.FINANCIAL_TRANSACTION,
   }
   ```
3. Implement enforcement function:
   ```python
   def can_execute_action(
       action: ActionType,
       work_zone: WorkZone,
   ) -> Tuple[bool, str]:
       """
       Check if action can be executed in current work-zone.

       Args:
           action: Action type to execute
           work_zone: Current work-zone (from WORK_ZONE env var)

       Returns:
           (allowed: bool, reason: str)
       """
       if action in SENSITIVE_ACTIONS and work_zone == WorkZone.CLOUD:
           return (
               False,
               f"Action '{action.value}' requires LOCAL work-zone "
               f"(human approval required). Current work-zone: {work_zone.value}",
           )

       return (True, f"Action '{action.value}' permitted in {work_zone.value} work-zone")
   ```
4. Add helper to get current work-zone:
   ```python
   import os

   def get_current_work_zone() -> WorkZone:
       """Get work-zone from environment variable."""
       work_zone_str = os.getenv("WORK_ZONE", "local")
       try:
           return WorkZone(work_zone_str)
       except ValueError:
           # Default to local if invalid
           return WorkZone.LOCAL
   ```
5. Add logging helper:
   ```python
   from src.utils.audit_logger import log_audit, AuditStatus

   def log_execution_blocked(
       task_id: str,
       action: ActionType,
       work_zone: WorkZone,
       agent_id: str,
   ):
       """Log when execution is blocked by work-zone."""
       log_audit(
           event="EXECUTION_BLOCKED",
           task_id=task_id,
           agent_id=agent_id,
           status=AuditStatus.BLOCKED,
           details={
               "action": action.value,
               "work_zone": work_zone.value,
               "reason": "work_zone_restriction",
           },
       )
   ```
6. Write unit tests:
   ```python
   # tests/test_work_zone.py

   from src.utils.work_zone import (
       can_execute_action,
       ActionType,
       WorkZone,
   )

   def test_cloud_blocks_sensitive_actions():
       """Cloud work-zone should block sensitive actions."""
       action = ActionType.SEND_EMAIL
       work_zone = WorkZone.CLOUD

       allowed, reason = can_execute_action(action, work_zone)

       assert allowed == False
       assert "LOCAL work-zone" in reason

   def test_cloud_allows_safe_actions():
       """Cloud work-zone should allow safe actions."""
       action = ActionType.READ_DATA
       work_zone = WorkZone.CLOUD

       allowed, reason = can_execute_action(action, work_zone)

       assert allowed == True

   def test_local_allows_all_actions():
       """Local work-zone should allow all actions."""
       action = ActionType.SEND_EMAIL
       work_zone = WorkZone.LOCAL

       allowed, reason = can_execute_action(action, work_zone)

       assert allowed == True
   ```

**Test Plan:**
```bash
# Unit tests
pytest tests/test_work_zone.py -v

# Integration test
export WORK_ZONE=cloud
python -c "
from src.utils.work_zone import can_execute_action, ActionType, get_current_work_zone
wz = get_current_work_zone()
print(can_execute_action(ActionType.SEND_EMAIL, wz))
"
# Expected: (False, "...requires LOCAL work-zone...")

export WORK_ZONE=local
python -c "
from src.utils.work_zone import can_execute_action, ActionType, get_current_work_zone
wz = get_current_work_zone()
print(can_execute_action(ActionType.SEND_EMAIL, wz))
"
# Expected: (True, "Action 'send_email' permitted...")
```

**Files to Create:**
- `src/utils/work_zone.py`
- `tests/test_work_zone.py`

---

### T-105: Create Vault Drafts Folder

**Estimated Time:** 0.5 hours
**Priority:** Medium
**Dependencies:** None
**Phase:** 1

**Objective:**
Create `Vault/Drafts/` folder for Cloud-generated drafts and update .gitignore.

**Acceptance Criteria:**
- [ ] `Vault/Drafts/` folder created
- [ ] `.gitkeep` file added (track empty folder)
- [ ] `Vault/Drafts/README.md` explains purpose
- [ ] Folder committed to Git

**Implementation Steps:**
1. Create folder:
   ```bash
   mkdir -p Vault/Drafts
   ```
2. Add `.gitkeep`:
   ```bash
   touch Vault/Drafts/.gitkeep
   ```
3. Create `Vault/Drafts/README.md`:
   ```markdown
   # Drafts Folder

   This folder contains draft responses and actions generated by the Cloud Agent.

   **Purpose:**
   - Cloud Agent (24/7 VM) monitors incoming tasks and creates drafts
   - Drafts are saved here for human review
   - Local Agent pulls drafts and displays them in Obsidian for approval

   **Workflow:**
   1. Cloud Agent detects new task (email, WhatsApp, LinkedIn)
   2. Cloud Agent generates draft response (AI-powered)
   3. Cloud Agent saves draft to this folder
   4. Cloud Agent pushes to Git (syncs to Local)
   5. Local Agent pulls and displays draft in Obsidian
   6. Human reviews and approves/rejects draft
   7. If approved, Local Agent executes action

   **File Format:**
   - Filename: `{timestamp}_{source}_{priority}_{slug}.md`
   - Content: YAML frontmatter + Markdown body
   - See `specs/platinum/architecture.md` for full schema

   **Security:**
   - Cloud Agent cannot execute actions (work-zone restriction)
   - All drafts require human approval before execution
   - Audit trail for all drafts (Logs/audit/)
   ```
4. Commit:
   ```bash
   git add Vault/Drafts/
   git commit -m "feat: add Drafts folder for Platinum Tier cloud-generated drafts"
   ```

**Test Plan:**
```bash
# Verify folder exists
ls -la Vault/Drafts/

# Verify in Git
git ls-tree HEAD Vault/Drafts/
# Expected: .gitkeep and README.md

# Verify README content
cat Vault/Drafts/README.md
```

**Files to Create:**
- `Vault/Drafts/.gitkeep`
- `Vault/Drafts/README.md`

---

## 3. Phase 2: Cloud Agent (10-15h)

**Objective:** Deploy and configure Cloud Agent on Oracle Cloud VM

**Deliverables:**
- Oracle Cloud VM provisioned
- Python environment set up
- Systemd service configured
- Cloud Agent running 24/7

---

### T-201: Oracle Cloud VM Provisioning

**Estimated Time:** 2-3 hours
**Priority:** High
**Dependencies:** None
**Phase:** 2

**Objective:**
Create Oracle Cloud VM instance with proper networking and security configuration.

**Acceptance Criteria:**
- [ ] Oracle Cloud account created (free tier)
- [ ] Compute instance created (VM.Standard.A1.Flex, 4 OCPU, 24 GB RAM)
- [ ] Ubuntu 22.04 ARM64 installed
- [ ] SSH key-based authentication configured
- [ ] Security list allows SSH (port 22)
- [ ] Public IP assigned
- [ ] Can SSH into instance

**Implementation Steps:**
1. **Create Oracle Cloud Account:**
   - Go to https://www.oracle.com/cloud/free/
   - Sign up for Always Free tier
   - Verify email and phone
   - Complete account setup

2. **Create VCN (Virtual Cloud Network):**
   ```
   OCI Console → Networking → Virtual Cloud Networks → Create VCN

   Name: digitalfte-vcn
   CIDR Block: 10.0.0.0/16
   Compartment: (root) or create new

   Create Subnet:
   Name: digitalfte-subnet
   Type: Regional
   CIDR Block: 10.0.0.0/24
   Access: Public
   ```

3. **Configure Security List:**
   ```
   VCN → Security Lists → Default Security List

   Ingress Rules:
   - Source: 0.0.0.0/0
     Protocol: TCP
     Destination Port: 22 (SSH)

   Egress Rules:
   - Destination: 0.0.0.0/0
     Protocol: All
   ```

4. **Create Compute Instance:**
   ```
   OCI Console → Compute → Instances → Create Instance

   Name: digitalfte-cloud-001
   Image: Ubuntu 22.04 Minimal ARM64 (Always Free)
   Shape: VM.Standard.A1.Flex
   OCPU: 4
   Memory: 24 GB
   Boot Volume: 200 GB

   Network:
   VCN: digitalfte-vcn
   Subnet: digitalfte-subnet
   Assign Public IP: Yes

   SSH Keys:
   - Upload your public SSH key (~/.ssh/id_rsa.pub)
   OR
   - Generate new key pair (download private key)
   ```

5. **Note Public IP:**
   ```
   After instance creation, note the Public IP address.
   Example: 123.45.67.89
   ```

6. **Test SSH Connection:**
   ```bash
   ssh ubuntu@<PUBLIC_IP>

   # If using custom key:
   ssh -i ~/.ssh/oracle_cloud_key ubuntu@<PUBLIC_IP>
   ```

7. **Initial System Setup:**
   ```bash
   # SSH into instance
   ssh ubuntu@<PUBLIC_IP>

   # Update system
   sudo apt update
   sudo apt upgrade -y

   # Install basic tools
   sudo apt install -y \
       git \
       curl \
       wget \
       htop \
       vim \
       build-essential

   # Verify ARM architecture
   uname -m
   # Expected: aarch64
   ```

8. **Document Access Info:**
   Create `docs/ORACLE_CLOUD_ACCESS.md`:
   ```markdown
   # Oracle Cloud Access

   **Instance:** digitalfte-cloud-001
   **Public IP:** <PUBLIC_IP>
   **SSH Key:** ~/.ssh/oracle_cloud_key
   **Username:** ubuntu

   **SSH Command:**
   ```bash
   ssh -i ~/.ssh/oracle_cloud_key ubuntu@<PUBLIC_IP>
   ```

   **OCI Console:**
   https://cloud.oracle.com/compute/instances
   ```

**Test Plan:**
```bash
# Verify SSH access
ssh ubuntu@<PUBLIC_IP>

# Verify resources
ssh ubuntu@<PUBLIC_IP> 'cat /proc/cpuinfo | grep processor | wc -l'
# Expected: 4 (4 cores)

ssh ubuntu@<PUBLIC_IP> 'free -h'
# Expected: ~24GB RAM

ssh ubuntu@<PUBLIC_IP> 'df -h /'
# Expected: ~200GB disk

# Verify internet connectivity
ssh ubuntu@<PUBLIC_IP> 'ping -c 3 google.com'
# Expected: successful ping
```

**Files to Create:**
- `docs/ORACLE_CLOUD_ACCESS.md`

---

### T-202: Cloud VM Software Installation

**Estimated Time:** 2-3 hours
**Priority:** High
**Dependencies:** T-201
**Phase:** 2

**Objective:**
Install Python 3.14, dependencies, and clone repository on Oracle Cloud VM.

**Acceptance Criteria:**
- [ ] Python 3.14 installed
- [ ] Git configured with SSH keys
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Environment variables configured

**Implementation Steps:**
1. **SSH into Oracle VM:**
   ```bash
   ssh ubuntu@<PUBLIC_IP>
   ```

2. **Install Python 3.14:**
   ```bash
   # Add deadsnakes PPA (Python backports for Ubuntu)
   sudo add-apt-repository ppa:deadsnakes/ppa -y
   sudo apt update

   # Install Python 3.14 and dev tools
   sudo apt install -y \
       python3.14 \
       python3.14-venv \
       python3.14-dev \
       python3-pip

   # Verify installation
   python3.14 --version
   # Expected: Python 3.14.x
   ```

3. **Create Service User:**
   ```bash
   # Create dedicated user for running agent
   sudo useradd -m -s /bin/bash digitalfte
   sudo -u digitalfte -i

   # All subsequent commands run as digitalfte user
   ```

4. **Generate SSH Key for Git:**
   ```bash
   # Generate SSH key
   ssh-keygen -t ed25519 -C "cloud-agent@digitalfte" -f ~/.ssh/id_ed25519_cloud -N ""

   # Display public key
   cat ~/.ssh/id_ed25519_cloud.pub

   # Copy public key to clipboard (manually)
   ```

5. **Add Deploy Key to GitHub:**
   ```
   GitHub → Repository Settings → Deploy Keys → Add Deploy Key

   Title: Oracle Cloud Agent (Read/Write)
   Key: <paste public key from above>
   Allow write access: ✓
   ```

6. **Configure Git:**
   ```bash
   git config --global user.name "Cloud Agent"
   git config --global user.email "cloud-agent@digitalfte"

   # Configure SSH for GitHub
   cat >> ~/.ssh/config <<EOF
   Host github.com
       HostName github.com
       User git
       IdentityFile ~/.ssh/id_ed25519_cloud
       StrictHostKeyChecking no
   EOF

   chmod 600 ~/.ssh/config
   ```

7. **Test GitHub SSH:**
   ```bash
   ssh -T git@github.com
   # Expected: "Hi username/digital-fte-vault! You've successfully authenticated..."
   ```

8. **Clone Repository:**
   ```bash
   cd ~
   git clone git@github.com:username/digital-fte-vault.git Hacathan_2
   cd Hacathan_2

   # Verify clone
   git status
   git log -1
   ```

9. **Create Virtual Environment:**
   ```bash
   python3.14 -m venv .venv
   source .venv/bin/activate

   # Verify
   which python
   # Expected: /home/digitalfte/Hacathan_2/.venv/bin/python

   python --version
   # Expected: Python 3.14.x
   ```

10. **Install Dependencies:**
    ```bash
    # Upgrade pip
    pip install --upgrade pip

    # Install requirements
    pip install -r requirements.txt

    # Verify key packages
    pip list | grep -E "anthropic|google|fastmcp"
    ```

11. **Configure Environment:**
    ```bash
    # Copy cloud config template
    cp config/.env.cloud.example .env

    # Edit config (no credentials needed for cloud)
    nano .env
    # Set:
    # - WORK_ZONE=cloud
    # - AGENT_ID=cloud-oracle-001
    # - VAULT_PATH=/home/digitalfte/Hacathan_2/Vault
    # - All MCP servers disabled
    # - Gmail/WhatsApp/LinkedIn watchers enabled
    ```

12. **Test Basic Import:**
    ```bash
    python -c "from src.orchestrator import main; print('Import successful')"
    ```

**Test Plan:**
```bash
# Test Python
ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte python3.14 --version'
# Expected: Python 3.14.x

# Test Git clone
ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte ls -la ~/Hacathan_2'
# Expected: Repository files listed

# Test virtual environment
ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte bash -c "cd ~/Hacathan_2 && source .venv/bin/activate && which python"'
# Expected: /home/digitalfte/Hacathan_2/.venv/bin/python

# Test dependencies
ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte bash -c "cd ~/Hacathan_2 && source .venv/bin/activate && pip list"'
# Expected: All packages listed

# Test environment config
ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte cat ~/Hacathan_2/.env | grep WORK_ZONE'
# Expected: WORK_ZONE=cloud
```

**Files to Modify:**
- `.env` (on Oracle VM)

---

### T-203: Systemd Service Configuration

**Estimated Time:** 2-3 hours
**Priority:** High
**Dependencies:** T-202
**Phase:** 2

**Objective:**
Configure systemd service for auto-start and auto-restart of Cloud Agent.

**Acceptance Criteria:**
- [ ] Systemd service file created
- [ ] Service enabled and started
- [ ] Auto-restart on crash verified
- [ ] Logging to journalctl working
- [ ] Resource limits enforced

**Implementation Steps:**
1. **Create Systemd Service File:**
   ```bash
   # SSH into Oracle VM
   ssh ubuntu@<PUBLIC_IP>

   # Create service file
   sudo nano /etc/systemd/system/digitalfte-cloud.service
   ```

   ```ini
   [Unit]
   Description=Digital FTE Cloud Agent (Draft Mode)
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=simple
   User=digitalfte
   WorkingDirectory=/home/digitalfte/Hacathan_2
   Environment="WORK_ZONE=cloud"
   Environment="PYTHONUNBUFFERED=1"
   ExecStart=/home/digitalfte/Hacathan_2/.venv/bin/python src/orchestrator.py

   # Auto-restart configuration
   Restart=always
   RestartSec=10

   # Resource limits
   MemoryLimit=8G
   CPUQuota=200%  # 2 full cores max

   # Logging
   StandardOutput=journal
   StandardError=journal
   SyslogIdentifier=digitalfte-cloud

   [Install]
   WantedBy=multi-user.target
   ```

2. **Reload Systemd:**
   ```bash
   sudo systemctl daemon-reload
   ```

3. **Enable Service (Auto-Start on Boot):**
   ```bash
   sudo systemctl enable digitalfte-cloud.service
   # Expected: Created symlink /etc/systemd/system/multi-user.target.wants/digitalfte-cloud.service
   ```

4. **Start Service:**
   ```bash
   sudo systemctl start digitalfte-cloud.service
   ```

5. **Check Status:**
   ```bash
   sudo systemctl status digitalfte-cloud.service
   # Expected:
   # ● digitalfte-cloud.service - Digital FTE Cloud Agent (Draft Mode)
   #    Loaded: loaded (/etc/systemd/system/digitalfte-cloud.service; enabled)
   #    Active: active (running) since ...
   #    Main PID: ...
   ```

6. **View Logs:**
   ```bash
   # View recent logs
   sudo journalctl -u digitalfte-cloud.service -n 50

   # Follow logs in real-time
   sudo journalctl -u digitalfte-cloud.service -f
   ```

7. **Test Auto-Restart:**
   ```bash
   # Kill the process
   sudo kill -9 $(sudo systemctl show digitalfte-cloud.service -p MainPID --value)

   # Wait 10 seconds
   sleep 10

   # Check if restarted
   sudo systemctl status digitalfte-cloud.service
   # Expected: Active (running), recently started
   ```

8. **Create Monitoring Script:**
   Create `/home/digitalfte/check_agent.sh`:
   ```bash
   #!/bin/bash
   # Check if Cloud Agent is running

   if systemctl is-active --quiet digitalfte-cloud.service; then
       echo "✓ Cloud Agent is running"
       systemctl status digitalfte-cloud.service --no-pager
   else
       echo "✗ Cloud Agent is NOT running"
       journalctl -u digitalfte-cloud.service -n 20 --no-pager
       exit 1
   fi
   ```

   ```bash
   chmod +x /home/digitalfte/check_agent.sh
   ```

**Test Plan:**
```bash
# Test service is enabled
ssh ubuntu@<PUBLIC_IP> 'systemctl is-enabled digitalfte-cloud.service'
# Expected: enabled

# Test service is active
ssh ubuntu@<PUBLIC_IP> 'systemctl is-active digitalfte-cloud.service'
# Expected: active

# Test logs
ssh ubuntu@<PUBLIC_IP> 'sudo journalctl -u digitalfte-cloud.service -n 20'
# Expected: Recent orchestrator logs

# Test auto-restart
ssh ubuntu@<PUBLIC_IP> 'sudo systemctl restart digitalfte-cloud.service && sleep 5 && systemctl is-active digitalfte-cloud.service'
# Expected: active

# Test monitoring script
ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte /home/digitalfte/check_agent.sh'
# Expected: ✓ Cloud Agent is running
```

**Files to Create:**
- `/etc/systemd/system/digitalfte-cloud.service` (on Oracle VM)
- `/home/digitalfte/check_agent.sh` (on Oracle VM)

---

### T-204: Cloud Agent Validation

**Estimated Time:** 1-2 hours
**Priority:** High
**Dependencies:** T-203
**Phase:** 2

**Objective:**
Validate Cloud Agent is running correctly and monitoring Gmail.

**Acceptance Criteria:**
- [ ] Cloud Agent running for >5 minutes without crashes
- [ ] Gmail watcher successfully polls inbox
- [ ] Task files created in Needs_Action/
- [ ] Git push/pull working
- [ ] Audit logs generated
- [ ] Dashboard.md updated

**Implementation Steps:**
1. **Monitor Service Logs:**
   ```bash
   ssh ubuntu@<PUBLIC_IP>
   sudo journalctl -u digitalfte-cloud.service -f
   ```

2. **Send Test Email:**
   - From personal Gmail, send email to monitored inbox
   - Subject: "Test Platinum Cloud Agent"
   - Body: "This is a test email to verify Cloud Agent monitoring."

3. **Verify Task Creation:**
   ```bash
   # Wait 5 minutes (Gmail poll interval)
   # Check Needs_Action folder
   ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte ls -la ~/Hacathan_2/Vault/Needs_Action/'
   # Expected: Test email task file created
   ```

4. **Verify Draft Creation:**
   ```bash
   # Cloud Agent should claim task and create draft
   ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte ls -la ~/Hacathan_2/Vault/Drafts/'
   # Expected: Draft response file created
   ```

5. **Verify Git Push:**
   ```bash
   ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte bash -c "cd ~/Hacathan_2 && git log -1"'
   # Expected: Recent commit with "draft:" prefix
   ```

6. **Verify Audit Log:**
   ```bash
   ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte cat ~/Hacathan_2/Vault/Logs/audit/audit_$(date +%Y-%m-%d).jsonl | tail -5'
   # Expected: TASK_CREATED, TASK_CLAIMED, DRAFT_CREATED events
   ```

7. **Verify Dashboard Update:**
   ```bash
   ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte cat ~/Hacathan_2/Vault/Dashboard.md'
   # Expected: Cloud Agent status, recent activity
   ```

8. **Check Resource Usage:**
   ```bash
   ssh ubuntu@<PUBLIC_IP> 'ps aux | grep orchestrator'
   # Note: CPU and memory usage

   ssh ubuntu@<PUBLIC_IP> 'free -h'
   # Verify memory usage < 8GB
   ```

**Test Plan:**
```bash
# End-to-end test
# 1. Send test email
# 2. Wait 5 minutes
# 3. Check all validation points above
# 4. Verify no errors in logs

# Validation checklist:
# [ ] Service running
# [ ] Gmail watcher active
# [ ] Task created
# [ ] Draft generated
# [ ] Git pushed
# [ ] Audit logged
# [ ] Dashboard updated
# [ ] Resource usage acceptable
```

---

## 4. Phase 3: Work-Zone System (8-12h)

**Objective:** Modify orchestrator to support work-zones and draft creation

**Deliverables:**
- Orchestrator modified for work-zone awareness
- Draft creation for Cloud work-zone
- Execution blocking for sensitive actions
- Local approval workflow

---

### T-301: Orchestrator Work-Zone Integration

**Estimated Time:** 3-4 hours
**Priority:** High
**Dependencies:** T-104
**Phase:** 3

**Objective:**
Modify orchestrator.py to load work-zone config and enforce execution restrictions.

**Acceptance Criteria:**
- [ ] Orchestrator loads WORK_ZONE from environment
- [ ] Work-zone displayed in logs and Dashboard
- [ ] Execution checks work-zone before actions
- [ ] Cloud work-zone creates drafts instead of executing
- [ ] Local work-zone executes normally
- [ ] Unit tests pass

**Implementation Steps:**
1. **Modify `src/orchestrator.py`:**

   **Add imports:**
   ```python
   from src.utils.work_zone import (
       can_execute_action,
       ActionType,
       WorkZone,
       get_current_work_zone,
       log_execution_blocked,
   )
   from src.utils.config import load_config
   ```

   **Load config in `__init__()`:**
   ```python
   class Orchestrator:
       def __init__(self):
           # Load config
           self.config = load_config()
           self.work_zone = self.config["work_zone"]
           self.agent_id = self.config["agent_id"]

           # Log work-zone
           logger.info(f"Orchestrator initialized in {self.work_zone.value} work-zone")
           logger.info(f"Agent ID: {self.agent_id}")

           # ... existing init code
   ```

   **Add work-zone check to action execution:**
   ```python
   def execute_task_action(self, task: Task) -> bool:
       """
       Execute task action with work-zone enforcement.

       Args:
           task: Task to execute

       Returns:
           True if executed, False if blocked or failed
       """
       # Determine action type from task
       action_type = self._get_action_type(task)

       # Check if action allowed in current work-zone
       allowed, reason = can_execute_action(action_type, self.work_zone)

       if not allowed:
           # Execution blocked - create draft instead
           logger.warning(f"Execution blocked: {reason}")
           log_execution_blocked(
               task_id=task.id,
               action=action_type,
               work_zone=self.work_zone,
               agent_id=self.agent_id,
           )

           # Create draft (see T-302)
           self.create_draft(task, action_type, reason)
           return False

       # Execute action normally
       return self._execute_action(task, action_type)

   def _get_action_type(self, task: Task) -> ActionType:
       """Determine action type from task."""
       if "send_email" in task.action.lower():
           return ActionType.SEND_EMAIL
       elif "post" in task.action.lower() and "social" in task.action.lower():
           return ActionType.POST_SOCIAL_MEDIA
       elif "invoice" in task.action.lower():
           return ActionType.CREATE_INVOICE
       elif "expense" in task.action.lower():
           return ActionType.RECORD_EXPENSE
       elif "whatsapp" in task.action.lower():
           return ActionType.SEND_WHATSAPP
       else:
           return ActionType.READ_DATA  # Default safe action
   ```

2. **Update Dashboard to show work-zone:**

   **Modify `update_dashboard()`:**
   ```python
   def update_dashboard(self):
       """Update Dashboard.md with current metrics."""
       dashboard_content = f"""# Digital FTE Health Dashboard

   **Last Updated:** {datetime.now().isoformat()}

   ## Agent Status

   | Agent ID | Type | Work-Zone | Status | Uptime |
   |----------|------|-----------|--------|--------|
   | {self.agent_id} | {self.work_zone.value.upper()} | {self.work_zone.value} | 🟢 HEALTHY | {self._get_uptime()} |

   ## Work-Zone Configuration

   - **Current Work-Zone:** {self.work_zone.value}
   - **Execution Mode:** {"DRAFT ONLY (no actions executed)" if self.work_zone == WorkZone.CLOUD else "FULL EXECUTION (all actions allowed)"}
   - **MCP Servers:** {"Disabled" if self.work_zone == WorkZone.CLOUD else "Enabled"}

   ... (rest of dashboard)
   """

       dashboard_path = self.vault_path / "Dashboard.md"
       dashboard_path.write_text(dashboard_content)
   ```

3. **Update logging to include work-zone:**
   ```python
   # In all log messages, include work-zone context
   logger.info(f"[{self.work_zone.value}] Processing task: {task.id}")
   logger.info(f"[{self.work_zone.value}] Task claimed: {task.id}")
   logger.info(f"[{self.work_zone.value}] Draft created: {task.id}")
   ```

4. **Write unit tests:**
   ```python
   # tests/test_orchestrator_work_zone.py

   import os
   from src.orchestrator import Orchestrator
   from src.utils.work_zone import WorkZone

   def test_cloud_work_zone_blocks_execution(monkeypatch):
       """Cloud work-zone should block sensitive actions."""
       monkeypatch.setenv("WORK_ZONE", "cloud")

       orch = Orchestrator()
       assert orch.work_zone == WorkZone.CLOUD

       # Create test task
       task = create_test_task(action="send_email")

       # Execute should return False (blocked)
       result = orch.execute_task_action(task)
       assert result == False

       # Draft should be created
       drafts = list(orch.vault_path.glob("Drafts/*.md"))
       assert len(drafts) > 0

   def test_local_work_zone_allows_execution(monkeypatch):
       """Local work-zone should allow all actions."""
       monkeypatch.setenv("WORK_ZONE", "local")

       orch = Orchestrator()
       assert orch.work_zone == WorkZone.LOCAL

       # Create test task
       task = create_test_task(action="send_email")

       # Execute should succeed (mocked MCP call)
       result = orch.execute_task_action(task)
       assert result == True
   ```

**Test Plan:**
```bash
# Test cloud work-zone
export WORK_ZONE=cloud
python -c "from src.orchestrator import Orchestrator; o = Orchestrator(); print(o.work_zone)"
# Expected: WorkZone.CLOUD

# Test local work-zone
export WORK_ZONE=local
python -c "from src.orchestrator import Orchestrator; o = Orchestrator(); print(o.work_zone)"
# Expected: WorkZone.LOCAL

# Unit tests
pytest tests/test_orchestrator_work_zone.py -v
```

**Files to Modify:**
- `src/orchestrator.py`

**Files to Create:**
- `tests/test_orchestrator_work_zone.py`

---

### T-302: Draft Creation for Cloud Work-Zone

**Estimated Time:** 3-4 hours
**Priority:** High
**Dependencies:** T-301
**Phase:** 3

**Objective:**
Implement draft creation when Cloud work-zone blocks execution.

**Acceptance Criteria:**
- [ ] Draft file created in `Vault/Drafts/`
- [ ] Draft includes original context and proposed action
- [ ] Draft follows task file schema
- [ ] Draft includes reasoning and confidence
- [ ] Draft marked with `status: draft`
- [ ] Audit log records DRAFT_CREATED event

**Implementation Steps:**
1. **Add draft creation method to Orchestrator:**

   ```python
   def create_draft(
       self,
       task: Task,
       action_type: ActionType,
       blocked_reason: str,
   ):
       """
       Create draft response when execution is blocked.

       Args:
           task: Original task
           action_type: Action that was blocked
           blocked_reason: Why execution was blocked
       """
       logger.info(f"Creating draft for task: {task.id}")

       # Generate draft response using AI
       draft_response = self._generate_draft_response(task)

       # Create draft file
       draft_file = self._create_draft_file(
           task=task,
           action_type=action_type,
           draft_response=draft_response,
           blocked_reason=blocked_reason,
       )

       # Move task to Drafts folder
       self._move_task_to_drafts(task, draft_file)

       # Log draft creation
       log_audit(
           event="DRAFT_CREATED",
           task_id=task.id,
           agent_id=self.agent_id,
           status=AuditStatus.SUCCESS,
           details={
               "action_type": action_type.value,
               "work_zone": self.work_zone.value,
               "draft_file": str(draft_file),
               "ai_agent": self.ai_agent,
           },
       )

       logger.info(f"Draft created: {draft_file.name}")

   def _generate_draft_response(self, task: Task) -> dict:
       """Generate draft response using AI agent."""
       # Construct prompt
       prompt = f"""
       Task: {task.title}

       Original Context:
       {task.content}

       Required Action:
       {task.action}

       Please draft a response or action plan for this task.
       Include:
       1. Proposed response/action
       2. Reasoning for this approach
       3. Confidence level (0-1)
       4. Any risks or considerations
       """

       # Invoke AI agent
       success, response, ai_agent = invoke_agent(prompt)

       if not success:
           # Fallback: Simple template
           response = f"Auto-draft: Respond to {task.title}"
           ai_agent = "fallback-template"

       return {
           "response": response,
           "ai_agent": ai_agent,
           "confidence": 0.8,  # Estimate from AI response
       }

   def _create_draft_file(
       self,
       task: Task,
       action_type: ActionType,
       draft_response: dict,
       blocked_reason: str,
   ) -> Path:
       """Create draft file in Vault/Drafts/."""
       # Generate filename
       timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
       slug = self._create_slug(task.title)
       filename = f"{timestamp}_{task.source}_{task.priority}_{slug}.md"

       draft_path = self.vault_path / "Drafts" / filename

       # Create file content
       content = f"""---
   id: {task.id}
   source: {task.source}
   priority: {task.priority}
   domain: {task.domain}
   status: draft
   created_at: {task.created_at}
   updated_at: {datetime.now().isoformat()}
   claimed_by: {self.agent_id}
   claimed_at: {datetime.now().isoformat()}
   processed_by: null
   processed_at: null
   completed_at: null
   error: null

   # Classification
   complexity: {task.complexity}
   action_type: {action_type.value}
   risk_level: low
   approval_required: true

   # AI Context
   ai_agent: {draft_response["ai_agent"]}
   processing_time: {draft_response.get("processing_time", 0)}
   confidence: {draft_response["confidence"]}

   # Related Files
   related_tasks: []
   plan_file: null
   attachments: []
   ---

   # Task: {task.title}

   ## Original Context

   {task.content}

   ## Proposed Action (DRAFT)

   {draft_response["response"]}

   ## Reasoning

   This is a draft response generated by the Cloud Agent ({self.agent_id}) in draft-only mode.

   **Work-Zone Restriction:**
   {blocked_reason}

   **AI Confidence:** {draft_response["confidence"]:.0%}

   **Next Steps:**
   1. Local Agent will pull this draft via Git sync
   2. Human reviews draft in Obsidian
   3. If approved, Local Agent executes the action
   4. If rejected, draft moves to Dead Letter Queue

   ## Required Approval

   - [ ] Review proposed action
   - [ ] Verify accuracy of information
   - [ ] Approve for execution

   ## Execution Plan

   (To be completed by Local Agent after approval)

   ## Audit Trail

   - **{datetime.now().isoformat()}**: Draft created by Cloud Agent
   - **Blocked Action**: {action_type.value}
   - **Reason**: {blocked_reason}
   """

       # Write file
       draft_path.write_text(content)

       return draft_path

   def _move_task_to_drafts(self, task: Task, draft_file: Path):
       """Move original task file to Drafts (or delete if draft created)."""
       # Option 1: Delete original (draft is comprehensive)
       task_path = self.vault_path / task.folder / f"{task.id}.md"
       if task_path.exists():
           task_path.unlink()

       # Option 2: Move original alongside draft (for reference)
       # shutil.move(task_path, draft_file.parent / f"{task.id}_original.md")
   ```

2. **Write unit tests:**
   ```python
   # tests/test_draft_creation.py

   from src.orchestrator import Orchestrator
   from src.utils.work_zone import WorkZone, ActionType

   def test_create_draft(monkeypatch):
       """Test draft creation in cloud work-zone."""
       monkeypatch.setenv("WORK_ZONE", "cloud")

       orch = Orchestrator()

       # Create test task
       task = create_test_task(
           title="Test Email Response",
           action="send_email",
           content="Original email content",
       )

       # Create draft
       orch.create_draft(
           task=task,
           action_type=ActionType.SEND_EMAIL,
           blocked_reason="Cloud work-zone blocks email sending",
       )

       # Verify draft file created
       drafts = list(orch.vault_path.glob("Drafts/*.md"))
       assert len(drafts) == 1

       # Verify draft content
       draft_content = drafts[0].read_text()
       assert "status: draft" in draft_content
       assert "Test Email Response" in draft_content
       assert "Cloud work-zone blocks email sending" in draft_content
       assert "Required Approval" in draft_content

       # Verify audit log
       audit_log = read_audit_log()
       assert any(e["event"] == "DRAFT_CREATED" for e in audit_log)
   ```

**Test Plan:**
```bash
# Unit tests
pytest tests/test_draft_creation.py -v

# Integration test
export WORK_ZONE=cloud
python src/orchestrator.py &

# Send test email
# Wait for draft creation
ls -la Vault/Drafts/
# Expected: Draft file created

# Verify draft content
cat Vault/Drafts/<draft-file>.md
# Expected: Complete draft with original context and proposed action
```

**Files to Modify:**
- `src/orchestrator.py` (add draft creation methods)

**Files to Create:**
- `tests/test_draft_creation.py`

---

### T-303: Local Agent Approval Workflow

**Estimated Time:** 2-3 hours
**Priority:** High
**Dependencies:** T-302
**Phase:** 3

**Objective:**
Implement Local Agent workflow to pull drafts, display for approval, and execute.

**Acceptance Criteria:**
- [ ] Local Agent scans `Drafts/` folder on each loop
- [ ] Draft displayed in Obsidian (already automatic)
- [ ] Manual approval moves draft to `Approved/`
- [ ] Approved draft triggers execution
- [ ] Completed task moved to `Done/`
- [ ] Git push after each step

**Implementation Steps:**
1. **Add draft processing to Orchestrator main loop:**

   ```python
   def main_loop(self):
       """Main orchestrator loop with work-zone support."""
       logger.info(f"Starting main loop in {self.work_zone.value} work-zone")

       while True:
           try:
               # Git pull (get latest drafts from Cloud)
               self.git_pull()

               # Process based on work-zone
               if self.work_zone == WorkZone.CLOUD:
                   # Cloud: Monitor and draft
                   self.process_cloud_loop()
               else:
                   # Local: Approve and execute
                   self.process_local_loop()

               # Git push (sync changes)
               self.git_push()

               # Sleep before next iteration
               time.sleep(self.loop_interval)

           except KeyboardInterrupt:
               logger.info("Orchestrator stopped by user")
               break
           except Exception as e:
               logger.error(f"Error in main loop: {e}")
               time.sleep(self.error_sleep_interval)

   def process_cloud_loop(self):
       """Cloud work-zone: Monitor and create drafts."""
       # Scan Needs_Action
       tasks = self.scan_needs_action()

       for task in tasks:
           # Try claim
           claimed = self.claim_task(task, "Drafts")
           if claimed:
               # Generate draft
               action_type = self._get_action_type(task)
               allowed, reason = can_execute_action(action_type, self.work_zone)

               if not allowed:
                   self.create_draft(task, action_type, reason)
               else:
                   # Safe action, can process normally
                   self.process_task(task)

   def process_local_loop(self):
       """Local work-zone: Approve and execute."""
       # Process drafts (if any)
       self.process_drafts()

       # Process approved tasks
       self.process_approved_tasks()

       # Process new local tasks
       tasks = self.scan_needs_action()
       for task in tasks:
           self.process_task(task)

   def process_drafts(self):
       """Scan Drafts folder and check for approvals."""
       drafts_path = self.vault_path / "Drafts"

       for draft_file in drafts_path.glob("*.md"):
           # Check if manually approved (moved to Approved/)
           # This happens outside the orchestrator (human in Obsidian)
           # Just log that drafts are available for review
           logger.info(f"Draft available for review: {draft_file.name}")

   def process_approved_tasks(self):
       """Execute approved tasks."""
       approved_path = self.vault_path / "Approved"

       for approved_file in approved_path.glob("*.md"):
           # Load task
           task = self.load_task_from_file(approved_file)

           # Execute action
           logger.info(f"Executing approved task: {task.id}")
           success = self._execute_action(task, self._get_action_type(task))

           if success:
               # Move to Done
               done_path = self.vault_path / "Done" / approved_file.name
               approved_file.rename(done_path)

               log_audit(
                   event="COMPLETED",
                   task_id=task.id,
                   agent_id=self.agent_id,
                   status=AuditStatus.SUCCESS,
                   details={"execution": "approved_and_completed"},
               )

               logger.info(f"Task completed: {task.id}")
           else:
               # Move to DLQ
               dlq_path = self.vault_path / "Dead_Letter_Queue" / approved_file.name
               approved_file.rename(dlq_path)

               logger.error(f"Task failed: {task.id}")
   ```

2. **Add Git pull/push to main loop:**
   ```python
   from src.utils.git_sync import git_pull, git_push

   def git_pull(self):
       """Pull latest changes from remote."""
       result = git_pull()

       if result["success"]:
           logger.info(f"Git pull successful: {result['files_changed']} files changed")
           if result["conflicts"]:
               logger.warning(f"Resolved conflicts: {result['conflicts']}")
       else:
           logger.error(f"Git pull failed: {result['error']}")

   def git_push(self):
       """Push local changes to remote."""
       # Determine folders to push based on work-zone
       if self.work_zone == WorkZone.CLOUD:
           folders = ["Drafts/", "Plans/", "Logs/audit/", "Dashboard.md"]
       else:
           folders = ["Approved/", "Done/", "Pending_Approval/", "Logs/", "Dashboard.md"]

       description = f"sync {len(folders)} folders"
       result = git_push(self.agent_id, description, folders)

       if result["success"]:
           logger.info(f"Git push successful: {result['files_pushed']} files pushed")
       else:
           logger.error(f"Git push failed: {result['error']}")
   ```

3. **Write integration test:**
   ```python
   # tests/test_local_approval_workflow.py

   from src.orchestrator import Orchestrator
   from pathlib import Path

   def test_local_approval_workflow(monkeypatch):
       """Test end-to-end approval workflow."""
       monkeypatch.setenv("WORK_ZONE", "local")

       orch = Orchestrator()

       # Create draft file (simulating Cloud agent)
       draft_file = orch.vault_path / "Drafts" / "test_draft.md"
       draft_file.write_text("""
       ---
       id: test-draft
       action_type: send_email
       status: draft
       ---
       # Test Draft
       Original email: Test
       Proposed response: Test response
       """)

       # Manually approve (move to Approved/)
       approved_file = orch.vault_path / "Approved" / "test_draft.md"
       draft_file.rename(approved_file)

       # Process approved tasks
       orch.process_approved_tasks()

       # Verify moved to Done
       done_file = orch.vault_path / "Done" / "test_draft.md"
       assert done_file.exists()
       assert not approved_file.exists()

       # Verify audit log
       audit_log = read_audit_log()
       assert any(e["event"] == "COMPLETED" for e in audit_log)
   ```

**Test Plan:**
```bash
# Integration test
export WORK_ZONE=local
python src/orchestrator.py &

# Create draft file manually
echo "Test draft" > Vault/Drafts/test.md

# Move to Approved (simulate human approval)
mv Vault/Drafts/test.md Vault/Approved/

# Wait for orchestrator to process
sleep 35

# Verify moved to Done
ls Vault/Done/test.md
# Expected: File exists

# Kill orchestrator
pkill -f orchestrator.py
```

**Files to Modify:**
- `src/orchestrator.py` (add draft processing, Git sync)

**Files to Create:**
- `tests/test_local_approval_workflow.py`

---

## 5. Phase 4: Git Communication (6-10h)

**Objective:** Implement automated Git synchronization and conflict resolution

**Deliverables:**
- Auto-sync loop for both agents
- Conflict resolution strategy
- Dashboard real-time updates

---

### T-401: Auto-Sync Loop Implementation

**Estimated Time:** 2-3 hours
**Priority:** High
**Dependencies:** T-102, T-301
**Phase:** 4

**Objective:**
Integrate Git sync into main orchestrator loop with proper error handling.

**Acceptance Criteria:**
- [ ] Git pull every 30 seconds
- [ ] Git push after processing tasks
- [ ] Sync metrics logged
- [ ] Sync failures trigger retry
- [ ] Dashboard shows last sync time

**Implementation Steps:**
(Already covered in T-303 - Git pull/push integration)

1. **Verify sync interval:**
   ```python
   # In orchestrator.py

   LOOP_INTERVAL = 30  # seconds
   GIT_SYNC_ENABLED = True

   def main_loop(self):
       while True:
           if GIT_SYNC_ENABLED:
               self.git_pull()

           # Process tasks
           self.process_tasks()

           if GIT_SYNC_ENABLED:
               self.git_push()

           time.sleep(LOOP_INTERVAL)
   ```

2. **Add sync metrics:**
   ```python
   class SyncMetrics:
       def __init__(self):
           self.pulls_success = 0
           self.pulls_failed = 0
           self.pushes_success = 0
           self.pushes_failed = 0
           self.last_pull = None
           self.last_push = None
           self.conflicts_resolved = 0

   # In Orchestrator.__init__()
   self.sync_metrics = SyncMetrics()

   # In git_pull()
   if result["success"]:
       self.sync_metrics.pulls_success += 1
       self.sync_metrics.last_pull = datetime.now()
       if result["conflicts"]:
           self.sync_metrics.conflicts_resolved += len(result["conflicts"])
   else:
       self.sync_metrics.pulls_failed += 1

   # In git_push()
   if result["success"]:
       self.sync_metrics.pushes_success += 1
       self.sync_metrics.last_push = datetime.now()
   else:
       self.sync_metrics.pushes_failed += 1
   ```

3. **Update Dashboard with sync status:**
   ```python
   def update_dashboard(self):
       """Update Dashboard with Git sync metrics."""
       dashboard_content = f"""
       ## Git Sync Status

       - **Last Pull:** {self.sync_metrics.last_pull or "Never"}
       - **Last Push:** {self.sync_metrics.last_push or "Never"}
       - **Pull Success Rate:** {self._calc_success_rate(self.sync_metrics.pulls_success, self.sync_metrics.pulls_failed)}
       - **Push Success Rate:** {self._calc_success_rate(self.sync_metrics.pushes_success, self.sync_metrics.pushes_failed)}
       - **Conflicts Resolved (24h):** {self.sync_metrics.conflicts_resolved}
       """
       # ... rest of dashboard
   ```

**Test Plan:**
```bash
# Run both agents with sync enabled
# Cloud Agent
ssh ubuntu@<PUBLIC_IP> 'sudo systemctl start digitalfte-cloud.service'

# Local Agent
export WORK_ZONE=local
python src/orchestrator.py &

# Monitor sync
# Cloud logs
ssh ubuntu@<PUBLIC_IP> 'sudo journalctl -u digitalfte-cloud.service -f | grep "Git"'

# Local logs
tail -f orchestrator.log | grep "Git"

# Verify sync happening every 30s
# Expected: Git pull/push logs every 30s
```

**Files to Modify:**
- `src/orchestrator.py` (already modified in T-303)

---

### T-402: Conflict Resolution Testing

**Estimated Time:** 2-3 hours
**Priority:** Medium
**Dependencies:** T-401
**Phase:** 4

**Objective:**
Test and validate conflict resolution strategy (local always wins).

**Acceptance Criteria:**
- [ ] Simultaneous edits to Dashboard.md resolved correctly
- [ ] Local changes preserved in conflicts
- [ ] Cloud changes merged where no conflict
- [ ] Conflict resolution logged in audit

**Implementation Steps:**
1. **Create conflict simulation script:**
   ```python
   # tests/simulate_conflict.py

   import subprocess
   from pathlib import Path

   def simulate_dashboard_conflict():
       """Simulate concurrent Dashboard.md edits."""

       # Cloud: Edit Dashboard
       cloud_content = """
       # Dashboard

       Cloud Agent: 10 tasks processed
       """

       cloud_dashboard = Path("Vault/Dashboard.md")
       cloud_dashboard.write_text(cloud_content)

       subprocess.run(["git", "add", "Vault/Dashboard.md"])
       subprocess.run(["git", "commit", "-m", "cloud: update dashboard"])
       subprocess.run(["git", "push", "origin", "main"])

       # Local: Edit Dashboard (different content)
       local_content = """
       # Dashboard

       Local Agent: 5 tasks processed
       """

       local_dashboard = Path("Vault/Dashboard.md")
       local_dashboard.write_text(local_content)

       subprocess.run(["git", "add", "Vault/Dashboard.md"])
       subprocess.run(["git", "commit", "-m", "local: update dashboard"])

       # Try to pull (will conflict)
       result = subprocess.run(
           ["git", "pull", "origin", "main", "--rebase"],
           capture_output=True,
           text=True,
       )

       print("Git pull result:")
       print(result.stdout)
       print(result.stderr)

       if "CONFLICT" in result.stdout:
           print("\nConflict detected! Resolving...")

           # Auto-resolve: Local wins
           subprocess.run(["git", "checkout", "--ours", "Vault/Dashboard.md"])
           subprocess.run(["git", "add", "Vault/Dashboard.md"])
           subprocess.run(["git", "rebase", "--continue"])

           print("Conflict resolved: Local changes preserved")

           # Verify local content preserved
           final_content = local_dashboard.read_text()
           assert "Local Agent" in final_content
           print("✓ Local changes preserved")

   if __name__ == "__main__":
       simulate_dashboard_conflict()
   ```

2. **Run conflict simulation:**
   ```bash
   python tests/simulate_conflict.py
   ```

3. **Verify conflict resolution in orchestrator:**
   ```python
   # tests/test_conflict_resolution.py

   from src.utils.git_sync import git_pull

   def test_conflict_resolution():
       """Test that git_pull resolves conflicts with local winning."""

       # Create conflict scenario
       setup_conflict_scenario()

       # Run git_pull
       result = git_pull()

       # Should succeed despite conflict
       assert result["success"] == True

       # Should report conflicts
       assert len(result["conflicts"]) > 0

       # Local content should be preserved
       local_content = Path("Vault/Dashboard.md").read_text()
       assert "Local Agent" in local_content
   ```

**Test Plan:**
```bash
# Automated test
pytest tests/test_conflict_resolution.py -v

# Manual test
# 1. Cloud agent updates Dashboard.md
# 2. Local agent updates Dashboard.md (don't pull first)
# 3. Local agent tries to pull
# 4. Verify local changes preserved
```

**Files to Create:**
- `tests/simulate_conflict.py`
- `tests/test_conflict_resolution.py`

---

### T-403: Dashboard Real-Time Updates

**Estimated Time:** 2-3 hours
**Priority:** Medium
**Dependencies:** T-401
**Phase:** 4

**Objective:**
Enhance Dashboard.md with real-time metrics from both agents.

**Acceptance Criteria:**
- [ ] Dashboard shows Cloud and Local agent status
- [ ] Recent activity from both agents
- [ ] Task queue sizes
- [ ] Sync metrics
- [ ] Health status

**Implementation Steps:**
1. **Create Dashboard template:**

   (Already defined in architecture.md - implement in orchestrator)

   ```python
   # In orchestrator.py

   def update_dashboard(self):
       """Update Dashboard.md with comprehensive metrics."""

       # Collect metrics
       agent_status = self._get_agent_status()
       task_metrics = self._get_task_metrics()
       watcher_status = self._get_watcher_status()
       mcp_status = self._get_mcp_status()
       resource_usage = self._get_resource_usage()
       vault_status = self._get_vault_status()
       git_status = self._get_git_status()
       recent_activity = self._get_recent_activity(limit=10)

       # Render dashboard
       dashboard_content = f"""# Digital FTE Health Dashboard

   **Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
   **Refresh Interval:** 60 seconds

   ---

   ## 📊 Agent Status

   | Agent ID | Type | Status | Uptime | Last Sync |
   |----------|------|--------|--------|-----------|
   | {agent_status["agent_id"]} | {agent_status["type"]} | {agent_status["status"]} | {agent_status["uptime"]} | {agent_status["last_sync"]} |

   ---

   ## 📈 Task Metrics (24h Rolling)

   ### {agent_status["type"]} Agent
   - **Processed:** {task_metrics["processed"]} tasks
   - **Failed:** {task_metrics["failed"]} tasks ({task_metrics["failure_rate"]:.1%} failure rate)
   - **Pending:** {task_metrics["pending"]} tasks
   - **Avg Processing Time:** {task_metrics["avg_time"]:.1f}s

   ---

   ## 👁️ Watchers

   | Watcher | Agent | Status | Last Check | Items (24h) |
   |---------|-------|--------|------------|-------------|
   {self._format_watcher_table(watcher_status)}

   ---

   ## 🔌 MCP Servers

   | Server | Agent | Status | Last Used | Success Rate |
   |--------|-------|--------|-----------|--------------|
   {self._format_mcp_table(mcp_status)}

   ---

   ## 💻 Resource Usage

   ### {agent_status["type"]} Agent
   - **CPU:** {resource_usage["cpu_percent"]:.1f}%
   - **Memory:** {resource_usage["memory_mb"]:.1f} MB / {resource_usage["memory_total_mb"]:.1f} MB ({resource_usage["memory_percent"]:.1f}%)
   - **Disk:** {resource_usage["disk_gb"]:.1f} GB / {resource_usage["disk_total_gb"]:.1f} GB ({resource_usage["disk_percent"]:.1f}%)

   ---

   ## 📁 Vault Status

   | Folder | Tasks | Size |
   |--------|-------|------|
   {self._format_vault_table(vault_status)}

   **Git Status:**
   - Commits behind remote: {git_status["commits_behind"]}
   - Commits ahead of remote: {git_status["commits_ahead"]}
   - Last sync: {git_status["last_sync"]}
   - Sync failures (24h): {git_status["failures_24h"]}

   ---

   ## ⚠️ Alerts & Warnings

   {self._format_alerts()}

   ---

   ## 📋 Recent Activity (Last 10 Events)

   {self._format_recent_activity(recent_activity)}

   ---

   ## 🔍 Debug Info

   - **Agent Version:** 1.0.0-platinum
   - **Python Version:** {platform.python_version()}
   - **Git Version:** {self._get_git_version()}
   - **Last Health Check:** {agent_status["last_health_check"]}
   - **Next Health Check:** {agent_status["next_health_check"]}

   ---

   _This dashboard is auto-updated by both agents and synced via Git._
   """

       # Write dashboard
       dashboard_path = self.vault_path / "Dashboard.md"
       dashboard_path.write_text(dashboard_content)

       logger.info("Dashboard updated")
   ```

2. **Implement metric collection methods:**
   ```python
   def _get_agent_status(self) -> dict:
       """Get current agent status."""
       return {
           "agent_id": self.agent_id,
           "type": "Cloud" if self.work_zone == WorkZone.CLOUD else "Local",
           "status": "🟢 HEALTHY",  # TODO: Compute from health metrics
           "uptime": self._get_uptime_string(),
           "last_sync": self._get_last_sync_time(),
           "last_health_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
           "next_health_check": (datetime.now() + timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S"),
       }

   def _get_task_metrics(self) -> dict:
       """Get task processing metrics for last 24h."""
       # Read audit log for last 24h
       audit_events = self._read_audit_log_24h()

       processed = len([e for e in audit_events if e["event"] == "COMPLETED"])
       failed = len([e for e in audit_events if e["event"] == "FAILED"])
       pending = len(list((self.vault_path / "Drafts").glob("*.md")))

       return {
           "processed": processed,
           "failed": failed,
           "failure_rate": failed / max(processed, 1),
           "pending": pending,
           "avg_time": 4.2,  # TODO: Compute from audit logs
       }

   # ... other metric collection methods
   ```

**Test Plan:**
```bash
# Run orchestrator
python src/orchestrator.py &

# Wait for dashboard update (60s)
sleep 65

# View dashboard
cat Vault/Dashboard.md

# Verify sections present:
# - Agent Status
# - Task Metrics
# - Watchers
# - MCP Servers
# - Resource Usage
# - Vault Status
# - Recent Activity

# Verify updates over time
for i in {1..3}; do
    echo "Check $i:"
    cat Vault/Dashboard.md | grep "Last Updated"
    sleep 65
done
# Expected: Timestamp increments each check
```

**Files to Modify:**
- `src/orchestrator.py` (implement Dashboard update logic)

---

## 6. Phase 5: Testing & Validation (8-11h)

**Objective:** Comprehensive testing of Platinum Tier features

**Deliverables:**
- Unit tests for all new modules
- Integration tests for workflows
- End-to-end demo scenario
- Performance validation

---

### T-501: Unit Test Suite

**Estimated Time:** 3-4 hours
**Priority:** High
**Dependencies:** All Phase 1-4 tasks
**Phase:** 5

**Objective:**
Create comprehensive unit tests for all Platinum Tier utilities.

**Acceptance Criteria:**
- [ ] 90%+ code coverage for new modules
- [ ] All tests pass
- [ ] Tests run in CI/CD (optional)

**Implementation Steps:**
1. **Run existing tests:**
   ```bash
   pytest tests/ -v --cov=src --cov-report=html
   ```

2. **Add missing tests:**
   - `tests/test_config.py` (T-101)
   - `tests/test_git_sync.py` (T-102)
   - `tests/test_claim_by_move.py` (T-103)
   - `tests/test_work_zone.py` (T-104)
   - `tests/test_orchestrator_work_zone.py` (T-301)
   - `tests/test_draft_creation.py` (T-302)
   - `tests/test_local_approval_workflow.py` (T-303)
   - `tests/test_conflict_resolution.py` (T-402)

3. **Fix any failing tests**

4. **Generate coverage report:**
   ```bash
   pytest tests/ --cov=src --cov-report=html
   open htmlcov/index.html
   ```

**Test Plan:**
```bash
# Run all tests
pytest tests/ -v

# Expected: All tests pass
# Expected: Coverage >90%
```

**Files to Create:**
- (Tests already created in previous tasks)

---

### T-502: Integration Test Suite

**Estimated Time:** 3-4 hours
**Priority:** High
**Dependencies:** T-501
**Phase:** 5

**Objective:**
Test end-to-end workflows with both agents.

**Acceptance Criteria:**
- [ ] Email draft & approval workflow test passes
- [ ] Git sync integration test passes
- [ ] Work-zone enforcement test passes
- [ ] Conflict resolution test passes

**Implementation Steps:**
1. **Create integration test file:**
   ```python
   # tests/test_platinum_integration.py

   import subprocess
   import time
   from pathlib import Path

   def test_email_draft_approval_workflow():
       """Test complete workflow: Cloud drafts, Local approves."""

       # 1. Cloud Agent: Create draft
       # (Simulate by manually creating draft file)
       draft_content = """---
   id: test-email-draft
   status: draft
   action_type: send_email
   ---
   # Email Draft
   Original: Test email
   Proposed: Test response
   """
       draft_path = Path("Vault/Drafts/test-email-draft.md")
       draft_path.write_text(draft_content)

       # 2. Cloud Agent: Git push
       subprocess.run(["git", "add", "Vault/Drafts/"])
       subprocess.run(["git", "commit", "-m", "draft: test email"])
       subprocess.run(["git", "push", "origin", "main"])

       # 3. Local Agent: Git pull
       subprocess.run(["git", "pull", "origin", "main"])

       # Verify draft pulled
       assert draft_path.exists()

       # 4. Human: Approve (move to Approved/)
       approved_path = Path("Vault/Approved/test-email-draft.md")
       draft_path.rename(approved_path)

       # 5. Local Agent: Execute
       # (Start orchestrator briefly)
       proc = subprocess.Popen(
           ["python", "src/orchestrator.py"],
           env={"WORK_ZONE": "local"},
       )

       # Wait for processing
       time.sleep(35)

       # Stop orchestrator
       proc.terminate()
       proc.wait()

       # 6. Verify task completed
       done_path = Path("Vault/Done/test-email-draft.md")
       assert done_path.exists()
       assert not approved_path.exists()

       # 7. Verify audit log
       audit_log = read_audit_log()
       assert any(e["event"] == "DRAFT_CREATED" for e in audit_log)
       assert any(e["event"] == "APPROVED" for e in audit_log)
       assert any(e["event"] == "COMPLETED" for e in audit_log)

   def test_git_sync_integration():
       """Test Git sync between Cloud and Local."""

       # Create file on Cloud
       cloud_file = Path("Vault/Drafts/cloud-test.md")
       cloud_file.write_text("Cloud draft")
       subprocess.run(["git", "add", str(cloud_file)])
       subprocess.run(["git", "commit", "-m", "cloud: test"])
       subprocess.run(["git", "push", "origin", "main"])

       # Pull on Local
       result = subprocess.run(
           ["git", "pull", "origin", "main"],
           capture_output=True,
       )
       assert result.returncode == 0

       # Verify file exists locally
       assert cloud_file.exists()

       # Create file on Local
       local_file = Path("Vault/Done/local-test.md")
       local_file.write_text("Local completion")
       subprocess.run(["git", "add", str(local_file)])
       subprocess.run(["git", "commit", "-m", "local: test"])
       subprocess.run(["git", "push", "origin", "main"])

       # Verify pushed to remote
       result = subprocess.run(
           ["git", "log", "-1", "--oneline"],
           capture_output=True,
           text=True,
       )
       assert "local: test" in result.stdout

   def test_work_zone_enforcement():
       """Test that Cloud cannot execute, Local can."""

       # Cloud work-zone
       env_cloud = {"WORK_ZONE": "cloud"}

       # Try to execute action (should create draft)
       # (Would need to mock orchestrator execution)
       # ...implementation details...

       # Local work-zone
       env_local = {"WORK_ZONE": "local"}

       # Try to execute action (should succeed)
       # ...implementation details...
   ```

2. **Run integration tests:**
   ```bash
   pytest tests/test_platinum_integration.py -v -s
   ```

**Test Plan:**
```bash
# Run integration tests
pytest tests/test_platinum_integration.py -v

# Expected: All workflows pass
```

**Files to Create:**
- `tests/test_platinum_integration.py`

---

### T-503: End-to-End Demo Scenario

**Estimated Time:** 2-3 hours
**Priority:** High
**Dependencies:** T-502
**Phase:** 5

**Objective:**
Create demo script for hackathon judges showing offline resilience.

**Acceptance Criteria:**
- [ ] Demo script documented
- [ ] Demo runs successfully start to finish
- [ ] Email sent while Local offline
- [ ] Cloud drafts response
- [ ] Local reviews and sends
- [ ] Complete audit trail

**Implementation Steps:**
1. **Create demo script:**

   (Already defined in spec.md - create executable version)

   Create `docs/PLATINUM_DEMO_SCRIPT.md`:
   ```markdown
   # Platinum Tier Demo Script

   **Duration:** 10 minutes
   **Audience:** Hackathon judges

   ## Setup (Before Demo)

   1. **Verify Cloud Agent Running:**
      ```bash
      ssh ubuntu@<PUBLIC_IP> 'sudo systemctl status digitalfte-cloud.service'
      ```

   2. **Start Local Agent:**
      ```bash
      cd D:\Hacathan_2
      .\Start_Local_Agent.ps1
      ```

   3. **Verify Both Agents Healthy:**
      ```bash
      cat Vault/Dashboard.md
      # Check: Both Cloud and Local agents show "HEALTHY"
      ```

   ## Demo Flow

   ### Step 1: Show Current State (1 min)

   **Narrator:**
   "This is a Digital FTE with dual-agent architecture. Cloud Agent runs 24/7 on Oracle Cloud, Local Agent runs on my laptop."

   **Action:**
   - Open Obsidian vault (Vault/)
   - Show Dashboard.md (both agents running)
   - Show empty Drafts/ folder

   ### Step 2: Simulate User Going Offline (1 min)

   **Narrator:**
   "Now I'm going to simulate going offline - I'll stop my Local Agent and close my laptop."

   **Action:**
   ```bash
   # Stop Local Agent
   pkill -f orchestrator.py

   # Show Dashboard - only Cloud active now
   # (via SSH to Cloud VM)
   ssh ubuntu@<PUBLIC_IP> 'sudo -u digitalfte cat ~/Hacathan_2/Vault/Dashboard.md'
   ```

   ### Step 3: Send Test Email (2 min)

   **Narrator:**
   "While I'm offline, an email arrives to my Gmail inbox."

   **Action:**
   - From test Gmail account, send email:
     - To: monitored-inbox@example.com
     - Subject: "Urgent: Need Q4 Financial Summary"
     - Body: "Can you provide Q4 revenue, expenses, and profit margin by EOD?"

   - Show email in Gmail web UI

   ### Step 4: Cloud Agent Detects and Drafts (3 min)

   **Narrator:**
   "Cloud Agent monitors Gmail 24/7. It detects the email within 5 minutes."

   **Action:**
   - SSH to Cloud VM
     ```bash
     ssh ubuntu@<PUBLIC_IP>
     sudo journalctl -u digitalfte-cloud.service -f
     ```

   - Wait for logs:
     ```
     [cloud] Gmail watcher detected email: Q4 Financial Summary
     [cloud] Created task: Vault/Needs_Action/2026-01-22_1430_gmail_high_Q4-summary.md
     [cloud] Claimed task: moved to Drafts/
     [cloud] Generating draft response...
     [cloud] Draft created: Vault/Drafts/2026-01-22_1430_gmail_high_Q4-summary.md
     [cloud] Git push successful
     ```

   - Show draft file on Cloud VM:
     ```bash
     cat ~/Hacathan_2/Vault/Drafts/2026-01-22_1430_gmail_high_Q4-summary.md
     ```

   **Narrator:**
   "Cloud Agent created a draft response but didn't send it - work-zone restriction prevents execution without human approval."

   ### Step 5: User Returns Online (2 min)

   **Narrator:**
   "Now I'm back online. I start my Local Agent."

   **Action:**
   ```bash
   cd D:\Hacathan_2
   python src/orchestrator.py &

   # Watch logs
   tail -f orchestrator.log
   ```

   - Wait for Git pull:
     ```
     [local] Git pull successful: 1 file changed
     [local] New draft detected: Vault/Drafts/2026-01-22_1430_gmail_high_Q4-summary.md
     ```

   - Open Obsidian
   - Navigate to Drafts/ folder
   - Show draft file

   ### Step 6: Human Review & Approval (1 min)

   **Narrator:**
   "I review the draft in Obsidian. The AI retrieved Q4 data from our Odoo accounting system and drafted a response."

   **Action:**
   - Show draft content in Obsidian:
     ```
     # Task: Email Response - Q4 Financial Summary

     ## Original Email
     From: client@example.com
     Subject: Urgent: Need Q4 Financial Summary

     Can you provide Q4 revenue, expenses, and profit margin by EOD?

     ## Proposed Action (DRAFT)

     Subject: RE: Q4 Financial Summary

     Hi [Client Name],

     Here's the Q4 summary you requested:
     - Revenue: $1,245,000
     - Expenses: $892,000
     - Profit: $353,000
     - Profit Margin: 28.3%

     Full report attached.

     Best regards,
     [Your Name]

     ## Reasoning

     Retrieved financial data from Odoo accounting system.
     Confidence: 95%
     ```

   - **Approve the draft:**
     - In Obsidian: Right-click → Move to → Approved/

   ### Step 7: Local Agent Executes (1 min)

   **Narrator:**
   "Local Agent detects the approval and sends the email."

   **Action:**
   - Watch orchestrator logs:
     ```
     [local] Approved task detected: 2026-01-22_1430_gmail_high_Q4-summary.md
     [local] Executing action: send_email
     [local] Email sent successfully
     [local] Task completed, moved to Done/
     [local] Git push successful
     ```

   - Show sent email in Gmail (recipient inbox)

   - Show task in Done/ folder

   ### Step 8: Verify Audit Trail (1 min)

   **Narrator:**
   "Complete audit trail available for compliance."

   **Action:**
   - Show audit log:
     ```bash
     cat Vault/Logs/audit/audit_2026-01-22.jsonl | grep "Q4-summary" | jq
     ```

   - Expected events:
     ```json
     {"event": "TASK_CREATED", "timestamp": "...", "agent": "cloud"}
     {"event": "TASK_CLAIMED", "timestamp": "...", "agent": "cloud"}
     {"event": "DRAFT_CREATED", "timestamp": "...", "agent": "cloud"}
     {"event": "APPROVED", "timestamp": "...", "agent": "local", "user": "human"}
     {"event": "EXECUTED", "timestamp": "...", "agent": "local", "status": "success"}
     {"event": "COMPLETED", "timestamp": "...", "agent": "local"}
     ```

   ## Summary

   **Narrator:**
   "This demonstrates true 24/7 autonomous operation with human-in-the-loop safety:
   - Cloud Agent monitored email while I was offline
   - Drafted intelligent response using AI
   - Local Agent required human approval before sending
   - Complete audit trail for all operations
   - Zero cost infrastructure (Oracle Free Tier + GitHub)"

   ## Validation Checklist

   - [x] Cloud Agent ran 24/7
   - [x] Email detected while Local offline
   - [x] Draft created autonomously
   - [x] Human approval required
   - [x] Email sent after approval
   - [x] Complete audit trail
   - [x] No secrets exposed to Cloud
   ```

2. **Test demo flow:**
   ```bash
   # Run through demo script manually
   # Record any issues
   # Fix and re-test until perfect
   ```

**Test Plan:**
```bash
# Full demo run-through (10 min)
# Follow script exactly
# Time each step
# Verify all outputs match expected
```

**Files to Create:**
- `docs/PLATINUM_DEMO_SCRIPT.md`

---

## 7. Phase 6: Documentation & Demo (0h - parallel with other phases)

**Objective:** Create deployment and operations documentation

**Deliverables:**
- Deployment guide
- Operations manual
- Security documentation
- Demo script

---

### T-601: Deployment Guide

**Estimated Time:** Already created (specs/platinum/)
**Priority:** Medium
**Dependencies:** Phase 2 complete
**Phase:** 6

**Objective:**
Document step-by-step deployment procedure.

**Files:**
- `docs/PLATINUM_DEPLOYMENT.md` (extract from architecture.md)

**Status:** Content already exists in architecture.md, just needs formatting

---

### T-602: Operations Manual

**Estimated Time:** Already planned
**Priority:** Medium
**Dependencies:** Phase 4 complete
**Phase:** 6

**Objective:**
Document operational procedures and troubleshooting.

**Files:**
- `docs/PLATINUM_OPERATIONS.md`

**Status:** To be created (but low priority - can be done after implementation)

---

### T-603: Security Documentation

**Estimated Time:** Already created
**Priority:** Medium
**Dependencies:** Phase 1 complete
**Phase:** 6

**Objective:**
Document security architecture and controls.

**Files:**
- `docs/PLATINUM_SECURITY.md` (extract from architecture.md)

**Status:** Content already exists in architecture.md

---

## Summary

**Total Tasks:** 21 major tasks
**Total Estimated Time:** 40-60 hours
**Critical Path:**
1. Phase 1 (Foundation) → 2 (Cloud Agent) → 3 (Work-Zone) → 4 (Git Sync) → 5 (Testing)

**Parallel Work Opportunities:**
- T-101, T-102, T-103, T-104 can be done in parallel (Phase 1)
- T-601, T-602, T-603 can be done throughout (Phase 6)

**High-Risk Tasks:**
- T-202: Cloud VM setup (Oracle Cloud complexity)
- T-303: Local approval workflow (integration complexity)
- T-402: Conflict resolution (Git edge cases)
- T-503: End-to-end demo (dependencies on all features)

**Next Steps:**
1. Review and approve this task breakdown
2. Create GitHub issues for each task (optional)
3. Start with Phase 1 (Foundation)
4. Test each task before proceeding to next

---

**Document Version:** 1.0
**Last Updated:** 2026-01-22
**Status:** Ready for Implementation
