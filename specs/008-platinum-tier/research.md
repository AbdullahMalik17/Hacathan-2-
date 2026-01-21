# Research Findings: Platinum Tier

## 1. Environment Specialization

### Concept
The system needs to know if it is running in "Cloud" or "Local" mode. This will be controlled by an environment variable `FTE_ROLE`.

### Sensitive Actions
- **Email**: Cloud should only use `send_email(..., requires_approval=True)`.
- **WhatsApp**: Local only (due to session dependency).
- **Social Media**: Cloud drafts, Local posts.
- **Banking/Payments**: Local only.

## 2. Vault Sync Mechanism

### Choice: Git
- **Rationale**: Built-in conflict resolution, history, and easy exclusion of files via `.gitignore`.
- **Implementation**: A `SyncManager` that periodically runs `git add .`, `git commit -m "sync"`, `git pull --rebase`, and `git push`.

### Race Condition Prevention
- **Claim-by-Move**:
  - `Vault/Needs_Action/task.md`
  - Agent A moves to `Vault/In_Progress/cloud/task.md`
  - Agent B sees it's gone from `Needs_Action`, ignores it.

## 3. Odoo Deployment

### Strategy
- Deploy Odoo Community on a Cloud VM (e.g., Oracle Cloud Free Tier).
- Use HTTPS (Nginx reverse proxy + Certbot).
- Integrate Cloud Agent with Odoo for "Draft" actions.

## 4. Gaps in Current Codebase

- **Orchestrator**: Needs to respect `FTE_ROLE`.
- **MCP Servers**: Need to check `FTE_ROLE` before executing destructive actions.
- **Directories**: Need `/In_Progress/cloud/` and `/In_Progress/local/`.
- **Sync Script**: Doesn't exist yet.
