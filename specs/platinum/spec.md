# Platinum Tier Feature Specification - Dual-Agent Digital FTE

**Version:** 1.0
**Date:** 2026-01-22
**Status:** Draft
**Author:** Abdullah Junior Development Team
**Tier:** Platinum (Hackathon)

---

## Executive Summary

This specification defines the Platinum Tier upgrade for the Digital FTE system, transforming it from a single local agent into a **dual-agent architecture** with:

- **Cloud Agent**: Always-on, autonomous drafting on 24/7 cloud VM
- **Local Agent**: Human-supervised review and approval on personal machine
- **Git-Based Communication**: File-based task synchronization via Obsidian vault
- **Work-Zone Specialization**: Cloud drafts, Local approves and executes
- **Offline Resilience**: Continues operating when Local is offline

**Primary Goal:** Enable 24/7 autonomous operation with human-in-the-loop approval for critical actions.

---

## 1. Feature Overview

### 1.1 Problem Statement

**Current State (Gold Tier):**
- Single agent running on local machine
- Watchers only active when machine is powered on
- No operation during user's offline hours (sleep, travel)
- All tasks processed on single machine

**Limitations:**
- Email responses delayed until machine powered on
- No 24/7 monitoring capability
- Single point of failure
- Cannot respond to time-sensitive requests

**Desired State (Platinum Tier):**
- Dual-agent system: Cloud (always-on) + Local (approval)
- 24/7 email monitoring and draft responses
- Human approval required before sending
- Resilient to local machine downtime

### 1.2 Success Criteria

**Must Have:**
1. Cloud agent deployed to 24/7 VM (Oracle Cloud Free Tier)
2. Git-based vault synchronization between Cloud and Local
3. Claim-by-move pattern prevents race conditions
4. Cloud agent drafts responses (no execution)
5. Local agent approves and executes (final control)
6. Demo: Email arrives while Local offline → Cloud drafts → Local reviews and sends
7. Secrets never sync to cloud (local only)
8. All operations audited with complete trail

**Should Have:**
1. Systemd service for auto-restart on failure
2. Health monitoring with alerts
3. Conflict resolution strategy
4. Performance: <30s sync latency
5. Cost: $0/month (Oracle Free Tier)

**Could Have:**
1. Multi-cloud deployment (AWS + Oracle backup)
2. Real-time sync (<5s) using webhooks
3. Mobile app for approval workflow
4. Dashboard showing Cloud vs Local activity

**Won't Have (Out of Scope):**
1. Direct agent-to-agent (A2A) communication
2. Centralized database
3. Real-time WebSocket connections
4. Complex distributed consensus

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PLATINUM TIER                            │
│                    Dual-Agent Digital FTE                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐         ┌──────────────────────────┐
│   CLOUD AGENT (24/7)     │         │  LOCAL AGENT (On-Demand) │
│   Oracle Free Tier VM    │         │  User's Machine          │
│   4 CPU, 24GB RAM        │         │  Windows/Mac/Linux       │
├──────────────────────────┤         ├──────────────────────────┤
│                          │         │                          │
│  📊 Perception Layer     │         │  📊 Perception Layer     │
│   ├─ Gmail Watcher       │         │   ├─ Filesystem Watcher  │
│   ├─ WhatsApp (Cloud)    │         │   ├─ LinkedIn Watcher    │
│   └─ LinkedIn (Cloud)    │         │   └─ WhatsApp (Local)    │
│                          │         │                          │
│  🧠 Reasoning Layer      │         │  🧠 Reasoning Layer      │
│   ├─ Orchestrator        │         │   ├─ Orchestrator        │
│   ├─ Domain Classifier   │         │   ├─ Domain Classifier   │
│   └─ Plan Generator      │         │   └─ Plan Generator      │
│                          │         │                          │
│  ⚙️  Work-Zone: DRAFT    │         │  ⚙️  Work-Zone: APPROVE  │
│   - Create drafts        │         │   - Review drafts        │
│   - NO execution         │         │   - Execute approved     │
│   - NO sending emails    │         │   - Send emails          │
│   - NO financial ops     │         │   - Financial operations │
│                          │         │                          │
│  📁 Vault (Git Clone)    │◄────────┤  📁 Vault (Git Origin)   │
│   - Needs_Action/        │  Sync   │   - Needs_Action/        │
│   - Drafts/              │  Every  │   - Drafts/              │
│   - Pending_Approval/    │  30s    │   - Pending_Approval/    │
│   - Approved/            │         │   - Approved/            │
│   - Done/                │         │   - Done/                │
│   - Plans/               │         │   - Plans/               │
│   - DLQ/                 │         │   - DLQ/                 │
│   - Logs/ (audit only)   │         │   - Logs/                │
│   - NO .env (secrets)    │         │   - .env (local only)    │
│                          │         │                          │
│  🔒 Security             │         │  🔒 Security             │
│   - No secrets           │         │   - All secrets here     │
│   - Audit logging only   │         │   - Full permissions     │
│   - Read-only MCP        │         │   - Write MCP servers    │
│                          │         │                          │
└──────────────────────────┘         └──────────────────────────┘
           │                                      │
           │    Git Push/Pull (30s interval)      │
           └──────────────────────────────────────┘
```

### 2.2 Component Specifications

#### 2.2.1 Cloud Agent (Always-On VM)

**Infrastructure:**
- **Platform:** Oracle Cloud Infrastructure (OCI) Always Free Tier
- **Instance Type:** VM.Standard.A1.Flex (Ampere ARM)
- **Resources:** 4 OCPU, 24GB RAM, 200GB Storage (forever free)
- **OS:** Ubuntu 22.04 LTS ARM64
- **Region:** Primary: us-ashburn-1, Backup: us-phoenix-1
- **Network:** Public IP, SSH port 22, HTTPS 443

**Systemd Service Configuration:**
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
ExecStart=/home/digitalfte/.venv/bin/python src/orchestrator.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Work-Zone Rules (DRAFT Mode):**
- ✅ CAN: Watch Gmail, WhatsApp, LinkedIn
- ✅ CAN: Process tasks and create drafts
- ✅ CAN: Generate plans for complex tasks
- ✅ CAN: Move tasks to `Drafts/` folder
- ✅ CAN: Read audit logs (monitoring)
- ✅ CAN: Git pull/push to sync vault
- ❌ CANNOT: Send emails
- ❌ CANNOT: Post to social media
- ❌ CANNOT: Execute financial operations (Odoo)
- ❌ CANNOT: Access secrets (.env file)
- ❌ CANNOT: Move tasks to `Approved/` or `Done/`

**MCP Servers Enabled:**
- None (all disabled or read-only mode)
- Email MCP: Not available (no credentials)
- Odoo MCP: Not available (no credentials)
- Social MCP: Not available (no credentials)

#### 2.2.2 Local Agent (On-Demand)

**Infrastructure:**
- **Platform:** User's personal machine (Windows/Mac/Linux)
- **Resources:** Variable (minimum 8GB RAM, 4 CPU cores)
- **OS:** Windows 11 / macOS / Ubuntu Desktop
- **Startup:** Manual or scheduled (e.g., morning routine)

**Work-Zone Rules (APPROVE Mode):**
- ✅ CAN: Review drafts from Cloud agent
- ✅ CAN: Approve/reject/modify drafts
- ✅ CAN: Execute approved tasks
- ✅ CAN: Send emails (final control)
- ✅ CAN: Post to social media (after approval)
- ✅ CAN: Execute financial operations (Odoo)
- ✅ CAN: Access all secrets (.env file)
- ✅ CAN: Move tasks through full workflow
- ✅ CAN: Git push/pull to sync vault
- ❌ CANNOT: Auto-execute without human review

**MCP Servers Enabled:**
- Email Sender MCP (with credentials)
- Odoo Accounting MCP (with credentials)
- Meta Social MCP (with credentials)
- Twitter/X MCP (with credentials)
- WhatsApp MCP (with credentials)

#### 2.2.3 Git-Based Vault Synchronization

**Repository Structure:**
```
Vault/
├── Needs_Action/           # New incoming tasks
│   ├── INBOX.md
│   └── <task-files>.md
├── Drafts/                 # Cloud-generated drafts
│   └── <draft-files>.md
├── Pending_Approval/       # Requires human review
│   └── <pending-files>.md
├── Approved/               # Approved for execution
│   └── <approved-files>.md
├── Done/                   # Completed tasks
│   └── <done-files>.md
├── Plans/                  # Strategic plans
│   └── <plan-files>.md
├── Dead_Letter_Queue/      # Failed tasks
│   └── <failed-files>.md
├── Logs/                   # Audit trail
│   ├── audit/
│   │   └── audit_<date>.jsonl
│   └── health/
│       └── health_<date>.jsonl
├── Dashboard.md            # Real-time metrics
├── Company_Handbook.md     # Business rules
└── .gitignore              # Exclude secrets
```

**.gitignore Configuration:**
```
# Secrets (NEVER sync to cloud)
.env
.env.local
.env.production
*.key
*.pem
credentials.json
secrets/

# Sensitive data
*.secret
*.password
oauth_tokens/

# Local only
.DS_Store
Thumbs.db
```

**Git Workflow:**

**Cloud Agent (Pusher):**
```bash
# Every 30 seconds
git pull origin main --rebase
# Process tasks, create drafts
git add Drafts/ Logs/audit/ Dashboard.md
git commit -m "draft: Cloud agent processed <task-count> tasks"
git push origin main
```

**Local Agent (Puller & Approver):**
```bash
# Every 30 seconds when online
git pull origin main
# Review drafts, approve tasks
git add Approved/ Done/ Logs/
git commit -m "approve: Local agent approved <task-count> tasks"
git push origin main
```

**Conflict Resolution Strategy:**
1. **No conflicts expected**: Cloud and Local operate on different folders
2. **If conflict occurs**: Local always wins (human authority)
3. **Merge strategy**: Recursive merge with patience
4. **Atomic operations**: Use claim-by-move (see section 2.3)

### 2.3 Claim-by-Move Pattern

**Problem:** Race condition if both agents try to claim same task

**Solution:** Filesystem atomic move operation

**Implementation:**

```python
import os
import time
from pathlib import Path

def claim_task(task_path: Path, agent_id: str, destination_folder: str) -> bool:
    """
    Atomically claim a task by moving it to destination folder.

    Args:
        task_path: Path to task file in Needs_Action/
        agent_id: Unique agent identifier (e.g., "cloud", "local")
        destination_folder: Target folder (e.g., "Drafts", "Pending_Approval")

    Returns:
        True if claim successful, False if already claimed by other agent
    """
    try:
        # Compute destination path
        dest_path = task_path.parent.parent / destination_folder / task_path.name

        # Atomic move (rename) - only succeeds if file exists at source
        # This is atomic on most filesystems (POSIX rename, Windows MoveFile)
        os.rename(task_path, dest_path)

        # Successfully claimed
        print(f"[{agent_id}] Claimed task: {task_path.name} -> {destination_folder}/")
        return True

    except FileNotFoundError:
        # Another agent already moved the file
        print(f"[{agent_id}] Task already claimed by another agent: {task_path.name}")
        return False

    except Exception as e:
        # Unexpected error
        print(f"[{agent_id}] Error claiming task {task_path.name}: {e}")
        return False


def cloud_agent_loop():
    """Cloud agent: Draft mode only"""
    needs_action = Path("Vault/Needs_Action")

    for task_file in needs_action.glob("*.md"):
        # Try to claim task for drafting
        if claim_task(task_file, "cloud", "Drafts"):
            # Process and create draft (no execution)
            draft_response(task_file)


def local_agent_loop():
    """Local agent: Review and approve mode"""
    drafts = Path("Vault/Drafts")

    for draft_file in drafts.glob("*.md"):
        # Try to claim draft for approval
        if claim_task(draft_file, "local", "Pending_Approval"):
            # Review draft with human
            review_and_approve(draft_file)
```

**Guarantees:**
- ✅ **Atomic**: Filesystem rename/move is atomic
- ✅ **No race conditions**: Only one agent can successfully move file
- ✅ **No locks needed**: Filesystem handles concurrency
- ✅ **Works across Git sync**: Git pull/push preserves file locations
- ✅ **Simple**: No distributed coordination required

**Edge Cases:**
1. **File moved during read**: Catch FileNotFoundError, skip gracefully
2. **Git conflict on move**: Local always wins (force push if needed)
3. **Task deleted**: FileNotFoundError caught, skip
4. **Network partition**: Each agent operates on local clone, sync when reconnected

---

## 3. User Stories & Acceptance Criteria

### 3.1 Epic: 24/7 Email Monitoring & Response

**As a user**, I want my Digital FTE to monitor emails 24/7 and draft responses even when my machine is offline, so that I never miss time-sensitive communications.

#### User Story 3.1.1: Cloud Agent Drafts Email Response

**Story:**
```
AS A user
I WANT the Cloud agent to draft email responses while I'm offline
SO THAT responses are ready for my review when I come back online
```

**Acceptance Criteria:**
1. ✅ Cloud agent runs 24/7 on Oracle Cloud VM
2. ✅ Gmail watcher monitors inbox every 5 minutes
3. ✅ When new email arrives, creates task in `Needs_Action/`
4. ✅ Cloud agent claims task using claim-by-move
5. ✅ Generates draft response using AI agent
6. ✅ Saves draft to `Vault/Drafts/<timestamp>-email-response.md`
7. ✅ Draft includes: original email, proposed response, reasoning
8. ✅ Git pushes draft to origin (syncs to Local)
9. ✅ Does NOT send email (execution blocked in cloud work-zone)
10. ✅ Audit log records: DRAFT_CREATED event with timestamp

**Test Scenario:**
```gherkin
Given Cloud agent is running on VM
And Local agent is offline (user's machine powered off)
When New email arrives at 2:00 AM: "Can you send me the Q4 report?"
Then Cloud agent detects email within 5 minutes
And Creates task file: "Vault/Needs_Action/2026-01-22_0200_gmail_high_Q4-report-request.md"
And Claims task by moving to "Vault/Drafts/"
And Generates draft response: "I'll send the Q4 report shortly..."
And Saves draft with original email context
And Git pushes to origin (commit: "draft: email response for Q4 report")
And Does NOT send email (no email credentials on cloud)
And Audit log shows: {"event": "DRAFT_CREATED", "agent": "cloud", "task": "Q4 report", "timestamp": "2026-01-22T02:03:15Z"}
```

#### User Story 3.1.2: Local Agent Reviews and Sends

**Story:**
```
AS A user
I WANT to review cloud-drafted emails and approve them before sending
SO THAT I maintain final control over all communications
```

**Acceptance Criteria:**
1. ✅ Local agent pulls latest drafts from Git when started
2. ✅ Displays drafts in `Vault/Drafts/` folder (Obsidian UI)
3. ✅ User reviews draft email response
4. ✅ User can: Approve / Modify / Reject draft
5. ✅ If approved, Local agent moves draft to `Approved/`
6. ✅ Executes approved action: sends email via Email MCP
7. ✅ Moves completed task to `Done/`
8. ✅ Git pushes result to origin
9. ✅ Audit log records: APPROVED, EXECUTED, COMPLETED events

**Test Scenario:**
```gherkin
Given Cloud agent created draft at 2:03 AM
And Draft is in "Vault/Drafts/2026-01-22_0200_gmail_high_Q4-report-request.md"
When User powers on local machine at 8:00 AM
And Local agent starts and runs git pull
Then Draft file appears in local vault
When User opens draft in Obsidian
And Reviews proposed response
And Approves draft
Then Local agent moves file to "Vault/Approved/"
And Sends email via Email MCP server
And Attaches Q4 report from filesystem
And Moves task to "Vault/Done/"
And Git pushes: "approve: sent email for Q4 report request"
And Audit log shows: {"event": "APPROVED", "agent": "local", "user": "human", "timestamp": "2026-01-22T08:05:00Z"}
And Audit log shows: {"event": "EXECUTED", "action": "send_email", "status": "SUCCESS", "timestamp": "2026-01-22T08:05:02Z"}
```

### 3.2 Epic: Work-Zone Specialization

**As a system administrator**, I want clear separation between Cloud (draft) and Local (execute) work-zones, so that sensitive operations require human approval.

#### User Story 3.2.1: Cloud Agent Enforces Draft-Only Mode

**Story:**
```
AS A system administrator
I WANT the Cloud agent to be restricted to draft-only operations
SO THAT no sensitive actions are executed without human approval
```

**Acceptance Criteria:**
1. ✅ Cloud agent has `WORK_ZONE=cloud` environment variable
2. ✅ Cloud orchestrator checks work-zone before execution
3. ✅ For sensitive operations (email, financial, social), creates draft instead of executing
4. ✅ Draft includes: action type, parameters, reasoning, risk level
5. ✅ Blocks execution with error if attempted: "Execution blocked in cloud work-zone"
6. ✅ No MCP server credentials available on cloud (.env not synced)
7. ✅ Audit log records: EXECUTION_BLOCKED events

**Test Scenario:**
```gherkin
Given Cloud agent receives task: "Send invoice to client@example.com"
And WORK_ZONE=cloud environment variable is set
When Orchestrator attempts to execute send_email MCP tool
Then Execution is blocked with error: "Email sending not allowed in cloud work-zone"
And Draft is created: "Vault/Drafts/2026-01-22_1430_invoice_send.md"
And Draft contains: invoice details, recipient, email body
And Audit log shows: {"event": "EXECUTION_BLOCKED", "reason": "cloud_work_zone", "action": "send_email", "timestamp": "2026-01-22T14:30:00Z"}
```

#### User Story 3.2.2: Local Agent Executes Approved Actions

**Story:**
```
AS A local agent
I WANT to execute approved actions with full MCP server access
SO THAT I can complete tasks after human review
```

**Acceptance Criteria:**
1. ✅ Local agent has `WORK_ZONE=local` environment variable
2. ✅ All MCP servers enabled (Email, Odoo, Social, WhatsApp)
3. ✅ Credentials available from `.env` file (not synced to cloud)
4. ✅ Can execute all approved actions in `Approved/` folder
5. ✅ Audit log records: EXECUTED events with full details

**Test Scenario:**
```gherkin
Given Task in "Vault/Approved/2026-01-22_1430_invoice_send.md"
And WORK_ZONE=local environment variable is set
And Email MCP credentials in .env file
When Local orchestrator processes approved task
Then Email is sent via Email MCP server
And Invoice PDF is attached
And Task moved to "Vault/Done/"
And Audit log shows: {"event": "EXECUTED", "action": "send_email", "status": "SUCCESS", "timestamp": "2026-01-22T16:00:00Z"}
```

### 3.3 Epic: Offline Resilience Demonstration

**As a hackathon judge**, I want to see the system operate while the local machine is offline, so that I can verify 24/7 autonomous capability.

#### User Story 3.3.1: Offline Resilience Demo

**Story:**
```
AS A hackathon judge
I WANT to see the system handle an email while local is offline
SO THAT I can verify true 24/7 autonomous operation
```

**Acceptance Criteria:**
1. ✅ Demo starts with both agents running
2. ✅ Local agent is shut down (simulates user going offline)
3. ✅ Email sent to monitored Gmail account
4. ✅ Cloud agent detects email within 5 minutes
5. ✅ Cloud agent drafts response and pushes to Git
6. ✅ Local agent is restarted (simulates user coming back online)
7. ✅ Local agent pulls draft, displays for review
8. ✅ Judge reviews and approves draft
9. ✅ Local agent sends email
10. ✅ Complete audit trail available for review

**Demo Script:**
```markdown
# Platinum Tier Demo: Offline Resilience

## Setup (5 minutes)
1. Show Cloud agent running on Oracle VM (ssh session)
2. Show Local agent running on laptop
3. Show Obsidian vault synced (Dashboard.md displays both agents)

## Demo Flow (10 minutes)

### Step 1: Simulate User Offline (1 min)
- Stop Local agent on laptop
- Close laptop lid (simulate user leaving)
- Show Dashboard: Only Cloud agent active

### Step 2: Send Test Email (2 min)
- From test Gmail account, send email:
  Subject: "Urgent: Need Q4 Financial Summary"
  Body: "Can you provide Q4 revenue, expenses, and profit margin?"
- Show email in Gmail web UI

### Step 3: Cloud Agent Responds (3 min)
- Switch to Oracle VM ssh session
- Show Cloud agent logs detecting email
- Show draft being created in Vault/Drafts/
- Show Git commit: "draft: financial summary request"
- Show audit log entry: DRAFT_CREATED

### Step 4: User Returns Online (2 min)
- Open laptop, start Local agent
- Show Git pull retrieving draft
- Open draft in Obsidian
- Show draft contents:
  - Original email quoted
  - Proposed response with Q4 numbers from Odoo
  - Reasoning: "Retrieved from Odoo financial reports"

### Step 5: Human Approval & Execution (2 min)
- Judge reviews draft in Obsidian
- Judge approves (moves to Approved/ folder)
- Local agent detects approval
- Sends email via Email MCP
- Shows email sent in Gmail (recipient receives it)
- Shows task in Done/ folder
- Shows audit log: APPROVED, EXECUTED, COMPLETED

## Verification (judge validates)
- ✅ Cloud agent operated while Local offline
- ✅ Draft created autonomously
- ✅ Human approval required before sending
- ✅ Complete audit trail available
- ✅ No secrets exposed to cloud (check .env.example)
```

---

## 4. Technical Specifications

### 4.1 Configuration Schema

#### 4.1.1 Environment Variables

**Cloud Agent (.env.cloud)**
```bash
# Work-Zone Configuration
WORK_ZONE=cloud

# Agent Identity
AGENT_ID=cloud-oracle-001
AGENT_NAME=Cloud Agent (Draft Mode)

# Vault Configuration
VAULT_PATH=/home/digitalfte/Hacathan_2/Vault
GIT_REMOTE=git@github.com:username/digital-fte-vault.git
GIT_SYNC_INTERVAL=30  # seconds

# Watchers (Cloud-enabled only)
GMAIL_ENABLED=true
WHATSAPP_ENABLED=true  # Cloud monitoring
LINKEDIN_ENABLED=true
FILESYSTEM_ENABLED=false  # Local only

# MCP Servers (All disabled on cloud)
EMAIL_MCP_ENABLED=false
ODOO_MCP_ENABLED=false
META_SOCIAL_MCP_ENABLED=false
TWITTER_MCP_ENABLED=false
WHATSAPP_MCP_ENABLED=false

# Logging
LOG_LEVEL=INFO
AUDIT_LOG_PATH=/home/digitalfte/Hacathan_2/Vault/Logs/audit
HEALTH_LOG_PATH=/home/digitalfte/Hacathan_2/Vault/Logs/health

# Resource Limits (Cloud)
MAX_CONCURRENT_TASKS=5
TASK_TIMEOUT=300  # seconds
MEMORY_LIMIT_MB=8192  # 8GB
```

**Local Agent (.env.local)**
```bash
# Work-Zone Configuration
WORK_ZONE=local

# Agent Identity
AGENT_ID=local-laptop-001
AGENT_NAME=Local Agent (Approval Mode)

# Vault Configuration
VAULT_PATH=D:\Hacathan_2\Vault
GIT_REMOTE=git@github.com:username/digital-fte-vault.git
GIT_SYNC_INTERVAL=30  # seconds

# Watchers (Local-enabled)
GMAIL_ENABLED=false  # Cloud handles this
WHATSAPP_ENABLED=true  # Local monitoring
LINKEDIN_ENABLED=false  # Cloud handles this
FILESYSTEM_ENABLED=true  # Local only

# MCP Servers (All enabled on local with credentials)
EMAIL_MCP_ENABLED=true
ODOO_MCP_ENABLED=true
META_SOCIAL_MCP_ENABLED=true
TWITTER_MCP_ENABLED=true
WHATSAPP_MCP_ENABLED=true

# Email MCP Credentials (LOCAL ONLY - NEVER SYNC)
GMAIL_ADDRESS=user@example.com
GMAIL_APP_PASSWORD=xxxx_xxxx_xxxx_xxxx

# Odoo MCP Credentials (LOCAL ONLY - NEVER SYNC)
ODOO_URL=http://localhost:8069
ODOO_DB=digital_fte
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password_2026

# Social Media Credentials (LOCAL ONLY - NEVER SYNC)
META_ACCESS_TOKEN=EAAxxxxxxxxxx
META_PAGE_ID=123456789
INSTAGRAM_ACCOUNT_ID=987654321
TWITTER_API_KEY=xxxxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxxxx
TWITTER_ACCESS_TOKEN=xxxxxxxxxxxx
TWITTER_ACCESS_SECRET=xxxxxxxxxxxx

# Logging
LOG_LEVEL=INFO
AUDIT_LOG_PATH=D:\Hacathan_2\Vault\Logs\audit
HEALTH_LOG_PATH=D:\Hacathan_2\Vault\Logs\health

# Resource Limits (Local)
MAX_CONCURRENT_TASKS=10
TASK_TIMEOUT=600  # seconds
MEMORY_LIMIT_MB=16384  # 16GB
```

#### 4.1.2 Task File Format

**Task File Structure:**
```markdown
---
id: 2026-01-22_0200_gmail_high_Q4-report-request
source: gmail
priority: high
domain: BUSINESS
status: draft
created_at: 2026-01-22T02:00:15Z
updated_at: 2026-01-22T02:03:45Z
claimed_by: cloud-oracle-001
---

# Task: Email Response - Q4 Report Request

## Original Email

**From:** client@example.com
**To:** user@example.com
**Subject:** Can you send me the Q4 report?
**Date:** 2026-01-22 02:00:15

> Hi,
>
> Can you send me the Q4 financial report as soon as possible?
>
> Thanks,
> Client Name

## Proposed Response (DRAFT)

**Subject:** RE: Q4 Financial Report

Hi Client Name,

I'll send you the Q4 financial report shortly. Let me retrieve the latest data from our accounting system.

Best regards,
[Your Name]

## Reasoning

- **Classification:** Business email, high priority
- **Action Required:** Send Q4 financial report
- **Complexity:** Simple (retrieve from Odoo + attach PDF)
- **Risk:** Low (standard business communication)
- **Draft Mode:** Response prepared but NOT sent (requires approval)

## Required Approval

- [ ] Review proposed response
- [ ] Verify Q4 report is ready
- [ ] Attach correct PDF file
- [ ] Approve and send

## Metadata

- **AI Agent:** gemini-2.0-flash
- **Processing Time:** 3.5 seconds
- **Confidence:** 0.95
- **Next Action:** Move to Pending_Approval for human review
```

### 4.2 API Contracts

#### 4.2.1 Orchestrator Work-Zone API

**Check Execution Permission:**
```python
def can_execute_action(action_type: str, work_zone: str) -> tuple[bool, str]:
    """
    Check if action can be executed in current work-zone.

    Args:
        action_type: Type of action (e.g., "send_email", "post_social", "odoo_invoice")
        work_zone: Current work-zone ("cloud" or "local")

    Returns:
        (allowed: bool, reason: str)
    """
    # Define restricted actions per work-zone
    RESTRICTED_ACTIONS = {
        "cloud": [
            "send_email",
            "post_social_media",
            "create_invoice",
            "record_expense",
            "send_whatsapp",
            "execute_financial_transaction",
        ],
        "local": [],  # No restrictions on local
    }

    restricted = RESTRICTED_ACTIONS.get(work_zone, [])

    if action_type in restricted:
        return False, f"Action '{action_type}' not allowed in {work_zone} work-zone"

    return True, "Action allowed"


# Usage in orchestrator
action = "send_email"
work_zone = os.getenv("WORK_ZONE", "local")

allowed, reason = can_execute_action(action, work_zone)
if not allowed:
    # Create draft instead of executing
    create_draft(task, action, reason)
    log_audit(
        event="EXECUTION_BLOCKED",
        reason=reason,
        action=action,
        work_zone=work_zone,
    )
else:
    # Execute action
    execute_action(task, action)
```

#### 4.2.2 Git Sync API

**Sync Vault:**
```python
import subprocess
from pathlib import Path
from datetime import datetime

def sync_vault(vault_path: Path, agent_id: str) -> dict:
    """
    Sync vault with remote Git repository.

    Args:
        vault_path: Path to local vault
        agent_id: Agent identifier for commit messages

    Returns:
        {
            "success": bool,
            "pulled": int,  # number of files pulled
            "pushed": int,  # number of files pushed
            "conflicts": list[str],
            "error": str | None
        }
    """
    result = {
        "success": False,
        "pulled": 0,
        "pushed": 0,
        "conflicts": [],
        "error": None,
    }

    try:
        # Change to vault directory
        os.chdir(vault_path)

        # Pull latest changes
        pull_result = subprocess.run(
            ["git", "pull", "origin", "main", "--rebase"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if pull_result.returncode != 0:
            # Check for conflicts
            if "CONFLICT" in pull_result.stdout:
                # Extract conflict files
                conflicts = extract_conflicts(pull_result.stdout)
                result["conflicts"] = conflicts

                # Auto-resolve: Local always wins
                for conflict_file in conflicts:
                    subprocess.run(["git", "checkout", "--ours", conflict_file])

                subprocess.run(["git", "add", "."])
                subprocess.run(["git", "rebase", "--continue"])
            else:
                result["error"] = f"Git pull failed: {pull_result.stderr}"
                return result

        result["pulled"] = count_changed_files(pull_result.stdout)

        # Stage changes
        subprocess.run(["git", "add", "Drafts/", "Approved/", "Done/", "Logs/", "Dashboard.md"])

        # Check if there are changes to commit
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
        )

        if status.stdout.strip():
            # Commit changes
            timestamp = datetime.now().isoformat()
            commit_msg = f"sync: {agent_id} - {timestamp}"

            subprocess.run(["git", "commit", "-m", commit_msg])

            # Push changes
            push_result = subprocess.run(
                ["git", "push", "origin", "main"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if push_result.returncode != 0:
                result["error"] = f"Git push failed: {push_result.stderr}"
                return result

            result["pushed"] = count_committed_files()

        result["success"] = True

    except subprocess.TimeoutExpired:
        result["error"] = "Git operation timed out"
    except Exception as e:
        result["error"] = f"Sync error: {str(e)}"

    return result
```

#### 4.2.3 Health Monitoring API

**Health Check:**
```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthReport:
    agent_id: str
    status: HealthStatus
    timestamp: datetime
    uptime_seconds: int
    tasks_processed: int
    tasks_failed: int
    git_sync_status: str
    watchers_active: list[str]
    mcp_servers_active: list[str]
    memory_usage_mb: float
    cpu_usage_percent: float
    disk_usage_percent: float
    last_error: str | None

def health_check(agent_id: str) -> HealthReport:
    """
    Perform comprehensive health check.

    Returns:
        HealthReport with current system status
    """
    # Collect metrics
    uptime = get_uptime()
    tasks = get_task_metrics()
    git_status = get_git_status()
    watchers = get_active_watchers()
    mcps = get_active_mcp_servers()
    resources = get_resource_usage()
    last_error = get_last_error()

    # Determine overall health
    if last_error and (datetime.now() - last_error["timestamp"]).seconds < 300:
        status = HealthStatus.UNHEALTHY
    elif tasks["failed"] / max(tasks["processed"], 1) > 0.1:
        status = HealthStatus.DEGRADED
    elif git_status != "synced":
        status = HealthStatus.DEGRADED
    else:
        status = HealthStatus.HEALTHY

    return HealthReport(
        agent_id=agent_id,
        status=status,
        timestamp=datetime.now(),
        uptime_seconds=uptime,
        tasks_processed=tasks["processed"],
        tasks_failed=tasks["failed"],
        git_sync_status=git_status,
        watchers_active=watchers,
        mcp_servers_active=mcps,
        memory_usage_mb=resources["memory_mb"],
        cpu_usage_percent=resources["cpu_percent"],
        disk_usage_percent=resources["disk_percent"],
        last_error=last_error,
    )
```

---

## 5. Non-Functional Requirements

### 5.1 Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Git Sync Latency** | < 30s (p95) | Time from file change to Git push complete |
| **Task Claim Latency** | < 1s (p95) | Time to claim task using claim-by-move |
| **Draft Generation** | < 60s (p95) | Time to generate draft response for email |
| **Approval Workflow** | < 5s (p95) | Time from approval to execution start |
| **Vault Sync (Full)** | < 120s | Full vault pull/push cycle |
| **Watcher Poll Interval** | 30s - 300s | Configurable per watcher |
| **Orchestrator Loop** | 30s | Main task processing loop |

### 5.2 Reliability Requirements

| Metric | Target | SLO |
|--------|--------|-----|
| **Cloud Agent Uptime** | 99.5% | Monthly uptime |
| **Git Sync Success Rate** | 99% | Successful syncs / total attempts |
| **Task Processing Success** | 95% | Tasks completed / total tasks |
| **Error Recovery Rate** | 90% | Recovered errors / total errors |
| **Data Durability** | 100% | No task data loss |

**Failure Modes & Recovery:**

1. **Cloud Agent Crash**
   - Detection: Systemd monitors process
   - Recovery: Auto-restart within 10 seconds
   - Impact: Max 10s downtime, no data loss

2. **Git Sync Failure**
   - Detection: Git command returns non-zero
   - Recovery: Retry with exponential backoff (3 attempts)
   - Impact: Max 90s delay, tasks queued locally

3. **Network Partition**
   - Detection: Git remote unreachable
   - Recovery: Continue processing locally, sync when reconnected
   - Impact: Delayed sync, no operational impact

4. **Disk Full**
   - Detection: df shows >95% usage
   - Recovery: Alert admin, pause new tasks
   - Impact: New tasks delayed until space freed

### 5.3 Security Requirements

**Authentication:**
- ✅ SSH key-based Git authentication (no passwords)
- ✅ MCP server credentials only on Local agent
- ✅ No credentials in environment variables on Cloud
- ✅ Audit logging for all sensitive operations

**Authorization:**
- ✅ Work-zone enforcement (Cloud cannot execute, only draft)
- ✅ Human approval required for all sensitive actions
- ✅ Secrets never synced to Cloud (.gitignore enforcement)

**Data Protection:**
- ✅ Secrets stored in .env (local only, never committed)
- ✅ Audit logs contain no sensitive data (sanitized)
- ✅ Task files may contain sensitive data (encrypted at rest via Git)

**Audit Trail:**
- ✅ All operations logged with timestamp, agent ID, action
- ✅ Immutable append-only audit log (JSONL format)
- ✅ Retention: 90 days minimum

### 5.4 Cost Requirements

**Oracle Cloud Always Free Tier:**
- VM.Standard.A1.Flex: 4 OCPU, 24GB RAM - **$0/month**
- Block Storage: 200GB - **$0/month**
- Network: 10TB/month egress - **$0/month**

**GitHub:**
- Private repository: **$0/month** (free tier)
- Git LFS: 1GB included - **$0/month**

**Total Cost:** **$0/month** (all within free tiers)

---

## 6. Deployment Architecture

### 6.1 Cloud VM Setup (Oracle Cloud)

**Provisioning Steps:**

1. **Create VM Instance:**
```bash
# Via OCI Console or CLI
oci compute instance launch \
  --availability-domain "AD-1" \
  --compartment-id "ocid1.compartment..." \
  --shape "VM.Standard.A1.Flex" \
  --shape-config '{"ocpus":4,"memoryInGBs":24}' \
  --image-id "ocid1.image..." \  # Ubuntu 22.04 ARM64
  --subnet-id "ocid1.subnet..." \
  --assign-public-ip true \
  --ssh-authorized-keys-file ~/.ssh/id_rsa.pub
```

2. **Configure Firewall:**
```bash
# Allow SSH (port 22)
oci network security-list update --security-list-id "ocid1.securitylist..." \
  --ingress-security-rules '[{"protocol":"6","source":"0.0.0.0/0","tcpOptions":{"destinationPortRange":{"min":22,"max":22}}}]'
```

3. **Install Dependencies:**
```bash
# SSH into VM
ssh ubuntu@<public-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.14
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.14 python3.14-venv python3.14-dev -y

# Install Git
sudo apt install git -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev -y
```

4. **Clone Repository:**
```bash
# Create user
sudo useradd -m -s /bin/bash digitalfte
sudo -u digitalfte -i

# Generate SSH key
ssh-keygen -t ed25519 -C "cloud-agent@digitalfte"

# Add public key to GitHub: cat ~/.ssh/id_ed25519.pub
# Add as deploy key with read/write access

# Clone repository
git clone git@github.com:username/digital-fte-vault.git ~/Hacathan_2
cd ~/Hacathan_2

# Create virtual environment
python3.14 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

5. **Configure Environment:**
```bash
# Copy cloud environment template
cp config/.env.cloud.example .env

# Edit configuration
nano .env
# Set WORK_ZONE=cloud
# Set AGENT_ID=cloud-oracle-001
# Disable all MCP servers
# Configure watchers (Gmail, WhatsApp, LinkedIn)
```

6. **Setup Systemd Service:**
```bash
# Create service file
sudo nano /etc/systemd/system/digitalfte-cloud.service

# Paste service configuration (see section 2.2.1)

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable digitalfte-cloud.service

# Start service
sudo systemctl start digitalfte-cloud.service

# Check status
sudo systemctl status digitalfte-cloud.service

# View logs
sudo journalctl -u digitalfte-cloud.service -f
```

### 6.2 Local Machine Setup

**Installation Steps:**

1. **Clone Repository:**
```powershell
# Windows PowerShell
cd D:\
git clone git@github.com:username/digital-fte-vault.git Hacathan_2
cd Hacathan_2

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

2. **Configure Environment:**
```powershell
# Copy local environment template
copy config\.env.local.example .env

# Edit configuration
notepad .env
# Set WORK_ZONE=local
# Set AGENT_ID=local-laptop-001
# Enable all MCP servers
# Add all credentials (Gmail, Odoo, Social Media)
```

3. **Setup Startup Script:**
```powershell
# Create startup script
notepad Start_Local_Agent.ps1

# Paste:
# .\Launch_Abdullah_Junior.ps1
# python src\orchestrator.py

# Test startup
.\Start_Local_Agent.ps1
```

### 6.3 Monitoring & Alerting

**Health Dashboard (Dashboard.md):**
```markdown
# Digital FTE Health Dashboard

**Last Updated:** 2026-01-22 14:35:00

## Agent Status

| Agent | Status | Uptime | Tasks (24h) | Last Sync |
|-------|--------|--------|-------------|-----------|
| Cloud (Oracle) | 🟢 HEALTHY | 15d 8h | 142 processed, 3 failed | 14:34:45 |
| Local (Laptop) | 🟢 HEALTHY | 8h 12m | 37 processed, 0 failed | 14:34:50 |

## Watchers

| Watcher | Agent | Status | Last Check | Items |
|---------|-------|--------|------------|-------|
| Gmail | Cloud | 🟢 Active | 14:30:00 | 3 new emails |
| WhatsApp | Cloud | 🟢 Active | 14:32:00 | 0 new messages |
| LinkedIn | Cloud | 🟢 Active | 14:25:00 | 1 new connection |
| Filesystem | Local | 🟢 Active | 14:34:00 | 0 new files |

## MCP Servers

| Server | Agent | Status | Last Used |
|--------|-------|--------|-----------|
| Email Sender | Local | 🟢 Ready | 13:45:00 |
| Odoo Accounting | Local | 🟢 Ready | Never |
| Meta Social | Local | 🟢 Ready | Yesterday |
| Twitter/X | Local | 🟢 Ready | 2 days ago |
| WhatsApp | Local | 🟢 Ready | 14:00:00 |

## Task Queue

- **Needs_Action:** 0 tasks
- **Drafts:** 3 tasks (awaiting review)
- **Pending_Approval:** 0 tasks
- **Approved:** 0 tasks
- **Done (24h):** 52 tasks

## Recent Activity

- `14:34:50` [Local] Approved and sent email: "Q4 Financial Summary"
- `14:30:15` [Cloud] Created draft: "LinkedIn connection request response"
- `14:15:00` [Cloud] Created draft: "WhatsApp business inquiry"
- `13:45:23` [Local] Sent email: "Invoice for Project XYZ"
- `13:12:45` [Cloud] Git sync completed (3 files pulled, 2 files pushed)

## Alerts

- ⚠️ No alerts at this time
```

**Alerting Configuration:**
```python
# src/utils/alerting.py

ALERT_RULES = {
    "agent_down": {
        "condition": "uptime == 0 for 60 seconds",
        "severity": "critical",
        "action": "email_admin",
    },
    "high_failure_rate": {
        "condition": "failed_tasks / total_tasks > 0.2 over 1 hour",
        "severity": "warning",
        "action": "email_admin",
    },
    "git_sync_failed": {
        "condition": "sync_failures >= 3 consecutive",
        "severity": "warning",
        "action": "slack_notification",
    },
    "disk_full": {
        "condition": "disk_usage > 95%",
        "severity": "critical",
        "action": "email_admin + pause_tasks",
    },
}
```

---

## 7. Risk Analysis & Mitigation

### 7.1 Technical Risks

**Risk 1: Git Merge Conflicts**
- **Likelihood:** Medium
- **Impact:** Low
- **Mitigation:**
  - Separate folder operations (Cloud → Drafts, Local → Approved/Done)
  - Conflict resolution: Local always wins
  - Test with concurrent operations before deployment

**Risk 2: Oracle Cloud Free Tier Revocation**
- **Likelihood:** Low
- **Impact:** High
- **Mitigation:**
  - Document backup deployment to AWS Free Tier (t2.micro)
  - Monthly check of Oracle Cloud account status
  - Keep cloud agent code portable (Docker container)

**Risk 3: Network Partition (Cloud-Local)**
- **Likelihood:** Medium
- **Impact:** Low
- **Mitigation:**
  - Both agents operate autonomously during partition
  - Sync resumes automatically when connection restored
  - Test with simulated network failures

**Risk 4: Secrets Accidentally Synced to Cloud**
- **Likelihood:** Low
- **Impact:** Critical
- **Mitigation:**
  - .gitignore configured to exclude .env
  - Pre-commit hook validates no secrets in commits
  - Regular audit of Git history for leaked credentials

**Risk 5: Task Double-Processing**
- **Likelihood:** Low
- **Impact:** Medium
- **Mitigation:**
  - Claim-by-move pattern (atomic filesystem operation)
  - Task ID in filename prevents duplicates
  - Audit log detects double-processing attempts

### 7.2 Operational Risks

**Risk 6: Cloud Agent Consumes Excessive Resources**
- **Likelihood:** Low
- **Impact:** Medium
- **Mitigation:**
  - Resource limits in systemd service (8GB RAM cap)
  - Monitoring with alerts at 80% threshold
  - Automatic task throttling if resources exceeded

**Risk 7: Human Forgets to Approve Drafts**
- **Likelihood:** High
- **Impact:** Low
- **Mitigation:**
  - Obsidian notification badge shows pending drafts
  - Daily summary email with draft count
  - Mobile app (future) for on-the-go approvals

---

## 8. Testing Strategy

### 8.1 Unit Tests

**Components to Test:**
1. Claim-by-move function (race condition tests)
2. Work-zone enforcement (execution blocking)
3. Git sync function (pull/push/conflict resolution)
4. Health check function (status determination)
5. Task file parsing (YAML frontmatter + Markdown)

**Test File:** `tests/test_platinum_tier.py`

### 8.2 Integration Tests

**Scenarios:**
1. End-to-end: Email → Cloud Draft → Local Approval → Send
2. Concurrent task claiming (race condition)
3. Git conflict resolution (Cloud vs Local)
4. Network partition recovery
5. Agent failure and restart

### 8.3 Acceptance Tests

**Demo Scenario (see User Story 3.3.1):**
- Pre-conditions: Both agents running
- Action: Send test email while Local offline
- Expected: Cloud drafts, Local approves and sends
- Validation: Complete audit trail, email received

---

## 9. Documentation Requirements

**Required Documentation:**

1. **Deployment Guide** (`docs/PLATINUM_DEPLOYMENT.md`)
   - Oracle Cloud VM setup
   - Local agent setup
   - Git repository configuration
   - Systemd service installation

2. **Operations Manual** (`docs/PLATINUM_OPERATIONS.md`)
   - Starting/stopping agents
   - Monitoring health dashboard
   - Troubleshooting common issues
   - Backup and recovery procedures

3. **Security Guide** (`docs/PLATINUM_SECURITY.md`)
   - Secrets management
   - Git access control
   - Audit log review
   - Incident response

4. **Demo Script** (`docs/PLATINUM_DEMO.md`)
   - Setup steps
   - Execution flow
   - Expected outcomes
   - Judge validation checklist

---

## 10. Success Metrics

**Platinum Tier Validation Criteria:**

| Requirement | Validation Method | Target |
|-------------|-------------------|--------|
| **24/7 Cloud Agent** | systemctl status shows 99.5% uptime | ✅ Pass |
| **Git Vault Sync** | Git log shows commits from both agents | ✅ Pass |
| **Claim-by-Move** | Race condition test shows no double-processing | ✅ Pass |
| **Work-Zone Enforce** | Cloud cannot send email (blocked with error) | ✅ Pass |
| **Secrets Security** | Git history has no .env file | ✅ Pass |
| **Offline Resilience** | Demo succeeds: Email while Local offline | ✅ Pass |
| **Audit Trail** | Complete log of all operations with timestamps | ✅ Pass |

**Automated Test Suite:**
- 60+ tests covering all Platinum requirements
- 95% pass rate minimum
- Continuous integration with GitHub Actions

---

## Appendix A: File Locations

```
D:\Hacathan_2\
├── specs\
│   └── platinum\
│       ├── research.md          # This research doc
│       ├── spec.md              # This specification
│       ├── architecture.md      # (To be created)
│       ├── tasks.md             # (To be created)
│       ├── security.md          # (To be created)
│       └── operations.md        # (To be created)
├── src\
│   ├── orchestrator.py          # (To be modified for work-zones)
│   ├── utils\
│   │   ├── git_sync.py          # (To be created)
│   │   └── claim_by_move.py     # (To be created)
│   └── config\
│       ├── .env.cloud.example   # (To be created)
│       └── .env.local.example   # (To be created)
├── tests\
│   └── test_platinum_tier.py    # (To be created)
├── docs\
│   ├── PLATINUM_DEPLOYMENT.md   # (To be created)
│   ├── PLATINUM_OPERATIONS.md   # (To be created)
│   ├── PLATINUM_SECURITY.md     # (To be created)
│   └── PLATINUM_DEMO.md         # (To be created)
└── Vault\
    ├── Drafts\                  # (To be created)
    └── .gitignore               # (To be updated)
```

---

**Specification Status:** ✅ COMPLETE - Ready for Architecture & Tasks

**Next Steps:**
1. Create architecture.md (system architecture diagrams)
2. Create tasks.md (implementation breakdown)
3. Create security.md (threat model & controls)
4. Create operations.md (runbooks & procedures)

**Estimated Implementation Time:** 40-60 hours
**Target Completion:** 2026-01-29 (7 days)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-22
**Status:** Draft - Awaiting Review
