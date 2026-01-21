# Implementation Tasks: Platinum Tier

## 1. Foundation & Directories

- [ ] **Create Folders**:
  - Create `Vault/In_Progress/cloud`
  - Create `Vault/In_Progress/local`
  - Create `Vault/Updates`
- [ ] **Config Update**:
  - Add `FTE_ROLE` and `AGENT_ID` to `config/.env.example`.

## 2. Orchestrator Specialization

- [ ] **Claim-by-Move Logic**:
  - Update `process_task` in `src/orchestrator.py` to use `In_Progress` folder.
- [ ] **Role-Based Workflow**:
  - Cloud: Process `Needs_Action` -> Move to `Pending_Approval` or `In_Progress`.
  - Local: Process `Approved` -> Execute.

## 3. Vault Sync Implementation

- [ ] **Sync Script**: Create `src/utils/vault_sync.py`.
- [ ] **Service Integration**: Add `vault-sync` to `src/service_manager.py`.

## 4. Safety Rails (MCP)

- [ ] **Restricted Tooling**:
  - Update `src/mcp_servers/email_sender.py` to check `os.getenv("FTE_ROLE")`.
  - Disable direct send if `ROLE == cloud`.

## 5. Documentation

- [ ] **Deployment Guide**: Create `docs/PLATINUM_DEPLOYMENT.md`.
