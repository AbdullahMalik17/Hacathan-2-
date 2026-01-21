# Feature Specification: Platinum Tier - Cloud + Local Executive

**Feature Branch**: `008-platinum-tier`  
**Created**: 2026-01-21  
**Status**: Draft  
**Input**: Platinum Tier requirements from Hackathon blueprint

## User Scenarios & Testing

### User Story 1 - Work-Zone Specialization (Priority: P1)

The Digital FTE system operates differently depending on whether it is running in "Cloud" or "Local" mode. 
- **Cloud Agent**: Performs triage, drafts replies, schedules social posts (Draft only).
- **Local Agent**: Processes approvals, executes final "send/post" actions, manages WhatsApp session, and handles banking.

**Why this priority**: Essential for security and production-grade separation of duties. Keeps secrets/sessions on local hardware while leveraging cloud availability.

**Independent Test**: Configure an instance as `ENVIRONMENT=cloud`, verify it cannot send emails directly but can create draft files in `Pending_Approval`. Configure as `ENVIRONMENT=local`, verify it can execute approved tasks.

---

### User Story 2 - Git-Based Vault Sync (Priority: P1)

Cloud and Local instances synchronize the Obsidian Vault (Markdown files/state) via Git to ensure coordination without sharing secrets (.env, tokens).

**Why this priority**: Foundation for multi-agent coordination. Enables "Delegation via Synced Vault".

**Independent Test**: Change a file on "Cloud", run sync, verify changes appear on "Local" within 5 minutes.

---

### User Story 3 - Claim-by-Move Rule (Priority: P1)

Prevents double-work by using a "claim-by-move" rule: first agent to move an item from `/Needs_Action` to `/In_Progress/<agent>/` owns it.

**Why this priority**: Critical for concurrency safety in a multi-agent environment.

**Independent Test**: Simultaneously trigger two agents on the same task; verify only one succeeds in moving it to its `/In_Progress` subfolder.

---

### User Story 4 - Platinum Demo Flow (Priority: P1)

A complete end-to-end flow: Email arrives -> Cloud drafts reply + creates approval file -> Local user approves -> Local executes send via MCP -> logs -> moves task to /Done.

**Why this priority**: Passing gate for Platinum Tier verification.

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST identify its environment via `FTE_ROLE` (cloud/local).
- **FR-002**: Cloud instance MUST be restricted to READ-ONLY or DRAFT-ONLY for sensitive MCP tools (Email, Social).
- **FR-003**: System MUST implement `VaultSync` utility using `git pull/push`.
- **FR-004**: System MUST implement `claim_task(task_path, agent_id)` logic to prevent race conditions.
- **FR-005**: System MUST maintain a single-writer rule for `Dashboard.md` (Local only).
- **FR-006**: Cloud MUST write updates to `/Updates/` or `/Signals/` folder for Local to merge.
- **FR-007**: System MUST exclude `.env`, `credentials.json`, and session data from Vault sync.

### Key Entities

- **AgentRole**: Enum (CLOUD, LOCAL).
- **VaultSyncManager**: Handles Git operations and conflict resolution.
- **TaskClaim**: Entry in `/In_Progress/<agent>/` indicating ownership.
- **SpecializationMatrix**: Map of tools/actions allowed per role.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Zero secrets leaked to Cloud (verified via `.gitignore`).
- **SC-002**: <5 minute sync latency between Cloud and Local.
- **SC-003**: 100% adherence to Claim-by-Move (zero duplicate executions).
- **SC-004**: Successful "Always-On" operation (99.9% uptime for Cloud watchers).
- **SC-005**: Seamless handover (Local picks up Cloud drafts automatically).
