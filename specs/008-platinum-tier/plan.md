# Implementation Plan: Platinum Tier

## 1. Core Changes

### Environment Configuration
- Add `FTE_ROLE` to `.env` (values: `cloud`, `local`).
- Add `AGENT_ID` to `.env` (e.g., `cloud-01`, `local-01`).

### Directory Structure
Ensure these exist:
- `Vault/In_Progress/cloud/`
- `Vault/In_Progress/local/`
- `Vault/Updates/` (Cloud writes here)

### Orchestrator Logic
- Update `DigitalFTEOrchestrator.process_task`:
  - Before starting, move task to `/In_Progress/<ROLE>/`.
  - If move fails (already gone), skip task.
- Implementation of `FTE_ROLE` checks:
  - If `cloud`, only process `Needs_Action`.
  - If `local`, process `Approved` AND merge `Updates`.

## 2. Vault Sync Utility (`src/utils/vault_sync.py`)

- Method `sync()`:
  - `git fetch`
  - `git add Vault/`
  - `git commit -m "agent sync"`
  - `git pull --rebase`
  - `git push`
- Add to `service_manager.py` as a managed service.

## 3. Tool Restrictions

- **EmailSenderMCP**: If `FTE_ROLE == 'cloud'`, force `requires_approval=True`.
- **WhatsAppWatcher**: If `FTE_ROLE == 'cloud'`, disable service.

## 4. Odoo Enhancements
- Support Odoo on Cloud (URL configuration).
- Draft-only mode for Cloud.

## 5. Deployment Guide
- Create `docs/PLATINUM_DEPLOYMENT.md`.
