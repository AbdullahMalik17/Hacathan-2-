# Platinum Tier Deployment Guide: Always-On Cloud + Local Executive

This guide explains how to set up the Digital FTE in a production-ish configuration using a Cloud VM and a Local machine.

## Architecture

- **Cloud VM**: Runs 24/7. Monitors sensors (Gmail, FS, etc.). Triages tasks and drafts replies.
- **Local Machine**: User's laptop. Processes approvals, executes final actions, manages WhatsApp session.
- **Sync**: Git-based Obsidian Vault synchronization.

## 1. Prerequisites

- A Git repository (GitHub/GitLab) to host your `Vault`.
- A Cloud VM (e.g., Oracle Cloud Free Tier, AWS, DigitalOcean).
- Python 3.10+ and Node.js v24+ on both machines.

## 2. Cloud VM Setup

1. **Clone Repository**:
   ```bash
   git clone <your-repo-url>
   cd Hacathan_2
   ```
2. **Environment Configuration**:
   ```bash
   cp config/.env.example .env
   # Set FTE_ROLE=cloud
   # Set AGENT_ID=cloud-01
   # Set DRY_RUN=false
   ```
3. **Install Dependencies**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Register Service Manager**:
   - Use `systemd` (Linux) to keep `src/service_manager.py` running.

## 3. Local Machine Setup

1. **Environment Configuration**:
   ```bash
   # Set FTE_ROLE=local
   # Set AGENT_ID=local-01
   ```
2. **Run Service Manager**:
   ```powershell
   ./scripts/install_service.ps1
   ```

## 4. Specialization Rules

### Cloud Agent
- **Gmail**: Triage only. All `send_email` calls are forced to `requires_approval=True`.
- **Social Media**: Drafts posts to `Vault/Pending_Approval`.
- **WhatsApp**: Disabled (Local only).
- **In_Progress**: Uses `Vault/In_Progress/cloud/`.

### Local Agent
- **Approvals**: Picks up files from `Vault/Approved/`.
- **Execution**: Sends emails, posts to LinkedIn, makes payments.
- **WhatsApp**: Fully enabled.
- **Merge**: Regularly merges files from `Vault/Updates/` into `Dashboard.md`.

## 5. Security & Sync

- **Secrets**: `.env` and `credentials.json` are in `.gitignore`. They MUST be manually configured on each machine.
- **Sync Interval**: Defaults to 5 minutes (`SYNC_INTERVAL=300`).
- **Claim-by-Move**: Orchestrator automatically moves tasks from `Needs_Action` to its specific `In_Progress` subfolder to prevent double-work.

---
*Digital FTE Platinum Tier Configuration*
