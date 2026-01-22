# Platinum Tier Architecture Plan - Digital FTE

**Version:** 1.0
**Date:** 2026-01-22
**Status:** Draft
**Author:** Abdullah Junior Development Team
**Phase:** Platinum Tier Implementation

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Component Architecture](#2-component-architecture)
3. [Data Architecture](#3-data-architecture)
4. [Communication Architecture](#4-communication-architecture)
5. [Security Architecture](#5-security-architecture)
6. [Deployment Architecture](#6-deployment-architecture)
7. [Monitoring Architecture](#7-monitoring-architecture)
8. [Architectural Decision Records](#8-architectural-decision-records)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL SYSTEMS & USERS                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
         Gmail API              LinkedIn API            WhatsApp API
              │                       │                       │
              │                       │                       │
┌─────────────┴───────────────────────┴───────────────────────┴───────────────┐
│                       PLATINUM TIER DIGITAL FTE                              │
│                    (Dual-Agent Distributed System)                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────┐         ┌────────────────────────────┐     │
│  │   CLOUD AGENT              │         │   LOCAL AGENT              │     │
│  │   (Oracle Cloud VM)        │◄────────┤   (User's Machine)         │     │
│  │                            │  Git    │                            │     │
│  │   - 24/7 Monitoring        │  Sync   │   - Human Approval         │     │
│  │   - Draft Responses        │         │   - Final Execution        │     │
│  │   - No Credentials         │         │   - All Credentials        │     │
│  └────────────────────────────┘         └────────────────────────────┘     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
     Odoo Community              Meta Graph API        Twitter API v2
     (Local Docker)              (Social Media)         (Social Media)
              │                       │                       │
┌─────────────┴───────────────────────┴───────────────────────┴───────────────┐
│                          ACTION SYSTEMS                                      │
│                    (MCP Server Integrations)                                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Architectural Principles

**P1: Simplicity Over Complexity**
- Use file-based communication (Git) instead of distributed database
- Leverage filesystem atomic operations (claim-by-move)
- No microservices, no message queues, no complex orchestration

**P2: Security by Design**
- Secrets never leave local machine (no cloud credentials)
- Human-in-the-loop for all sensitive operations
- Immutable audit trail for all actions

**P3: Resilience Through Decoupling**
- Cloud and Local agents operate independently
- Graceful degradation when one agent is offline
- No single point of failure (except Git remote)

**P4: Cost Optimization**
- 100% free infrastructure (Oracle Free Tier + GitHub)
- Minimal compute footprint (efficient Python)
- No paid services or APIs

**P5: Developer Experience**
- Simple deployment (systemd + PowerShell scripts)
- Obsidian UI for task management (no custom frontend)
- Standard tools (Git, Python, Docker)

---

## 2. Component Architecture

### 2.1 Cloud Agent Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    CLOUD AGENT (Draft Mode)                     │
│               Oracle Cloud VM - Always Running                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  PERCEPTION LAYER                         │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │  │
│  │  │   Gmail     │  │  WhatsApp   │  │  LinkedIn   │      │  │
│  │  │   Watcher   │  │   Watcher   │  │   Watcher   │      │  │
│  │  │             │  │             │  │             │      │  │
│  │  │ Poll: 5min  │  │ Poll: 2min  │  │ Poll: 10min │      │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │  │
│  │         │                │                │              │  │
│  │         └────────────────┼────────────────┘              │  │
│  │                          │                               │  │
│  │                    Create Tasks                          │  │
│  │                          │                               │  │
│  │                          ▼                               │  │
│  │              Vault/Needs_Action/*.md                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                  │
│  ┌──────────────────────────┼────────────────────────────────┐│
│  │              REASONING LAYER (Orchestrator)               ││
│  ├──────────────────────────────────────────────────────────┤│
│  │                                                           ││
│  │  Main Loop (30s interval):                               ││
│  │                                                           ││
│  │  1. Scan Vault/Needs_Action/ for tasks                   ││
│  │  2. For each task:                                       ││
│  │     a. Claim task (claim_by_move)                        ││
│  │     b. Classify domain (PERSONAL/BUSINESS)               ││
│  │     c. Detect complexity (simple/complex)                ││
│  │     d. Check work-zone permissions                       ││
│  │     e. Generate draft response (AI agent)                ││
│  │     f. Save draft to Vault/Drafts/                       ││
│  │  3. Git sync (push drafts)                               ││
│  │                                                           ││
│  │  Components:                                             ││
│  │  ┌────────────┐ ┌──────────────┐ ┌─────────────┐        ││
│  │  │ Task       │ │ Domain       │ │ Complexity  │        ││
│  │  │ Claimer    │ │ Classifier   │ │ Detector    │        ││
│  │  └────────────┘ └──────────────┘ └─────────────┘        ││
│  │  ┌────────────┐ ┌──────────────┐ ┌─────────────┐        ││
│  │  │ Work-Zone  │ │ Plan         │ │ AI Agent    │        ││
│  │  │ Enforcer   │ │ Generator    │ │ Invoker     │        ││
│  │  └────────────┘ └──────────────┘ └─────────────┘        ││
│  │                                                           ││
│  └───────────────────────────────────────────────────────────┘│
│                             │                                  │
│  ┌──────────────────────────┼────────────────────────────────┐│
│  │                 ACTION LAYER (Blocked)                    ││
│  ├──────────────────────────────────────────────────────────┤│
│  │                                                           ││
│  │  ❌ MCP Servers: ALL DISABLED                            ││
│  │     - No email sending                                   ││
│  │     - No financial operations                            ││
│  │     - No social media posting                            ││
│  │                                                           ││
│  │  Work-Zone Enforcement:                                  ││
│  │  - can_execute_action() always returns False             ││
│  │  - Creates draft instead of executing                    ││
│  │  - Logs EXECUTION_BLOCKED events                         ││
│  │                                                           ││
│  └───────────────────────────────────────────────────────────┘│
│                             │                                  │
│  ┌──────────────────────────┼────────────────────────────────┐│
│  │                STORAGE LAYER (Git Vault)                  ││
│  ├──────────────────────────────────────────────────────────┤│
│  │                                                           ││
│  │  Vault/ (Git clone of origin)                            ││
│  │  ├── Needs_Action/   (Read: tasks from watchers)         ││
│  │  ├── Drafts/         (Write: generated drafts)           ││
│  │  ├── Plans/          (Write: complex task plans)         ││
│  │  ├── Logs/audit/     (Write: audit events)               ││
│  │  └── Dashboard.md    (Write: health metrics)             ││
│  │                                                           ││
│  │  Git Operations (every 30s):                             ││
│  │  - git pull origin main --rebase                         ││
│  │  - git add Drafts/ Plans/ Logs/ Dashboard.md             ││
│  │  - git commit -m "draft: <description>"                  ││
│  │  - git push origin main                                  ││
│  │                                                           ││
│  └───────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           INFRASTRUCTURE LAYER                           │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  Systemd Service:                                       │   │
│  │  - Auto-start on boot                                   │   │
│  │  - Auto-restart on crash (10s delay)                    │   │
│  │  - Resource limits (8GB RAM, 2 CPU)                     │   │
│  │  - Journal logging (stdout/stderr)                      │   │
│  │                                                          │   │
│  │  Health Monitoring:                                     │   │
│  │  - Uptime tracking                                      │   │
│  │  - Resource usage (CPU, RAM, disk)                      │   │
│  │  - Task metrics (processed, failed)                     │   │
│  │  - Git sync status                                      │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Local Agent Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                   LOCAL AGENT (Approval Mode)                   │
│              User's Machine - On-Demand Operation               │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  PERCEPTION LAYER                         │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  ┌─────────────┐  ┌─────────────┐                        │  │
│  │  │ Filesystem  │  │  WhatsApp   │                        │  │
│  │  │  Watcher    │  │  Watcher    │                        │  │
│  │  │             │  │  (Local)    │                        │  │
│  │  │ Poll: 1min  │  │ Poll: 2min  │                        │  │
│  │  └─────────────┘  └─────────────┘                        │  │
│  │         │                │                                │  │
│  │         └────────────────┘                                │  │
│  │                │                                          │  │
│  │          Create Tasks                                    │  │
│  │                │                                          │  │
│  │                ▼                                          │  │
│  │    Vault/Needs_Action/*.md                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                  │
│  ┌──────────────────────────┼────────────────────────────────┐│
│  │              REASONING LAYER (Orchestrator)               ││
│  ├──────────────────────────────────────────────────────────┤│
│  │                                                           ││
│  │  Main Loop (30s interval):                               ││
│  │                                                           ││
│  │  1. Git pull (get Cloud drafts)                          ││
│  │  2. Scan Vault/Drafts/ for review                        ││
│  │  3. Display drafts in Obsidian (human UI)                ││
│  │  4. If human approves draft:                             ││
│  │     a. Move to Vault/Approved/                           ││
│  │     b. Execute approved action (MCP servers)             ││
│  │     c. Move to Vault/Done/                               ││
│  │     d. Git sync (push results)                           ││
│  │  5. Scan Vault/Needs_Action/ for local tasks             ││
│  │  6. Process local tasks (same as Gold Tier)              ││
│  │                                                           ││
│  │  Components:                                             ││
│  │  ┌────────────┐ ┌──────────────┐ ┌─────────────┐        ││
│  │  │ Draft      │ │ Approval     │ │ Execution   │        ││
│  │  │ Reviewer   │ │ Handler      │ │ Engine      │        ││
│  │  └────────────┘ └──────────────┘ └─────────────┘        ││
│  │  ┌────────────┐ ┌──────────────┐ ┌─────────────┐        ││
│  │  │ Work-Zone  │ │ MCP Client   │ │ AI Agent    │        ││
│  │  │ Enforcer   │ │ Manager      │ │ Invoker     │        ││
│  │  └────────────┘ └──────────────┘ └─────────────┘        ││
│  │                                                           ││
│  └───────────────────────────────────────────────────────────┘│
│                             │                                  │
│  ┌──────────────────────────┼────────────────────────────────┐│
│  │                 ACTION LAYER (Enabled)                    ││
│  ├──────────────────────────────────────────────────────────┤│
│  │                                                           ││
│  │  ✅ MCP Servers: ALL ENABLED                             ││
│  │                                                           ││
│  │  ┌─────────────────┐  ┌─────────────────┐               ││
│  │  │ Email Sender    │  │ Odoo Accounting │               ││
│  │  │                 │  │                 │               ││
│  │  │ - Send emails   │  │ - Create invoice│               ││
│  │  │ - Templates     │  │ - Record expense│               ││
│  │  │ - Attachments   │  │ - Financial rpt │               ││
│  │  └─────────────────┘  └─────────────────┘               ││
│  │                                                           ││
│  │  ┌─────────────────┐  ┌─────────────────┐               ││
│  │  │ Meta Social     │  │ Twitter/X       │               ││
│  │  │                 │  │                 │               ││
│  │  │ - FB posting    │  │ - Tweet/thread  │               ││
│  │  │ - IG posting    │  │ - Search        │               ││
│  │  │ - Insights      │  │ - Timeline      │               ││
│  │  └─────────────────┘  └─────────────────┘               ││
│  │                                                           ││
│  │  ┌─────────────────┐                                     ││
│  │  │ WhatsApp        │                                     ││
│  │  │                 │                                     ││
│  │  │ - Send messages │                                     ││
│  │  │ - Templates     │                                     ││
│  │  │ - Contact mgmt  │                                     ││
│  │  └─────────────────┘                                     ││
│  │                                                           ││
│  │  Credentials: Loaded from .env (local only)              ││
│  │  Work-Zone: can_execute_action() returns True            ││
│  │                                                           ││
│  └───────────────────────────────────────────────────────────┘│
│                             │                                  │
│  ┌──────────────────────────┼────────────────────────────────┐│
│  │                STORAGE LAYER (Git Vault)                  ││
│  ├──────────────────────────────────────────────────────────┤│
│  │                                                           ││
│  │  Vault/ (Git origin repository)                          ││
│  │  ├── Needs_Action/   (Write: new local tasks)            ││
│  │  ├── Drafts/         (Read: from Cloud)                  ││
│  │  ├── Pending_Approval/ (Write: for human review)         ││
│  │  ├── Approved/       (Write: after approval)             ││
│  │  ├── Done/           (Write: completed tasks)            ││
│  │  ├── Plans/          (Read/Write: strategic plans)       ││
│  │  ├── DLQ/            (Write: failed tasks)               ││
│  │  ├── Logs/           (Write: all audit events)           ││
│  │  ├── Dashboard.md    (Read/Write: metrics)               ││
│  │  └── .env            (Read: secrets, NEVER committed)    ││
│  │                                                           ││
│  │  Git Operations (every 30s):                             ││
│  │  - git pull origin main                                  ││
│  │  - git add Approved/ Done/ Logs/ Dashboard.md            ││
│  │  - git commit -m "approve: <description>"                ││
│  │  - git push origin main                                  ││
│  │                                                           ││
│  └───────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │               USER INTERFACE LAYER                       │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  Obsidian Vault:                                        │   │
│  │  - View drafts in Drafts/ folder                        │   │
│  │  - Review task details and proposed actions             │   │
│  │  - Approve by moving to Approved/ folder                │   │
│  │  - Monitor Dashboard.md for real-time status            │   │
│  │  - View audit logs for transparency                     │   │
│  │                                                          │   │
│  │  PowerShell Scripts:                                    │   │
│  │  - Start_Local_Agent.ps1 (launch orchestrator)          │   │
│  │  - Launch_Abdullah_Junior.ps1 (full system startup)     │   │
│  │                                                          │   │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Component Interactions

**Sequence Diagram: Email Draft & Approval**

```
Cloud Agent     Git Remote      Local Agent      Human       Email MCP
    │               │               │              │              │
    │ 1. Detect     │               │              │              │
    │    email      │               │              │              │
    │───────►       │               │              │              │
    │               │               │              │              │
    │ 2. Create     │               │              │              │
    │    draft      │               │              │              │
    │───────►       │               │              │              │
    │          Drafts/task.md       │              │              │
    │               │               │              │              │
    │ 3. Git push   │               │              │              │
    │──────────────►│               │              │              │
    │               │               │              │              │
    │               │ 4. Git pull   │              │              │
    │               │◄──────────────│              │              │
    │               │               │              │              │
    │               │               │ 5. Display   │              │
    │               │               │    draft     │              │
    │               │               │─────────────►│              │
    │               │               │              │              │
    │               │               │ 6. Review &  │              │
    │               │               │    approve   │              │
    │               │               │◄─────────────│              │
    │               │               │              │              │
    │               │               │ 7. Move to   │              │
    │               │               │    Approved/ │              │
    │               │               │───────►      │              │
    │               │               │              │              │
    │               │               │ 8. Execute   │              │
    │               │               │──────────────┼─────────────►│
    │               │               │              │   send_email()
    │               │               │              │              │
    │               │               │ 9. Move to   │              │
    │               │               │    Done/     │              │
    │               │               │───────►      │              │
    │               │               │              │              │
    │               │ 10. Git push  │              │              │
    │               │◄──────────────│              │              │
    │               │               │              │              │
    │ 11. Git pull  │               │              │              │
    │◄──────────────│               │              │              │
    │  (sees Done/) │               │              │              │
    │               │               │              │              │
```

**Sequence Diagram: Claim-by-Move Race Condition**

```
Cloud Agent                  Filesystem                  Local Agent
    │                            │                            │
    │ 1. Scan Needs_Action/      │                            │
    │───────────────────────────►│                            │
    │      task1.md found        │                            │
    │                            │ 1. Scan Needs_Action/      │
    │                            │◄───────────────────────────│
    │                            │      task1.md found        │
    │                            │                            │
    │ 2. Try claim (move)        │                            │
    │───────────────────────────►│                            │
    │  rename(task1.md, Drafts/) │                            │
    │      ✅ SUCCESS             │                            │
    │                            │                            │
    │                            │ 2. Try claim (move)        │
    │                            │◄───────────────────────────│
    │                            │  rename(task1.md, Approved/)
    │                            │      ❌ FAIL (file not found)
    │                            │                            │
    │                            │─────────────────────────────►
    │                            │  FileNotFoundError          │
    │                            │                            │
    │ 3. Process task1           │ 3. Skip task1 (claimed)    │
    │    (draft response)        │    (log: already claimed)  │
    │                            │                            │
```

---

## 3. Data Architecture

### 3.1 Task File Schema

**File Naming Convention:**
```
{timestamp}_{source}_{priority}_{slug}.md

Examples:
- 2026-01-22_0200_gmail_high_Q4-report-request.md
- 2026-01-22_1430_whatsapp_medium_client-inquiry.md
- 2026-01-22_0930_linkedin_low_connection-request.md  
```

**File Structure:**
```yaml
---
# Metadata (YAML frontmatter)
id: "2026-01-22_0200_gmail_high_Q4-report-request"
source: "gmail"                    # Watcher that created task
priority: "high"                   # low, medium, high, urgent
domain: "BUSINESS"                 # PERSONAL, BUSINESS, BOTH
status: "draft"                    # draft, pending, approved, executing, done, failed
created_at: "2026-01-22T02:00:15Z"
updated_at: "2026-01-22T02:03:45Z"
claimed_by: "cloud-oracle-001"    # Agent that claimed task
claimed_at: "2026-01-22T02:01:00Z"
processed_by: null                # Agent that executed task (null if draft)
processed_at: null
completed_at: null
error: null                       # Error message if failed

# Classification
complexity: "simple"              # simple, moderate, complex
action_type: "send_email"         # send_email, post_social, create_invoice, etc.
risk_level: "low"                 # low, medium, high
approval_required: true           # Always true for Platinum

# AI Context
ai_agent: "gemini-2.0-flash"      # AI model used
processing_time: 3.5              # Seconds
confidence: 0.95                  # 0.0 to 1.0

# Related Files
related_tasks: []                 # IDs of related tasks
plan_file: null                   # Path to plan.md if complex task
attachments: []                   # Local file paths for attachments
---

# Task Content (Markdown body)

## Original Context
[Original email, message, or event that triggered this task]

## Proposed Action (DRAFT)
[AI-generated proposed response or action]

## Reasoning
[Why this action is proposed, what data was used, confidence level]

## Required Approval
- [ ] Human review checklist items
- [ ] Verify data accuracy
- [ ] Approve final action

## Execution Plan
[If complex: steps to execute, dependencies, rollback plan]

## Audit Trail
[Logged events for this task]
```

### 3.2 Vault Directory Structure

```
Vault/
├── .git/                           # Git repository metadata
├── .gitignore                      # Exclude secrets, temp files
│
├── Needs_Action/                   # Incoming tasks (watchers create here)
│   ├── INBOX.md                    # Manual task input
│   ├── 2026-01-22_0800_gmail_*.md
│   └── 2026-01-22_0915_whatsapp_*.md
│
├── Drafts/                         # Cloud agent drafts (Cloud writes, Local reads)
│   ├── 2026-01-22_0200_gmail_high_Q4-report.md
│   └── 2026-01-22_0315_linkedin_low_connection.md
│
├── Pending_Approval/               # Requires human review (Local writes)
│   └── 2026-01-22_1000_manual_high_invoice-send.md
│
├── Approved/                       # Approved for execution (Local writes)
│   └── 2026-01-22_1005_manual_high_invoice-send.md
│
├── Done/                           # Completed tasks (Local writes)
│   ├── 2026-01-22_0830_gmail_high_Q4-report.md
│   └── 2026-01-22_1010_manual_high_invoice-send.md
│
├── Plans/                          # Strategic plans for complex tasks (Both write)
│   ├── 2026-01-22_implement-crm-integration.plan.md
│   └── 2026-01-23_marketing-campaign.plan.md
│
├── Dead_Letter_Queue/              # Failed tasks (Both write)
│   └── 2026-01-22_0900_gmail_error_payment-processing.md
│
├── Logs/                           # Audit and health logs
│   ├── audit/
│   │   ├── audit_2026-01-22.jsonl  # Daily audit log (JSONL)
│   │   └── audit_2026-01-23.jsonl
│   └── health/
│       ├── health_2026-01-22.jsonl # Daily health metrics
│       └── health_2026-01-23.jsonl
│
├── Dashboard.md                    # Real-time metrics dashboard (Both write)
├── Company_Handbook.md             # Business rules and policies (Manual edit)
│
└── .env                            # Secrets (LOCAL ONLY - .gitignore)
    # NEVER COMMITTED TO GIT
```

### 3.3 Audit Log Schema

**File Format:** JSONL (JSON Lines) - one JSON object per line

**File Naming:** `audit_YYYY-MM-DD.jsonl`

**Schema:**
```json
{
  "timestamp": "2026-01-22T02:03:45.123Z",
  "agent_id": "cloud-oracle-001",
  "agent_type": "cloud",
  "event": "DRAFT_CREATED",
  "task_id": "2026-01-22_0200_gmail_high_Q4-report-request",
  "domain": "BUSINESS",
  "action_type": "send_email",
  "status": "success",
  "details": {
    "ai_agent": "gemini-2.0-flash",
    "processing_time": 3.5,
    "confidence": 0.95
  },
  "metadata": {
    "work_zone": "cloud",
    "git_commit": "abc123def456"
  }
}
```

**Event Types:**
- `TASK_CREATED` - New task detected by watcher
- `TASK_CLAIMED` - Agent claimed task (claim-by-move)
- `DRAFT_CREATED` - Cloud agent created draft
- `APPROVAL_REQUESTED` - Task moved to Pending_Approval
- `APPROVED` - Human approved task
- `REJECTED` - Human rejected task
- `EXECUTION_STARTED` - Execution began
- `EXECUTION_BLOCKED` - Execution blocked by work-zone
- `EXECUTED` - Action executed successfully
- `FAILED` - Execution failed
- `COMPLETED` - Task fully completed
- `GIT_SYNC` - Git push/pull operation
- `ERROR` - Error occurred

---

## 4. Communication Architecture

### 4.1 Git-Based Communication Protocol

**Why Git?**
- ✅ Proven distributed file synchronization
- ✅ Built-in conflict resolution
- ✅ Immutable history (audit trail)
- ✅ Works over unreliable networks
- ✅ No additional infrastructure needed
- ✅ Free (GitHub private repos)

**Communication Pattern:**

```
Time  Cloud Agent                Git Remote              Local Agent
─────────────────────────────────────────────────────────────────────
T0    [Gmail detects email]
      │
      ├─► Create task file
      │   Needs_Action/task1.md
      │
T1    ├─► git add Needs_Action/
      ├─► git commit -m "task: new email"
      ├─► git push origin main
      │                         ───────────►
      │                         [task1.md stored]
      │                                            [Offline - no pull]
      │
T2    [Claim task1]
      ├─► mv task1.md Drafts/
      │
      ├─► Generate draft response
      │
T3    ├─► git add Drafts/
      ├─► git commit -m "draft: email response"
      ├─► git push origin main
      │                         ───────────►
      │                         [draft stored]
      │                                            [Still offline]
      │
T4    [Continue monitoring]
      │                                            [Machine powers on]
      │                                            │
      │                                            ├─► git pull origin main
      │                         ◄───────────────
      │                         [sends draft]
      │                                            │
      │                                            ├─► Display draft in Obsidian
      │                                            │   [Human reviews]
      │
T5    │                                            ├─► Human approves
      │                                            ├─► mv draft Approved/
      │                                            │
      │                                            ├─► Execute: send_email()
      │                                            │
      │                                            ├─► mv task1.md Done/
      │                                            │
T6    │                                            ├─► git add Done/
      │                                            ├─► git commit -m "approve: sent email"
      │                                            ├─► git push origin main
      │                         ◄───────────────
      │                         [completion stored]
      │
T7    [Next sync cycle]
      ├─► git pull origin main
      ◄────────────────────────
      [sees Done/task1.md]
      │
      ├─► Update Dashboard.md
      │   "Last completed: task1"
```

### 4.2 Sync Protocol Details

**Pull Strategy:**
```python
def git_pull() -> dict:
    """
    Pull latest changes from remote.

    Returns:
        {"success": bool, "files_changed": int, "conflicts": list}
    """
    try:
        # Rebase to avoid merge commits
        result = subprocess.run(
            ["git", "pull", "origin", "main", "--rebase"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            files_changed = count_changed_files(result.stdout)
            return {
                "success": True,
                "files_changed": files_changed,
                "conflicts": [],
            }
        else:
            # Check for conflicts
            if "CONFLICT" in result.stdout:
                conflicts = parse_conflicts(result.stdout)
                # Auto-resolve: Local always wins
                for file in conflicts:
                    subprocess.run(["git", "checkout", "--ours", file])
                subprocess.run(["git", "add", "."])
                subprocess.run(["git", "rebase", "--continue"])

                return {
                    "success": True,
                    "files_changed": files_changed,
                    "conflicts": conflicts,
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
            "error": "Timeout",
        }
```

**Push Strategy:**
```python
def git_push(agent_id: str, description: str) -> dict:
    """
    Stage changes and push to remote.

    Args:
        agent_id: Agent identifier (e.g., "cloud-oracle-001")
        description: Brief description of changes

    Returns:
        {"success": bool, "files_pushed": int, "commit_sha": str}
    """
    try:
        # Stage changes (agent-specific folders)
        if agent_id.startswith("cloud"):
            folders = ["Drafts/", "Plans/", "Logs/audit/", "Dashboard.md"]
        else:  # local
            folders = ["Approved/", "Done/", "Pending_Approval/", "Logs/", "Dashboard.md"]

        subprocess.run(["git", "add"] + folders)

        # Check if there are changes to commit
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
        )

        if not status.stdout.strip():
            # No changes to commit
            return {
                "success": True,
                "files_pushed": 0,
                "commit_sha": None,
            }

        # Commit with structured message
        timestamp = datetime.now().isoformat()
        commit_msg = f"{agent_id}: {description} - {timestamp}"

        subprocess.run(["git", "commit", "-m", commit_msg])

        # Push to remote
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            commit_sha = get_last_commit_sha()
            files_pushed = count_committed_files()

            return {
                "success": True,
                "files_pushed": files_pushed,
                "commit_sha": commit_sha,
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
            "error": "Timeout",
        }
```

### 4.3 Conflict Resolution Strategy

**No Conflicts Expected:**
- Cloud and Local operate on different folders
- Cloud writes: `Drafts/`, `Plans/` (cloud-generated)
- Local writes: `Approved/`, `Done/`, `Pending_Approval/`

**If Conflict Occurs:**

**Scenario 1: Same file modified by both agents**
```
# Conflict detected in Dashboard.md

Cloud version:
## Agent Status
| Cloud | HEALTHY | 142 tasks |

Local version:
## Agent Status
| Local | HEALTHY | 37 tasks |

Resolution:
- Merge both sections (both valid)
- Auto-resolution: Git merge strategy "union"
- Result:
## Agent Status
| Cloud | HEALTHY | 142 tasks |
| Local | HEALTHY | 37 tasks |
```

**Scenario 2: File moved by both agents (impossible)**
```
# Cloud moves: task1.md → Drafts/task1.md
# Local moves: task1.md → Approved/task1.md

Result:
- Cloud succeeds (first to execute rename)
- Local fails (FileNotFoundError - task1.md gone)
- No conflict (atomic filesystem operation)
```

**Scenario 3: Force push required**
```
# Local has diverged from remote (rare)

Resolution:
- Local is the source of truth (human authority)
- Force push: git push --force origin main
- Cloud will pull and resync

Risk:
- Could lose Cloud's uncommitted changes
- Mitigated by: frequent commits (every 30s)
```

---

## 5. Security Architecture

### 5.1 Threat Model

**Assets:**
1. User credentials (Gmail password, API keys)
2. Task data (emails, messages, business info)
3. Audit logs (operational history)
4. Source code (system logic)

**Threat Actors:**
1. Cloud VM compromise (attacker gains access to Oracle instance)
2. Git repository leak (accidental public repo)
3. Man-in-the-middle (network interception)
4. Insider threat (malicious human with Local access)

**Attack Scenarios:**

**T1: Cloud VM Compromised**
- Attacker gains SSH access to Oracle VM
- What they can access:
  - ✅ Cloud agent code
  - ✅ Vault/ directory (task data)
  - ✅ Audit logs
  - ❌ User credentials (.env not synced)
  - ❌ MCP server access (no credentials)
- Impact: Medium (data exposure, no execution capability)
- Mitigation:
  - SSH key-only authentication
  - Minimal privileges (digitalfte user, no sudo)
  - Audit logs detect unauthorized access
  - Secrets never on cloud (cannot execute actions)

**T2: Git Repository Made Public**
- Attacker discovers public GitHub repo
- What they can access:
  - ✅ Task files (potentially sensitive data)
  - ✅ Audit logs
  - ✅ Source code
  - ❌ User credentials (.gitignore prevents commit)
- Impact: High (data leak)
- Mitigation:
  - Private repository enforced
  - .gitignore validated in CI/CD
  - Pre-commit hook blocks .env files
  - Encrypt sensitive task data (future enhancement)

**T3: Network MITM**
- Attacker intercepts Git traffic
- What they can access:
  - ❌ Nothing (Git uses SSH with encryption)
- Impact: Low
- Mitigation:
  - SSH key-based authentication (not HTTPS)
  - Git verifies remote fingerprint

**T4: Malicious Local User**
- Attacker gains access to Local machine
- What they can access:
  - ✅ All credentials (.env file)
  - ✅ Full MCP server access
  - ✅ Vault/ directory
  - ✅ Can execute arbitrary actions
- Impact: Critical (full system compromise)
- Mitigation:
  - Physical security (user's responsibility)
  - Audit log detects suspicious activity
  - Rate limiting prevents mass actions
  - Human-in-the-loop approval (can be bypassed by attacker)

### 5.2 Security Controls

**C1: Secrets Isolation**

```
┌─────────────────────────────────────────────────────────┐
│                    SECRETS NEVER SYNC                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  .gitignore (enforced):                                 │
│  ───────────────────────                                │
│  .env                                                    │
│  .env.local                                              │
│  .env.production                                         │
│  *.key                                                   │
│  *.pem                                                   │
│  credentials.json                                        │
│  secrets/                                                │
│                                                          │
│  Pre-commit hook (validates):                           │
│  ──────────────────────────────                         │
│  1. Check for .env files in staged changes              │
│  2. Check for API keys in task files (regex)            │
│  3. Check for passwords in audit logs                   │
│  4. Abort commit if secrets detected                    │
│                                                          │
│  Cloud Agent (cannot access):                           │
│  ────────────────────────────                           │
│  - No .env file present on VM                           │
│  - MCP servers disabled (no credentials needed)         │
│  - Cannot execute sensitive actions                     │
│                                                          │
│  Local Agent (has access):                              │
│  ──────────────────────────                             │
│  - .env file in project root (not synced)               │
│  - All MCP servers enabled with credentials             │
│  - Full execution permissions                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**C2: Work-Zone Enforcement**

```python
# src/utils/work_zone.py

from enum import Enum
from typing import Tuple

class WorkZone(Enum):
    CLOUD = "cloud"  # Draft mode only
    LOCAL = "local"  # Full execution

class ActionType(Enum):
    SEND_EMAIL = "send_email"
    POST_SOCIAL = "post_social_media"
    CREATE_INVOICE = "create_invoice"
    RECORD_EXPENSE = "record_expense"
    SEND_WHATSAPP = "send_whatsapp"
    READ_DATA = "read_data"  # Always allowed

# Sensitive actions that require Local work-zone
SENSITIVE_ACTIONS = {
    ActionType.SEND_EMAIL,
    ActionType.POST_SOCIAL,
    ActionType.CREATE_INVOICE,
    ActionType.RECORD_EXPENSE,
    ActionType.SEND_WHATSAPP,
}

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
            f"Action '{action.value}' requires LOCAL work-zone (human approval required)",
        )

    return (True, "Action permitted")


# Usage in orchestrator
import os
from src.utils.work_zone import can_execute_action, WorkZone, ActionType
from src.utils.audit_logger import log_audit, AuditStatus

work_zone_str = os.getenv("WORK_ZONE", "local")
work_zone = WorkZone(work_zone_str)

action = ActionType.SEND_EMAIL

allowed, reason = can_execute_action(action, work_zone)

if not allowed:
    # Create draft instead of executing
    create_draft(task, action, reason)

    log_audit(
        event="EXECUTION_BLOCKED",
        task_id=task.id,
        action_type=action.value,
        status=AuditStatus.BLOCKED,
        details={"reason": reason, "work_zone": work_zone.value},
    )
else:
    # Execute action
    execute_action(task, action)
```

**C3: Audit Trail**

```
┌─────────────────────────────────────────────────────────┐
│               IMMUTABLE AUDIT TRAIL                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Format: JSONL (append-only)                            │
│  Location: Vault/Logs/audit/audit_YYYY-MM-DD.jsonl      │
│  Retention: 90 days minimum                             │
│  Sync: Both Cloud and Local write, Git merges           │
│                                                          │
│  Logged Events:                                         │
│  ──────────────                                         │
│  - TASK_CREATED (watcher detects new task)              │
│  - TASK_CLAIMED (agent claims via claim-by-move)        │
│  - DRAFT_CREATED (Cloud generates draft)                │
│  - APPROVAL_REQUESTED (task needs human review)         │
│  - APPROVED (human approves)                            │
│  - REJECTED (human rejects)                             │
│  - EXECUTION_STARTED (action begins)                    │
│  - EXECUTION_BLOCKED (work-zone restriction)            │
│  - EXECUTED (action completes successfully)             │
│  - FAILED (action fails)                                │
│  - COMPLETED (task fully done)                          │
│  - GIT_SYNC (push/pull operation)                       │
│  - ERROR (any error)                                    │
│                                                          │
│  Security Features:                                     │
│  ──────────────────────                                 │
│  - No credentials in logs (sanitized)                   │
│  - No sensitive data (email bodies summarized)          │
│  - Tamper-evident (Git commit history)                  │
│  - Timestamped with ISO 8601                            │
│  - Agent ID for accountability                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**C4: SSH Key Authentication**

```bash
# Cloud Agent setup (Oracle VM)

# Generate SSH key for Git access
ssh-keygen -t ed25519 -C "cloud-agent@digitalfte" -f ~/.ssh/id_ed25519_cloud

# Add public key to GitHub as Deploy Key
# Settings → Deploy Keys → Add Deploy Key
# Title: "Cloud Agent (Read/Write)"
# Key: <paste contents of id_ed25519_cloud.pub>
# Allow write access: ✓

# Configure Git to use SSH
git config --global user.name "Cloud Agent"
git config --global user.email "cloud-agent@digitalfte"

# Test authentication
ssh -T git@github.com
# Expected: "Hi username/digital-fte-vault! You've successfully authenticated..."

# Clone repository with SSH (not HTTPS)
git clone git@github.com:username/digital-fte-vault.git ~/Hacathan_2
```

### 5.3 Data Protection

**Encryption at Rest:**
- Git repository: Encrypted on GitHub (AES-256)
- Oracle VM disk: Default encryption enabled
- Local machine: User's responsibility (BitLocker/FileVault)

**Encryption in Transit:**
- Git over SSH: TLS 1.3 + SSH key authentication
- HTTPS APIs: TLS 1.3 for all MCP servers

**Data Minimization:**
- Task files: Only include necessary context
- Audit logs: Sanitize sensitive data (e.g., email bodies → summaries)
- Retention: 90 days for audit logs, indefinite for tasks

---

## 6. Deployment Architecture

### 6.1 Oracle Cloud Infrastructure

**Network Topology:**

```
Internet
    │
    │ HTTPS (443)
    │ SSH (22)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│        Oracle Cloud VCN (Virtual Cloud Network)          │
│           Subnet: Public (10.0.0.0/24)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  Security List (Firewall Rules)                │    │
│  ├────────────────────────────────────────────────┤    │
│  │  Ingress:                                      │    │
│  │  - SSH (22) from 0.0.0.0/0                     │    │
│  │  - HTTPS (443) from 0.0.0.0/0 (future webhook) │    │
│  │                                                 │    │
│  │  Egress:                                       │    │
│  │  - All traffic allowed                         │    │
│  └────────────────────────────────────────────────┘    │
│                       │                                  │
│                       ▼                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │  Compute Instance                              │    │
│  │  ────────────────                              │    │
│  │  Name: digitalfte-cloud-001                    │    │
│  │  Shape: VM.Standard.A1.Flex (ARM)              │    │
│  │  OCPU: 4                                       │    │
│  │  Memory: 24 GB                                 │    │
│  │  Boot Volume: 200 GB                           │    │
│  │  OS: Ubuntu 22.04 LTS ARM64                    │    │
│  │  Public IP: <assigned-by-oracle>               │    │
│  │                                                 │    │
│  │  Processes:                                    │    │
│  │  ┌─────────────────────────────────────────┐   │    │
│  │  │ systemd                                 │   │    │
│  │  │  └─► digitalfte-cloud.service           │   │    │
│  │  │       └─► python orchestrator.py        │   │    │
│  │  │            ├─► Gmail Watcher (5min)     │   │    │
│  │  │            ├─► WhatsApp Watcher (2min)  │   │    │
│  │  │            ├─► LinkedIn Watcher (10min) │   │    │
│  │  │            ├─► Task Processor (30s)     │   │    │
│  │  │            └─► Git Sync (30s)           │   │    │
│  │  └─────────────────────────────────────────┘   │    │
│  │                                                 │    │
│  │  Monitoring:                                   │    │
│  │  - journalctl -u digitalfte-cloud.service -f   │    │
│  │  - Resource: htop, df -h                       │    │
│  │  - Health: Dashboard.md (Git synced)           │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Resource Allocation:**

| Resource | Allocated | Usage (Expected) | Limit |
|----------|-----------|------------------|-------|
| CPU | 4 OCPU (ARM) | 20-30% avg | 100% |
| Memory | 24 GB | 4-6 GB | 8 GB (soft limit) |
| Disk | 200 GB | 10-20 GB | 180 GB (alert at 90%) |
| Network Egress | 10 TB/month | <1 GB/month | Free tier limit |

### 6.2 Local Machine Architecture

**Operating Systems Supported:**
- Windows 10/11 (PowerShell scripts)
- macOS 12+ (Bash scripts)
- Ubuntu 22.04+ (Bash scripts)

**Directory Structure:**

```
D:\Hacathan_2\                    (or ~/Hacathan_2 on macOS/Linux)
├── .venv\                        Python virtual environment
├── src\                          Source code
├── tests\                        Test suite
├── docs\                         Documentation
├── config\                       Configuration files
│   ├── .env.example              Template
│   └── .env                      ACTUAL SECRETS (not committed)
├── Vault\                        Obsidian vault (Git origin)
├── specs\                        Specifications
├── requirements.txt              Python dependencies
└── Start_Local_Agent.ps1         Startup script
```

**Process Management:**

**Windows (PowerShell):**
```powershell
# Start_Local_Agent.ps1

Write-Host "Starting Digital FTE Local Agent..." -ForegroundColor Cyan

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Check Git status
Write-Host "Checking Git status..." -ForegroundColor Yellow
git status --short

# Pull latest changes
Write-Host "Pulling latest changes..." -ForegroundColor Yellow
git pull origin main

# Start orchestrator
Write-Host "Launching orchestrator..." -ForegroundColor Green
python src\orchestrator.py

# If orchestrator crashes, log error
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Orchestrator crashed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
```

**macOS/Linux (Bash):**
```bash
#!/bin/bash
# start_local_agent.sh

echo "Starting Digital FTE Local Agent..."

# Activate virtual environment
source .venv/bin/activate

# Check Git status
echo "Checking Git status..."
git status --short

# Pull latest changes
echo "Pulling latest changes..."
git pull origin main

# Start orchestrator
echo "Launching orchestrator..."
python src/orchestrator.py

# If orchestrator crashes, log error
if [ $? -ne 0 ]; then
    echo "ERROR: Orchestrator crashed!"
    read -p "Press Enter to exit"
fi
```

---

## 7. Monitoring Architecture

### 7.1 Health Metrics

**Collected Metrics:**

```python
# src/utils/health.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import psutil
import subprocess

class HealthStatus(Enum):
    HEALTHY = "healthy"      # All systems operational
    DEGRADED = "degraded"    # Some issues, still functional
    UNHEALTHY = "unhealthy"  # Critical issues, needs attention

@dataclass
class HealthMetrics:
    # Agent info
    agent_id: str
    agent_type: str  # "cloud" or "local"
    status: HealthStatus
    timestamp: datetime

    # Uptime
    uptime_seconds: int
    last_restart: datetime

    # Task metrics (24h rolling window)
    tasks_processed: int
    tasks_failed: int
    tasks_pending: int
    failure_rate: float  # tasks_failed / tasks_processed

    # Watcher metrics
    watchers_active: int
    watchers_total: int
    last_task_detected: datetime

    # MCP metrics
    mcp_servers_active: int
    mcp_servers_total: int

    # Resource metrics
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_gb_used: float
    disk_percent: float

    # Git metrics
    git_commits_behind: int  # How far behind remote
    git_last_sync: datetime
    git_sync_failures_24h: int

    # Error metrics
    errors_24h: int
    last_error: str | None
    last_error_time: datetime | None


def collect_health_metrics(agent_id: str, agent_type: str) -> HealthMetrics:
    """Collect all health metrics for current agent."""

    # Uptime
    uptime = get_process_uptime()
    last_restart = datetime.now() - timedelta(seconds=uptime)

    # Task metrics
    task_stats = get_task_statistics()

    # Watcher metrics
    watcher_stats = get_watcher_statistics()

    # MCP metrics
    mcp_stats = get_mcp_statistics()

    # Resource metrics
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    # Git metrics
    git_stats = get_git_statistics()

    # Error metrics
    error_stats = get_error_statistics()

    # Determine overall status
    status = determine_health_status(
        failure_rate=task_stats["failure_rate"],
        git_sync_failures=git_stats["failures_24h"],
        errors_24h=error_stats["count_24h"],
        cpu_percent=cpu,
        memory_percent=memory.percent,
        disk_percent=disk.percent,
    )

    return HealthMetrics(
        agent_id=agent_id,
        agent_type=agent_type,
        status=status,
        timestamp=datetime.now(),
        uptime_seconds=uptime,
        last_restart=last_restart,
        tasks_processed=task_stats["processed"],
        tasks_failed=task_stats["failed"],
        tasks_pending=task_stats["pending"],
        failure_rate=task_stats["failure_rate"],
        watchers_active=watcher_stats["active"],
        watchers_total=watcher_stats["total"],
        last_task_detected=watcher_stats["last_detected"],
        mcp_servers_active=mcp_stats["active"],
        mcp_servers_total=mcp_stats["total"],
        cpu_percent=cpu,
        memory_mb=memory.used / 1024 / 1024,
        memory_percent=memory.percent,
        disk_gb_used=disk.used / 1024 / 1024 / 1024,
        disk_percent=disk.percent,
        git_commits_behind=git_stats["commits_behind"],
        git_last_sync=git_stats["last_sync"],
        git_sync_failures_24h=git_stats["failures_24h"],
        errors_24h=error_stats["count_24h"],
        last_error=error_stats["last_message"],
        last_error_time=error_stats["last_time"],
    )


def determine_health_status(
    failure_rate: float,
    git_sync_failures: int,
    errors_24h: int,
    cpu_percent: float,
    memory_percent: float,
    disk_percent: float,
) -> HealthStatus:
    """Determine overall health status from metrics."""

    # Critical conditions (UNHEALTHY)
    if failure_rate > 0.5:  # >50% task failure rate
        return HealthStatus.UNHEALTHY
    if git_sync_failures >= 5:  # 5+ consecutive sync failures
        return HealthStatus.UNHEALTHY
    if disk_percent > 95:  # Disk almost full
        return HealthStatus.UNHEALTHY
    if memory_percent > 95:  # Memory almost exhausted
        return HealthStatus.UNHEALTHY

    # Warning conditions (DEGRADED)
    if failure_rate > 0.2:  # >20% task failure rate
        return HealthStatus.DEGRADED
    if git_sync_failures >= 2:  # 2+ sync failures
        return HealthStatus.DEGRADED
    if errors_24h > 10:  # Frequent errors
        return HealthStatus.DEGRADED
    if cpu_percent > 80:  # High CPU usage
        return HealthStatus.DEGRADED
    if memory_percent > 80:  # High memory usage
        return HealthStatus.DEGRADED

    # All good
    return HealthStatus.HEALTHY
```

### 7.2 Dashboard

**Real-Time Dashboard (Dashboard.md):**

```markdown
# Digital FTE Health Dashboard

**Last Updated:** 2026-01-22 14:35:17 UTC
**Refresh Interval:** 60 seconds

---

## 📊 Agent Status

| Agent ID | Type | Status | Uptime | Last Sync |
|----------|------|--------|--------|-----------|
| cloud-oracle-001 | Cloud | 🟢 HEALTHY | 15d 8h 23m | 30s ago |
| local-laptop-001 | Local | 🟢 HEALTHY | 8h 12m 05s | 35s ago |

---

## 📈 Task Metrics (24h Rolling)

### Cloud Agent
- **Processed:** 142 tasks
- **Failed:** 3 tasks (2.1% failure rate)
- **Pending:** 0 tasks
- **Avg Processing Time:** 4.2s

### Local Agent
- **Processed:** 37 tasks
- **Failed:** 0 tasks (0.0% failure rate)
- **Pending:** 3 drafts awaiting review
- **Avg Approval Time:** 8.5 minutes

---

## 👁️ Watchers

| Watcher | Agent | Status | Last Check | Items Detected (24h) |
|---------|-------|--------|------------|----------------------|
| Gmail | Cloud | 🟢 Active | 2 min ago | 45 emails |
| WhatsApp (Cloud) | Cloud | 🟢 Active | 30s ago | 12 messages |
| LinkedIn | Cloud | 🟢 Active | 8 min ago | 5 connections |
| Filesystem | Local | 🟢 Active | 1 min ago | 2 file changes |
| WhatsApp (Local) | Local | 🟢 Active | 45s ago | 3 messages |

---

## 🔌 MCP Servers

| Server | Agent | Status | Last Used | Success Rate |
|--------|-------|--------|-----------|--------------|
| Email Sender | Local | 🟢 Ready | 15 min ago | 100% (12/12) |
| Odoo Accounting | Local | 🟢 Ready | Never | N/A |
| Meta Social | Local | 🟢 Ready | 2 hours ago | 100% (3/3) |
| Twitter/X | Local | 🟢 Ready | Yesterday | 100% (1/1) |
| WhatsApp | Local | 🟢 Ready | 5 min ago | 100% (5/5) |

---

## 💻 Resource Usage

### Cloud Agent (Oracle VM)
- **CPU:** 22% (4 OCPU Ampere ARM)
- **Memory:** 4.2 GB / 24 GB (17%)
- **Disk:** 12.5 GB / 200 GB (6%)
- **Network (24h):** 125 MB egress, 89 MB ingress

### Local Agent (Laptop)
- **CPU:** 8% (8 cores Intel i7)
- **Memory:** 2.1 GB / 16 GB (13%)
- **Disk:** 45.2 GB / 512 GB (9%)

---

## 📁 Vault Status

| Folder | Tasks | Size |
|--------|-------|------|
| Needs_Action | 0 | 0 KB |
| Drafts | 3 | 24 KB |
| Pending_Approval | 0 | 0 KB |
| Approved | 0 | 0 KB |
| Done (7 days) | 127 | 1.2 MB |
| Plans | 8 | 156 KB |
| Dead_Letter_Queue | 0 | 0 KB |

**Git Status:**
- Commits behind remote: 0 (synced)
- Commits ahead of remote: 0 (synced)
- Last sync: 35 seconds ago
- Sync failures (24h): 0

---

## ⚠️ Alerts & Warnings

- ✅ No alerts at this time

---

## 📋 Recent Activity (Last 10 Events)

1. `14:35:15` [Cloud] Git sync completed (0 files pulled, 1 file pushed)
2. `14:34:50` [Local] Approved and sent email: "Q4 Financial Summary"
3. `14:32:12` [Cloud] Created draft: "LinkedIn connection request response"
4. `14:30:45` [Local] Git sync completed (1 file pulled, 0 files pushed)
5. `14:28:33` [Cloud] Gmail watcher detected new email: "Product inquiry"
6. `14:25:00` [Cloud] Created draft: "Product inquiry response"
7. `14:20:18` [Local] Sent WhatsApp message: "Meeting confirmation"
8. `14:15:22` [Cloud] LinkedIn watcher detected connection request
9. `14:10:05` [Local] Filesystem watcher detected file change: "contract.pdf"
10. `14:05:33` [Cloud] Git sync completed (0 files pulled, 2 files pushed)

---

## 🔍 Debug Info

- Cloud Agent Version: 1.0.0-platinum
- Local Agent Version: 1.0.0-platinum
- Python Version: 3.14.0
- Git Version: 2.45.1
- Last Health Check: 35 seconds ago
- Next Health Check: 25 seconds

---

_This dashboard is auto-updated by both agents and synced via Git._
```

---

## 8. Architectural Decision Records

### ADR-001: Git Over Direct Agent-to-Agent Communication

**Date:** 2026-01-22
**Status:** Accepted
**Context:**

Platinum Tier requires two agents (Cloud + Local) to communicate and coordinate tasks. We evaluated two primary approaches:

**Option A: Direct Agent-to-Agent (A2A) Communication**
- WebSocket or HTTP API for real-time messaging
- Requires centralized message broker or peer-to-peer protocol
- Low latency (<1s)
- Complex failure modes (connection drops, state management)
- Additional infrastructure (message queue, API server)

**Option B: File-Based Communication via Git**
- Agents communicate by reading/writing shared files
- Git repository as source of truth
- Higher latency (30s default sync interval)
- Simple failure mode (continues operating locally, syncs when reconnected)
- No additional infrastructure (leverage GitHub)

**Decision:**

We chose **Option B: File-Based Communication via Git**.

**Rationale:**

1. **Simplicity:** No distributed systems complexity, no message brokers, no API servers
2. **Reliability:** Git is proven technology with mature conflict resolution
3. **Audit Trail:** Every communication is a Git commit (immutable history)
4. **Offline Resilience:** Agents operate independently when network partitioned
5. **Cost:** $0 (GitHub free tier vs. running message broker)
6. **Acceptable Latency:** 30s is sufficient for our use case (not real-time critical)

**Consequences:**

- ✅ Simple architecture, easy to debug
- ✅ Built-in audit trail via Git history
- ✅ Resilient to network failures
- ❌ Higher latency than real-time messaging (30s vs. <1s)
- ❌ Potential for merge conflicts (mitigated by folder separation)

**Alternatives Considered:**
- Redis pub/sub
- RabbitMQ
- gRPC
- HTTP webhooks

---

### ADR-002: Oracle Cloud Free Tier Over AWS/Azure

**Date:** 2026-01-22
**Status:** Accepted
**Context:**

Platinum Tier requires 24/7 cloud VM for running Cloud Agent. We evaluated three cloud providers:

**Option A: AWS Free Tier (EC2 t2.micro)**
- 750 hours/month (only enough for 1 instance)
- 1 vCPU, 1 GB RAM
- 12 months free, then pay-as-you-go
- Monthly cost after free tier: ~$8.50/month

**Option B: Azure Free Tier (B1S)**
- 750 hours/month
- 1 vCPU, 1 GB RAM
- 12 months free, then pay-as-you-go
- Monthly cost after free tier: ~$7.60/month

**Option C: Oracle Cloud Always Free Tier (VM.Standard.A1.Flex)**
- Unlimited hours (always free, forever)
- 4 OCPU (Ampere ARM), 24 GB RAM, 200 GB storage
- No expiration
- Monthly cost: $0 (forever)

**Decision:**

We chose **Option C: Oracle Cloud Always Free Tier**.

**Rationale:**

1. **Cost:** $0/month forever (vs. limited free trial on AWS/Azure)
2. **Resources:** 4 CPU + 24 GB RAM (vs. 1 CPU + 1 GB RAM)
3. **Sustainability:** No expiration, no billing surprises
4. **Sufficient for Platinum:** Easily handles watchers + orchestrator

**Consequences:**

- ✅ Zero cost infrastructure (hackathon judging criteria)
- ✅ Generous resources for growth (4 CPU, 24 GB RAM)
- ✅ Always-on availability (no free tier expiration)
- ❌ ARM architecture (some Python packages may need recompilation)
- ❌ Vendor lock-in to Oracle Cloud (mitigated by Docker portability)

**Alternatives Considered:**
- DigitalOcean ($5/month)
- Linode ($5/month)
- Self-hosted Raspberry Pi (unreliable, no public IP)

---

### ADR-003: Work-Zone Specialization Over Role-Based Access Control

**Date:** 2026-01-22
**Status:** Accepted
**Context:**

Platinum Tier requires separating draft (Cloud) from execution (Local). We evaluated two security models:

**Option A: Role-Based Access Control (RBAC)**
- Each agent has specific roles (e.g., "drafter", "executor")
- Permissions checked against centralized policy
- Fine-grained control over individual actions
- Requires policy engine and permission database

**Option B: Work-Zone Specialization**
- Each agent operates in one of two work-zones: CLOUD (draft) or LOCAL (execute)
- Work-zone determined by environment variable (WORK_ZONE=cloud/local)
- Simple boolean check: "Can this action execute in this work-zone?"
- No centralized policy, no database

**Decision:**

We chose **Option B: Work-Zone Specialization**.

**Rationale:**

1. **Simplicity:** Single environment variable, no policy engine needed
2. **Clear Intent:** Work-zone clearly communicates agent purpose
3. **Fail-Safe:** Cloud has no credentials, physically cannot execute
4. **Easy to Audit:** Work-zone logged in every audit event
5. **KISS Principle:** Solves exactly our requirements, no over-engineering

**Consequences:**

- ✅ Simple implementation (few lines of code)
- ✅ Easy to understand and audit
- ✅ Fail-safe (Cloud cannot execute even if code bug)
- ❌ Less flexible than RBAC (only two work-zones)
- ❌ Cannot implement fine-grained permissions (acceptable for our use case)

**Alternatives Considered:**
- Casbin (policy engine)
- OAuth 2.0 scopes
- Custom permission system

---

### ADR-004: Systemd Over Cron for Cloud Agent

**Date:** 2026-01-22
**Status:** Accepted
**Context:**

Cloud Agent must run 24/7 on Oracle VM. We need auto-restart on failure. Two primary options:

**Option A: Cron (Scheduled Execution)**
- Cron job runs orchestrator every N minutes
- Simple setup: `* * * * * python orchestrator.py`
- No built-in restart on failure
- Difficult to monitor (no central process)

**Option B: Systemd (Service Manager)**
- Systemd service runs orchestrator as daemon
- Auto-restart on crash (Restart=always)
- Centralized logging (journalctl)
- Process monitoring (systemctl status)

**Decision:**

We chose **Option B: Systemd Service Manager**.

**Rationale:**

1. **Auto-Restart:** Systemd automatically restarts on crash
2. **Monitoring:** `systemctl status` shows health at a glance
3. **Logging:** `journalctl -u digitalfte` for centralized logs
4. **Resource Limits:** Systemd can enforce memory/CPU caps
5. **Standard Practice:** Industry standard for Linux daemons

**Consequences:**

- ✅ Automatic restart on failure (within 10s)
- ✅ Easy monitoring and logging
- ✅ Resource limit enforcement
- ❌ Linux-only (not portable to Windows - acceptable for Cloud Agent)
- ❌ Requires root for service installation (one-time setup)

**Alternatives Considered:**
- Supervisor (Python-based process manager)
- Docker + restart policy
- PM2 (Node.js process manager)

---

## Appendix: Diagrams

### A1: Task Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                      TASK LIFECYCLE                              │
└─────────────────────────────────────────────────────────────────┘

[External Event]
     │
     │ (Email arrives, WhatsApp message, LinkedIn notification)
     │
     ▼
┌─────────────────┐
│  WATCHER        │  Detects event, creates task file
│  (Cloud/Local)  │  Location: Vault/Needs_Action/<task>.md
└────────┬────────┘  Status: created
         │
         │ [Task sits in Needs_Action/]
         │
         ▼
┌─────────────────┐
│  ORCHESTRATOR   │  Scans Needs_Action/ every 30s
│  (Cloud/Local)  │  Attempts claim-by-move
└────────┬────────┘
         │
         │ [Atomic filesystem move]
         │
         ├──► SUCCESS: Task claimed
         │    └──► Cloud: moves to Drafts/
         │    └──► Local: moves to Pending_Approval/ or Approved/
         │
         └──► FAILURE: Another agent claimed (FileNotFoundError)
              └──► Skip, log "already claimed"
         │
         ▼
┌─────────────────┐
│  PROCESSING     │  Cloud: Generate draft (AI agent)
│  (Work-Zone)    │  Local: Review or execute
└────────┬────────┘  Status: processing
         │
         ├──► Cloud Work-Zone (DRAFT):
         │    │
         │    ├──► can_execute_action() = False
         │    ├──► Create draft response
         │    ├──► Save to Vault/Drafts/<task>.md
         │    ├──► Log: DRAFT_CREATED
         │    └──► Git push (sync to Local)
         │         │
         │         └──► [Draft waits for Local to pull]
         │              │
         │              ▼
         │         ┌────────────────┐
         │         │  HUMAN REVIEW  │  Local agent displays draft
         │         │  (Obsidian UI) │  User reviews in Obsidian
         │         └────────┬───────┘
         │                  │
         │                  ├──► APPROVE:
         │                  │    ├──► Move to Vault/Approved/
         │                  │    ├──► Execute action (MCP server)
         │                  │    ├──► Move to Vault/Done/
         │                  │    ├──► Log: APPROVED, EXECUTED, COMPLETED
         │                  │    └──► Git push (sync completion)
         │                  │
         │                  ├──► MODIFY:
         │                  │    ├──► Edit task file
         │                  │    ├──► Move to Vault/Approved/
         │                  │    └──► [Same as APPROVE]
         │                  │
         │                  └──► REJECT:
         │                       ├──► Move to Vault/DLQ/
         │                       ├──► Log: REJECTED
         │                       └──► Git push
         │
         └──► Local Work-Zone (EXECUTE):
              │
              ├──► can_execute_action() = True
              ├──► Execute action directly (MCP server)
              ├──► Move to Vault/Done/
              ├──► Log: EXECUTED, COMPLETED
              └──► Git push (sync completion)
         │
         ▼
┌─────────────────┐
│  COMPLETED      │  Task in Vault/Done/
│  (Archived)     │  Status: done
└─────────────────┘  Available in audit log

         OR

┌─────────────────┐
│  FAILED         │  Task in Vault/DLQ/
│  (Dead Letter)  │  Status: failed
└─────────────────┘  Manual review required
```

---

**Architecture Document Status:** ✅ COMPLETE - Ready for Tasks Breakdown

**Next Steps:**
1. Create tasks.md (implementation breakdown with estimates)
2. Create security.md (detailed threat model and controls)
3. Create operations.md (deployment and maintenance runbooks)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-22
**Status:** Draft - Awaiting Review
