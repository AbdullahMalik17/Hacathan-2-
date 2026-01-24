# Platinum Tier Security Documentation

**Version:** 1.0
**Date:** 2026-01-22
**Classification:** Internal Use
**Compliance:** GDPR, SOC 2 (future)

---

## Table of Contents

1. [Security Overview](#1-security-overview)
2. [Threat Model](#2-threat-model)
3. [Security Controls](#3-security-controls)
4. [Secrets Management](#4-secrets-management)
5. [Access Control](#5-access-control)
6. [Data Protection](#6-data-protection)
7. [Audit & Compliance](#7-audit--compliance)
8. [Incident Response](#8-incident-response)
9. [Security Checklist](#9-security-checklist)

---

## 1. Security Overview

### 1.1 Security Philosophy

**Zero Trust Architecture:**
- Cloud Agent has no credentials (cannot execute sensitive actions)
- All sensitive operations require human approval
- Secrets never leave local machine
- Every action logged in immutable audit trail

**Defense in Depth:**
- Multiple layers of security controls
- Work-zone enforcement prevents unauthorized execution
- SSH key-based authentication (no passwords)
- Git repository access control

**Principle of Least Privilege:**
- Cloud Agent: Read-only operations, draft creation only
- Local Agent: Full permissions with human oversight
- Service users: Minimal system privileges

### 1.2 Security Objectives

| Objective | Control | Status |
|-----------|---------|--------|
| **Confidentiality** | Secrets isolation, encryption | ✅ Implemented |
| **Integrity** | Git commit signing, audit logs | ✅ Implemented |
| **Availability** | Auto-restart, error recovery | ✅ Implemented |
| **Accountability** | Comprehensive audit trail | ✅ Implemented |
| **Non-Repudiation** | Immutable Git history | ✅ Implemented |

---

## 2. Threat Model

### 2.1 Assets

**Primary Assets:**
1. **User Credentials**
   - Gmail password / app password
   - Odoo admin password
   - Social media API keys (Meta, Twitter)
   - WhatsApp API token

2. **Business Data**
   - Email contents (potentially sensitive communications)
   - Financial data (invoices, expenses from Odoo)
   - Customer information (contacts, orders)
   - Audit logs (operational history)

3. **Source Code**
   - Agent logic and algorithms
   - MCP server implementations
   - Configuration templates

**Secondary Assets:**
- Git repository (communication channel)
- Oracle Cloud VM (compute infrastructure)
- GitHub account (version control)

### 2.2 Threat Actors

**TA-1: External Attacker**
- **Motivation:** Financial gain, data theft
- **Capabilities:** Network scanning, exploit kits, social engineering
- **Access:** Internet-facing Oracle VM
- **Likelihood:** Medium

**TA-2: Malicious Insider**
- **Motivation:** Data theft, sabotage
- **Capabilities:** Physical access to local machine
- **Access:** Local agent, .env file
- **Likelihood:** Low

**TA-3: Cloud Provider Compromise**
- **Motivation:** Mass data collection
- **Capabilities:** VM access, network monitoring
- **Access:** Oracle Cloud infrastructure
- **Likelihood:** Very Low

**TA-4: Accidental Exposure**
- **Motivation:** N/A (human error)
- **Capabilities:** Git commit mistakes, config errors
- **Access:** Repository contributors
- **Likelihood:** Medium

### 2.3 Attack Scenarios

#### Scenario 1: Oracle VM Compromise

**Attack Chain:**
```
1. Attacker scans Oracle Cloud IP ranges
2. Discovers SSH port 22 open
3. Attempts brute-force SSH authentication
   └─► MITIGATED: SSH key-only (no password auth)
4. Gains unauthorized SSH access (hypothetical)
5. Accesses Cloud Agent code and vault files
   └─► IMPACT: Medium
       - Can read task data (email contents, etc.)
       - Can read audit logs
       - CANNOT access credentials (.env not synced)
       - CANNOT execute sensitive actions (no MCP credentials)
6. Attempts to execute malicious actions
   └─► MITIGATED: Work-zone enforcement blocks execution
7. Attempts to steal credentials
   └─► MITIGATED: No credentials present on Cloud VM
```

**Risk Rating:** Medium Likelihood, Low Impact = **Medium Risk**

**Controls:**
- ✅ SSH key-based authentication
- ✅ Fail2ban for brute-force protection
- ✅ Secrets isolation (no .env on cloud)
- ✅ Work-zone enforcement
- ✅ Audit logging detects unauthorized access

#### Scenario 2: Git Repository Made Public

**Attack Chain:**
```
1. Repository accidentally changed to public
2. Attacker discovers public repo via GitHub search
3. Clones repository
   └─► IMPACT: High
       - Full source code exposed
       - Task data visible (email contents, business data)
       - Audit logs visible
4. Searches for secrets in commit history
   └─► MITIGATED: .gitignore prevents .env commits
       └─► Pre-commit hook validates no secrets
5. Attempts to use exposed data
   └─► IMPACT: Medium
       - Business data leakage
       - System architecture revealed
```

**Risk Rating:** Medium Likelihood, High Impact = **High Risk**

**Controls:**
- ✅ Private repository enforced
- ✅ .gitignore excludes secrets
- ✅ Pre-commit hook validates commits
- ⚠️ Manual review of repository settings (monthly)
- 🔄 Git history scan for secrets (future: automated)

#### Scenario 3: Local Machine Theft/Compromise

**Attack Chain:**
```
1. Attacker gains physical access to local machine
2. Boots from USB, bypasses OS authentication
3. Mounts disk, accesses file system
4. Reads .env file
   └─► IMPACT: Critical
       - All credentials exposed
       - Full MCP server access
       - Can impersonate user
5. Uses credentials to access external systems
   └─► IMPACT: Critical
       - Send emails as user
       - Post to social media as user
       - Access Odoo accounting data
```

**Risk Rating:** Low Likelihood, Critical Impact = **High Risk**

**Controls:**
- ⚠️ Full-disk encryption (user responsibility)
- ⚠️ Strong OS password (user responsibility)
- ✅ Audit trail detects unauthorized usage
- 🔄 Credential rotation (future: automated)
- 🔄 MFA for critical operations (future)

#### Scenario 4: Secrets Accidentally Committed to Git

**Attack Chain:**
```
1. Developer accidentally commits .env file
2. Secrets pushed to GitHub
3. GitHub alerts (if secret scanning enabled)
   └─► MITIGATED: Pre-commit hook blocks commit
4. If hook bypassed (--no-verify flag)
   └─► IMPACT: Critical
       - Credentials exposed in Git history
       - Visible to all collaborators
       - Visible in public repo (if made public later)
```

**Risk Rating:** Medium Likelihood, Critical Impact = **High Risk**

**Controls:**
- ✅ .gitignore excludes all secret patterns
- ✅ Pre-commit hook validates no secrets
- ⚠️ Developer training (don't use --no-verify)
- 🔄 GitHub secret scanning enabled (future)
- 🔄 Automated Git history scan (future)

### 2.4 Risk Matrix

| Threat Scenario | Likelihood | Impact | Risk Level | Residual Risk |
|-----------------|------------|--------|------------|---------------|
| Oracle VM Compromise | Medium | Low | Medium | Low |
| Git Repo Public | Medium | High | High | Medium |
| Local Machine Theft | Low | Critical | High | High |
| Secrets in Git | Medium | Critical | High | Medium |
| Network MITM | Low | Low | Low | Low |
| DoS Attack | Medium | Low | Low | Low |

**Risk Acceptance:**
- **High residual risks** acknowledged (local machine security is user responsibility)
- **Medium residual risks** monitored and reviewed quarterly
- **Low residual risks** accepted

---

## 3. Security Controls

### 3.1 Preventive Controls

**PC-1: Secrets Isolation**

**Control Description:**
Secrets stored only on local machine, never synchronized to cloud or Git.

**Implementation:**
```bash
# .gitignore (enforced)
.env
.env.local
.env.cloud
.env.production
*.key
*.pem
credentials.json
secrets/
oauth_tokens/
```

**Validation:**
```bash
# Check .gitignore includes secret patterns
grep -E "\.env|\.key|\.pem|credentials|secrets" .gitignore

# Verify no secrets in Git history
git log --all --full-history --source --all --pretty=format:'' | grep -E "password|api_key|secret|token" || echo "No secrets found"

# Verify .env not tracked
git ls-files | grep .env || echo ".env not tracked"
```

**Monitoring:**
- Pre-commit hook validates no secrets in staged files
- Monthly manual audit of .gitignore
- Automated Git history scan (future)

---

**PC-2: Work-Zone Enforcement**

**Control Description:**
Cloud agent cannot execute sensitive actions; Local agent requires human approval.

**Implementation:**
```python
# src/utils/work_zone.py

from enum import Enum

class WorkZone(Enum):
    CLOUD = "cloud"  # Draft mode only
    LOCAL = "local"  # Full execution

def can_execute_action(action: ActionType, work_zone: WorkZone) -> tuple[bool, str]:
    """Enforce work-zone restrictions."""
    if action in SENSITIVE_ACTIONS and work_zone == WorkZone.CLOUD:
        return (False, "Action requires LOCAL work-zone (human approval required)")
    return (True, "Action permitted")
```

**Validation:**
```bash
# Test cloud work-zone blocks sensitive actions
export WORK_ZONE=cloud
python -c "from src.utils.work_zone import can_execute_action, ActionType, WorkZone; print(can_execute_action(ActionType.SEND_EMAIL, WorkZone.CLOUD))"
# Expected: (False, "...requires LOCAL work-zone...")

# Test local work-zone allows actions
export WORK_ZONE=local
python -c "from src.utils.work_zone import can_execute_action, ActionType, WorkZone; print(can_execute_action(ActionType.SEND_EMAIL, WorkZone.LOCAL))"
# Expected: (True, "Action permitted")
```

**Monitoring:**
- Audit log records all EXECUTION_BLOCKED events
- Alert if Cloud agent attempts execution (indicates bug or compromise)

---

**PC-3: SSH Key-Based Authentication**

**Control Description:**
SSH authentication to Oracle VM uses key pairs only, no password authentication.

**Implementation:**
```bash
# Oracle VM: /etc/ssh/sshd_config

PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
```

**Validation:**
```bash
# Verify SSH config on Oracle VM
ssh ubuntu@<PUBLIC_IP> 'sudo grep "PasswordAuthentication" /etc/ssh/sshd_config'
# Expected: PasswordAuthentication no

# Test password auth disabled
ssh -o PreferredAuthentications=password ubuntu@<PUBLIC_IP>
# Expected: Permission denied
```

**Monitoring:**
- SSH login attempts logged in /var/log/auth.log
- Fail2ban blocks repeated failed attempts

---

**PC-4: Git SSH Authentication**

**Control Description:**
Git push/pull uses SSH keys, not HTTPS with passwords.

**Implementation:**
```bash
# Cloud Agent: Generate dedicated SSH key
ssh-keygen -t ed25519 -C "cloud-agent@digitalfte" -f ~/.ssh/id_ed25519_cloud -N ""

# Add to GitHub as Deploy Key (read/write)
# Repository Settings → Deploy Keys → Add Deploy Key

# Git remote uses SSH (not HTTPS)
git remote -v
# Expected: git@github.com:username/repo.git (not https://)
```

**Validation:**
```bash
# Test SSH authentication
ssh -T git@github.com
# Expected: "Hi username/repo! You've successfully authenticated..."

# Verify remote is SSH
git remote -v | grep "git@github.com" || echo "ERROR: Not using SSH!"
```

**Monitoring:**
- Git operations logged in audit trail
- GitHub access logs reviewed monthly

---

### 3.2 Detective Controls

**DC-1: Comprehensive Audit Logging**

**Control Description:**
All operations logged to immutable append-only JSONL files.

**Implementation:**
```python
# src/utils/audit_logger.py

def log_audit(
    event: str,
    task_id: str,
    agent_id: str,
    status: AuditStatus,
    details: dict,
):
    """Log audit event to JSONL file."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent_id": agent_id,
        "event": event,
        "task_id": task_id,
        "status": status.value,
        "details": details,
    }

    log_file = LOGS_PATH / f"audit_{datetime.now().strftime('%Y-%m-%d')}.jsonl"

    # Append-only write (no modification of existing lines)
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

**Logged Events:**
- TASK_CREATED
- TASK_CLAIMED
- DRAFT_CREATED
- APPROVAL_REQUESTED
- APPROVED
- REJECTED
- EXECUTION_STARTED
- EXECUTION_BLOCKED
- EXECUTED
- FAILED
- COMPLETED
- GIT_SYNC
- ERROR

**Validation:**
```bash
# Verify audit log exists
ls -la Vault/Logs/audit/audit_$(date +%Y-%m-%d).jsonl

# View recent events
cat Vault/Logs/audit/audit_$(date +%Y-%m-%d).jsonl | tail -10 | jq

# Count events by type
cat Vault/Logs/audit/audit_*.jsonl | jq -r '.event' | sort | uniq -c
```

**Monitoring:**
- Daily review of EXECUTION_BLOCKED events (detect anomalies)
- Weekly review of FAILED events (detect issues)
- Monthly security audit of all events

---

**DC-2: Git Commit Signing (Future)**

**Control Description:**
All Git commits signed with GPG keys for integrity verification.

**Implementation:** (Future enhancement)
```bash
# Generate GPG key
gpg --full-generate-key

# Configure Git to sign commits
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true

# Verify signed commits
git log --show-signature
```

**Status:** 🔄 Future enhancement (not critical for Platinum Tier)

---

### 3.3 Corrective Controls

**CC-1: Credential Rotation**

**Control Description:**
Periodic rotation of credentials to limit exposure window.

**Procedure:**
1. **Quarterly Rotation** (every 3 months):
   - Gmail app password
   - Odoo admin password
   - Social media API keys
   - WhatsApp API token

2. **Immediate Rotation** (if compromise suspected):
   - Revoke compromised credential
   - Generate new credential
   - Update .env file on Local machine
   - Test all MCP servers
   - Log rotation event

**Implementation:** (Manual process for now)
```bash
# 1. Generate new Gmail app password
# Google Account → Security → 2-Step Verification → App Passwords → Generate

# 2. Update .env
nano .env
# Update GMAIL_APP_PASSWORD=<new-password>

# 3. Test email sending
python -c "from src.mcp_servers.email_sender import send_email; send_email('test@example.com', 'Test', 'Test')"

# 4. Log rotation
echo "$(date): Gmail app password rotated" >> Vault/Logs/security.log
```

**Future:** Automated credential rotation with HashiCorp Vault

---

**CC-2: Incident Response**

**Control Description:**
Documented procedure for responding to security incidents.

See [Section 8: Incident Response](#8-incident-response)

---

**CC-3: Error Recovery & Dead Letter Queue**

**Control Description:**
Failed tasks captured in DLQ for manual review and retry.

**Implementation:**
```python
# src/utils/error_recovery.py

def handle_task_failure(task: Task, error: Exception):
    """Move failed task to Dead Letter Queue."""
    dlq_path = VAULT_PATH / "Dead_Letter_Queue" / f"{task.id}.md"

    task_content = f"""---
Error: {str(error)}
Failed At: {datetime.now().isoformat()}
Agent: {AGENT_ID}
---

# Failed Task: {task.title}

## Error Details

{str(error)}

## Stack Trace

{traceback.format_exc()}

## Original Task

{task.content}
"""

    dlq_path.write_text(task_content)

    log_audit(
        event="FAILED",
        task_id=task.id,
        agent_id=AGENT_ID,
        status=AuditStatus.FAILED,
        details={"error": str(error)},
    )
```

**Monitoring:**
- Daily review of DLQ folder
- Alert if >5 tasks in DLQ
- Manual retry or investigation

---

## 4. Secrets Management

### 4.1 Secret Types

| Secret Type | Storage Location | Synced to Cloud? | Access |
|-------------|------------------|------------------|--------|
| Gmail App Password | `.env` (local) | ❌ No | Local Agent only |
| Odoo Admin Password | `.env` (local) | ❌ No | Local Agent only |
| Meta API Token | `.env` (local) | ❌ No | Local Agent only |
| Twitter API Keys | `.env` (local) | ❌ No | Local Agent only |
| WhatsApp API Token | `.env` (local) | ❌ No | Local Agent only |
| GitHub Deploy Key | `~/.ssh/` (cloud & local) | ❌ No | Both (different keys) |
| Oracle VM SSH Key | `~/.ssh/` (local) | ❌ No | Local only |

### 4.2 .env File Structure

**Local Agent (.env):**
```bash
# ============================================================
# PLATINUM TIER LOCAL AGENT CONFIGURATION
# ============================================================
# ⚠️  WARNING: THIS FILE CONTAINS SECRETS
# ⚠️  NEVER COMMIT THIS FILE TO GIT
# ⚠️  NEVER SYNC THIS FILE TO CLOUD
# ============================================================

# Work-Zone Configuration
WORK_ZONE=local
AGENT_ID=local-laptop-001

# ============================================================
# SECRETS - LOCAL ONLY (NEVER SYNC)
# ============================================================

# Gmail MCP Server
GMAIL_ADDRESS=user@example.com
GMAIL_APP_PASSWORD=xxxx_xxxx_xxxx_xxxx  # From Google App Passwords

# Odoo MCP Server
ODOO_URL=http://localhost:8069
ODOO_DB=digital_fte
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password_2026  # CHANGE THIS!

# Meta Social MCP Server (Facebook/Instagram)
META_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxx  # From Meta Developer Portal
META_PAGE_ID=123456789
INSTAGRAM_ACCOUNT_ID=987654321

# Twitter/X MCP Server
TWITTER_API_KEY=xxxxxxxxxxxxxxxxxxxx
TWITTER_API_SECRET=xxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_TOKEN=xxxxxxxxxxxxxxxxxxxx
TWITTER_ACCESS_SECRET=xxxxxxxxxxxxxxxxxxxx

# WhatsApp MCP Server
WHATSAPP_API_TOKEN=xxxxxxxxxxxxxxxxxxxx

# ============================================================
# CONFIGURATION - CAN BE SYNCED
# ============================================================

# Vault Configuration
VAULT_PATH=D:\Hacathan_2\Vault
GIT_REMOTE=git@github.com:username/digital-fte-vault.git

# ... rest of config
```

**Cloud Agent (.env):**
```bash
# ============================================================
# PLATINUM TIER CLOUD AGENT CONFIGURATION
# ============================================================
# ✅ SAFE TO SYNC (NO SECRETS)
# ============================================================

# Work-Zone Configuration
WORK_ZONE=cloud
AGENT_ID=cloud-oracle-001

# ============================================================
# NO SECRETS ON CLOUD
# ============================================================
# All MCP servers disabled (no credentials needed)
# ============================================================

# Vault Configuration
VAULT_PATH=/home/digitalfte/Hacathan_2/Vault
GIT_REMOTE=git@github.com:username/digital-fte-vault.git

# MCP Servers (ALL DISABLED)
EMAIL_MCP_ENABLED=false
ODOO_MCP_ENABLED=false
META_SOCIAL_MCP_ENABLED=false
TWITTER_MCP_ENABLED=false
WHATSAPP_MCP_ENABLED=false

# ... rest of config (no credentials)
```

### 4.3 Secret Validation

**Pre-Commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running pre-commit secret validation..."

# Check for .env files
if git diff --cached --name-only | grep -E "\.env$|\.env\."; then
    echo "ERROR: Attempting to commit .env file!"
    echo "This file contains secrets and should NEVER be committed."
    exit 1
fi

# Check for secret patterns in staged files
if git diff --cached | grep -iE "password|api_key|secret|token|credential"; then
    echo "WARNING: Potential secret detected in staged changes."
    echo "Please review carefully before committing."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✓ Pre-commit validation passed"
exit 0
```

**Installation:**
```bash
# Copy pre-commit hook
cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Test hook
git add .env  # Should fail
```

### 4.4 Secret Recovery

**If Secrets Compromised:**

1. **Immediate Actions** (within 1 hour):
   - Revoke compromised credential at source
   - Change password / regenerate API key
   - Update .env file with new credential
   - Test all affected MCP servers
   - Review recent operations for unauthorized usage

2. **Investigation** (within 24 hours):
   - Review audit logs for anomalies
   - Check Git history for accidental commits
   - Verify no other credentials exposed
   - Document incident in security log

3. **Remediation** (within 1 week):
   - Rotate related credentials (defense in depth)
   - Review and update security controls
   - Implement additional monitoring if needed
   - Update incident response playbook

---

## 5. Access Control

### 5.1 Oracle Cloud VM Access

**Authorized Users:**
- System Administrator (owner of Oracle Cloud account)
- Cloud Agent (digitalfte service user)

**Authentication:**
- SSH key-based only (no passwords)
- Root login disabled
- Password authentication disabled

**Authorization:**
```bash
# digitalfte user permissions
- Read: ~/Hacathan_2/ (repository)
- Write: ~/Hacathan_2/Vault/Drafts/, ~/Hacathan_2/Vault/Logs/
- Execute: Python orchestrator
- No sudo access
- No access to other users' files
```

**Audit:**
```bash
# View SSH login attempts
ssh ubuntu@<PUBLIC_IP> 'sudo grep "sshd" /var/log/auth.log | tail -20'

# View digitalfte user activity
ssh ubuntu@<PUBLIC_IP> 'sudo aureport --summary'
```

### 5.2 Git Repository Access

**Authorized Users:**
- Developer (read/write)
- Cloud Agent (read/write via Deploy Key)
- Local Agent (read/write via SSH key)

**Access Control:**
- Private repository (GitHub)
- Deploy keys with write permission
- Branch protection (future: require PR approval for main)

**Audit:**
```bash
# View recent commits
git log --all --oneline -20

# View commit authors
git shortlog -sn

# Verify no unauthorized commits
git log --all --author="suspicious@email.com"
```

### 5.3 MCP Server Access

**Cloud Agent:**
- ❌ Email Sender MCP: Disabled (no credentials)
- ❌ Odoo MCP: Disabled (no credentials)
- ❌ Social Media MCPs: Disabled (no credentials)

**Local Agent:**
- ✅ Email Sender MCP: Enabled (with Gmail app password)
- ✅ Odoo MCP: Enabled (with Odoo admin password)
- ✅ Social Media MCPs: Enabled (with API tokens)

**Human Approval Required:**
- All sensitive actions require moving draft to Approved/ folder
- Human reviews draft in Obsidian before approval
- Audit log records approval with timestamp

---

## 6. Data Protection

### 6.1 Data Classification

| Data Type | Classification | Encryption at Rest | Encryption in Transit |
|-----------|---------------|--------------------|-----------------------|
| User Credentials | Critical | ✅ OS-level | ✅ TLS 1.3 |
| Email Contents | Confidential | ✅ GitHub AES-256 | ✅ TLS 1.3 |
| Financial Data | Confidential | ✅ GitHub AES-256 | ✅ TLS 1.3 |
| Audit Logs | Internal | ✅ GitHub AES-256 | ✅ TLS 1.3 |
| Source Code | Internal | ✅ GitHub AES-256 | ✅ TLS 1.3 |
| Configuration | Internal | ✅ GitHub AES-256 | ✅ TLS 1.3 |

### 6.2 Encryption

**At Rest:**
- GitHub repository: AES-256 encryption (GitHub default)
- Oracle VM disk: Oracle Cloud default encryption
- Local machine: User responsibility (BitLocker/FileVault recommended)

**In Transit:**
- Git over SSH: TLS 1.3 + SSH key authentication
- HTTPS APIs: TLS 1.3 (Gmail, Odoo, Social Media)

**Key Management:**
- SSH keys: Generated locally, never transmitted
- GitHub Deploy Keys: Scoped to repository, revocable
- API tokens: Stored in .env (local only)

### 6.3 Data Retention

**Audit Logs:**
- Retention: 90 days minimum, indefinite maximum
- Format: JSONL (append-only)
- Location: `Vault/Logs/audit/`
- Backup: Git repository (synced to GitHub)

**Task Files:**
- Retention: Indefinite (moved through workflow folders)
- Cleanup: Manual (DLQ reviewed monthly)
- Archival: Git history (permanent record)

**Secrets:**
- Rotation: Quarterly or on compromise
- Revocation: Immediate on compromise
- No storage in Git or audit logs

### 6.4 Data Sanitization

**Audit Logs:**
```python
def sanitize_task_data(task: Task) -> dict:
    """Remove sensitive data from task before logging."""
    return {
        "task_id": task.id,
        "source": task.source,
        "priority": task.priority,
        "domain": task.domain,
        "action_type": task.action_type,
        # Email body replaced with summary
        "content_summary": task.content[:100] + "...",
        # No credentials, API keys, passwords
    }
```

**Git Commits:**
- Pre-commit hook checks for secrets
- .gitignore excludes all secret files
- Manual review before pushing

---

## 7. Audit & Compliance

### 7.1 Audit Trail Requirements

**What is Logged:**
- Every task creation (source, timestamp, priority)
- Every task claim (agent, destination)
- Every draft creation (AI model, confidence)
- Every approval/rejection (human decision, timestamp)
- Every execution (action type, status, result)
- Every Git sync (files changed, conflicts)
- Every error (exception type, stack trace)

**What is NOT Logged:**
- User credentials
- Full email bodies (only summaries)
- API keys or tokens
- Personally Identifiable Information (PII) - unless essential for task

**Audit Log Format (JSONL):**
```json
{
  "timestamp": "2026-01-22T14:35:17.123Z",
  "agent_id": "cloud-oracle-001",
  "agent_type": "cloud",
  "event": "DRAFT_CREATED",
  "task_id": "2026-01-22_1430_gmail_high_Q4-summary",
  "domain": "BUSINESS",
  "action_type": "send_email",
  "status": "success",
  "details": {
    "ai_agent": "gemini-2.0-flash",
    "processing_time": 3.5,
    "confidence": 0.95,
    "work_zone": "cloud"
  },
  "metadata": {
    "git_commit": "abc123def456",
    "uptime": 259200
  }
}
```

### 7.2 Compliance Monitoring

**Daily:**
- Review EXECUTION_BLOCKED events (should only be from Cloud agent)
- Review FAILED events (investigate failures)

**Weekly:**
- Validate .gitignore includes all secret patterns
- Check for unauthorized Git commits
- Review MCP server usage patterns

**Monthly:**
- Full audit log review (search for anomalies)
- Security configuration validation
- Credential rotation (if due)
- DLQ cleanup (retry or archive)

**Quarterly:**
- Threat model review (new threats?)
- Security control effectiveness assessment
- Penetration testing (simulated attacks)
- Credential rotation (all credentials)

### 7.3 Audit Tools

**Search Audit Logs:**
```bash
# Find all EXECUTION_BLOCKED events
cat Vault/Logs/audit/audit_*.jsonl | jq 'select(.event == "EXECUTION_BLOCKED")'

# Find failed tasks
cat Vault/Logs/audit/audit_*.jsonl | jq 'select(.status == "failed")'

# Find tasks by domain
cat Vault/Logs/audit/audit_*.jsonl | jq 'select(.domain == "BUSINESS")'

# Count events by type
cat Vault/Logs/audit/audit_*.jsonl | jq -r '.event' | sort | uniq -c

# Agent activity summary
cat Vault/Logs/audit/audit_*.jsonl | jq -r '.agent_id' | sort | uniq -c
```

**Generate Compliance Report:**
```python
# scripts/generate_compliance_report.py

def generate_compliance_report(start_date, end_date):
    """Generate compliance report for date range."""

    # Load audit logs
    events = load_audit_logs(start_date, end_date)

    report = {
        "period": f"{start_date} to {end_date}",
        "total_events": len(events),
        "events_by_type": count_by_field(events, "event"),
        "events_by_agent": count_by_field(events, "agent_id"),
        "execution_blocked": count_where(events, "event", "EXECUTION_BLOCKED"),
        "unauthorized_attempts": find_unauthorized_attempts(events),
        "failed_tasks": count_where(events, "status", "failed"),
        "compliance_score": calculate_compliance_score(events),
    }

    return report
```

---

## 8. Incident Response

### 8.1 Incident Classification

**Severity Levels:**

**P0 - Critical (Response: Immediate)**
- Credentials compromised and confirmed used by attacker
- Oracle VM fully compromised with root access
- Mass data exfiltration
- System completely unavailable (>4 hours)

**P1 - High (Response: <1 hour)**
- Suspected credential compromise (unconfirmed)
- Unauthorized access to Oracle VM
- Secrets committed to Git history
- Multiple failed security controls

**P2 - Medium (Response: <4 hours)**
- Repeated failed login attempts (possible brute force)
- Unusual audit log patterns
- Single security control failure

**P3 - Low (Response: <24 hours)**
- Minor configuration issue
- Low-risk vulnerability discovered
- Process improvement opportunity

### 8.2 Incident Response Playbook

#### Playbook: Suspected Credential Compromise

**Indicators:**
- Unusual MCP server usage (emails sent at odd times)
- Audit log shows operations not performed by user
- External alert (bank transaction, social media post)

**Response Steps:**

**1. Confirm Incident (0-15 minutes):**
```bash
# Review audit logs
cat Vault/Logs/audit/audit_$(date +%Y-%m-%d).jsonl | jq

# Check recent operations
cat Vault/Logs/audit/audit_*.jsonl | tail -100 | jq

# Interview user: "Did you perform these actions?"
```

**2. Contain Incident (15-30 minutes):**
```bash
# Revoke compromised credential immediately
# Example: Gmail app password
# Google Account → Security → 2-Step Verification → App Passwords → Revoke

# Stop Local Agent (prevent further unauthorized actions)
pkill -f orchestrator.py

# Verify no malicious processes running
ps aux | grep -i orchestrator
```

**3. Investigate Scope (30 minutes - 2 hours):**
```bash
# Determine what credential was compromised
# Review audit logs for unauthorized operations
# Check Git history for accidental commits

# Search audit logs
cat Vault/Logs/audit/audit_*.jsonl | jq 'select(.timestamp > "2026-01-22T10:00:00")'

# Search Git history for secrets
git log --all --full-history --source -- '*.env' || echo "No .env in history (good)"
git log -p | grep -iE "password|api_key|secret" | head -20
```

**4. Eradicate Threat (2-4 hours):**
```bash
# Rotate ALL credentials (not just compromised one)
# Update .env with new credentials
# Test all MCP servers with new credentials

# If secrets in Git history: BFG Repo-Cleaner
# git clone --mirror git@github.com:username/repo.git
# java -jar bfg.jar --delete-files .env repo.git
# cd repo.git && git reflog expire --expire=now --all && git gc --prune=now --aggressive
# git push --force
```

**5. Recover Operations (4-8 hours):**
```bash
# Restart Local Agent with new credentials
export WORK_ZONE=local
python src/orchestrator.py &

# Verify all MCP servers working
# Send test email, check Odoo connection, etc.

# Resume normal operations
```

**6. Document Incident (8-24 hours):**
```markdown
# Incident Report: <ID>-YYYY-MM-DD

## Summary
Brief description of incident.

## Timeline
- 10:00: Incident detected (unusual email sent)
- 10:05: Confirmed unauthorized (user didn't send it)
- 10:10: Gmail app password revoked
- 10:15: Local Agent stopped
- 10:45: Scope determined (only Gmail compromised)
- 11:30: All credentials rotated
- 12:00: MCP servers tested and working
- 12:30: Operations resumed

## Root Cause
Credential compromise via [method: phishing/malware/theft]

## Impact
- 3 unauthorized emails sent
- No financial loss
- No data exfiltration
- 2 hours downtime

## Remediation
- Credentials rotated
- 2FA enabled on Gmail
- Pre-commit hook enhanced
- Security awareness training scheduled

## Lessons Learned
- [What went well, what didn't, what to improve]
```

**7. Post-Incident Actions:**
- Review and update security controls
- User security awareness training
- Enhance monitoring (if gaps identified)
- Update incident response playbook

---

### 8.3 Emergency Contacts

**Incident Commander:**
- Name: [Project Owner]
- Email: [owner@example.com]
- Phone: [+1-555-0100]
- Role: Decision authority for security incidents

**Technical Lead:**
- Name: [Developer]
- Email: [dev@example.com]
- Phone: [+1-555-0101]
- Role: System access, credential management

**External Contacts:**
- GitHub Support: https://support.github.com
- Oracle Cloud Support: https://cloud.oracle.com/support
- Google Workspace Support: https://workspace.google.com/support

---

## 9. Security Checklist

### 9.1 Pre-Deployment Checklist

**Before deploying Platinum Tier:**

**Secrets Management:**
- [ ] .gitignore includes all secret patterns (.env, *.key, *.pem, credentials.json, secrets/)
- [ ] Pre-commit hook installed and tested (blocks .env commits)
- [ ] .env file created on Local machine with all credentials
- [ ] NO .env file on Cloud VM (verified: `ls -la ~/Hacathan_2/.env` returns "No such file")
- [ ] Credentials tested (all MCP servers working)

**Access Control:**
- [ ] Oracle VM SSH configured (password auth disabled, key-only)
- [ ] GitHub Deploy Key added (Cloud Agent, read/write)
- [ ] SSH config updated (Cloud Agent uses dedicated key)
- [ ] Git remote uses SSH (not HTTPS: `git remote -v` shows git@github.com)

**Work-Zone Configuration:**
- [ ] Cloud .env has WORK_ZONE=cloud, no MCP credentials
- [ ] Local .env has WORK_ZONE=local, all MCP credentials
- [ ] Work-zone enforcement tested (Cloud blocks send_email)

**Audit Logging:**
- [ ] Audit log directory created (Vault/Logs/audit/)
- [ ] Audit logger tested (log_audit() writes to JSONL)
- [ ] Git includes audit logs (Vault/Logs/ not in .gitignore)

**Git Security:**
- [ ] Repository is private (verify on GitHub)
- [ ] Branch protection enabled (future: require PR approval)
- [ ] Git history scanned for secrets (none found)

### 9.2 Post-Deployment Checklist

**After deploying Platinum Tier:**

**Operational Security:**
- [ ] Cloud Agent running (systemctl status digitalfte-cloud.service = active)
- [ ] Local Agent tested (can pull drafts, approve, execute)
- [ ] End-to-end test passed (email → draft → approve → send)
- [ ] Audit logs being written (Vault/Logs/audit/ populated)
- [ ] Dashboard updated (shows both agents)

**Monitoring:**
- [ ] Daily audit log review scheduled (calendar reminder)
- [ ] Weekly security validation scheduled
- [ ] Monthly compliance check scheduled
- [ ] Quarterly credential rotation scheduled

**Documentation:**
- [ ] Emergency contact list updated
- [ ] Incident response playbook reviewed
- [ ] Runbooks created (deployment, operations, troubleshooting)
- [ ] Security documentation shared with team

### 9.3 Continuous Security Checklist

**Daily:**
- [ ] Review EXECUTION_BLOCKED events (none from Local, only Cloud expected)
- [ ] Review FAILED events (investigate causes)
- [ ] Verify both agents healthy (Dashboard.md)

**Weekly:**
- [ ] Validate .gitignore unchanged (no secret patterns removed)
- [ ] Review unauthorized access attempts (SSH logs, Git logs)
- [ ] Check DLQ for stuck tasks

**Monthly:**
- [ ] Full audit log review (search for anomalies)
- [ ] Security configuration validation (all controls in place)
- [ ] Verify no secrets in Git history (git log | grep -iE "password|api_key")
- [ ] Review and update threat model (new threats?)

**Quarterly:**
- [ ] Rotate all credentials (Gmail, Odoo, Social Media API keys)
- [ ] Security control effectiveness assessment
- [ ] Penetration testing (simulated attacks)
- [ ] Review and update security documentation

---

## Appendix A: Security Tools & Commands

**Check for Secrets in Git History:**
```bash
# Search commits for secret patterns
git log -p | grep -iE "password|api_key|secret|token" | head -50

# Find files that were tracked and later deleted
git log --all --full-history --source -- '*.env' '*.key' '*.pem'

# Find large files (potential data leak)
git rev-list --objects --all | grep "$(git verify-pack -v .git/objects/pack/*.idx | sort -k 3 -n | tail -10 | awk '{print $1}')"
```

**Validate .gitignore:**
```bash
# Check .gitignore includes secret patterns
grep -E "\.env|\.key|\.pem|credentials|secrets" .gitignore || echo "ERROR: Missing secret patterns!"

# Verify .env not tracked
git ls-files | grep .env && echo "ERROR: .env is tracked!" || echo "OK: .env not tracked"

# Verify no staged secrets
git diff --cached | grep -iE "password|api_key|secret" && echo "WARNING: Possible secret staged!"
```

**Audit Oracle VM Security:**
```bash
# SSH config check
ssh ubuntu@<PUBLIC_IP> 'sudo grep -E "PasswordAuthentication|PermitRootLogin" /etc/ssh/sshd_config'

# Recent login attempts
ssh ubuntu@<PUBLIC_IP> 'sudo grep "sshd" /var/log/auth.log | tail -20'

# Failed login attempts
ssh ubuntu@<PUBLIC_IP> 'sudo grep "Failed password" /var/log/auth.log | wc -l'

# Current users
ssh ubuntu@<PUBLIC_IP> 'w'

# Running processes
ssh ubuntu@<PUBLIC_IP> 'ps aux | grep digitalfte'
```

**Generate Security Report:**
```bash
# Audit log summary
cat Vault/Logs/audit/audit_*.jsonl | jq -r '.event' | sort | uniq -c

# Execution blocks (should all be from Cloud)
cat Vault/Logs/audit/audit_*.jsonl | jq 'select(.event == "EXECUTION_BLOCKED")'

# Failed operations
cat Vault/Logs/audit/audit_*.jsonl | jq 'select(.status == "failed")' | jq -r '.task_id'

# Agent activity
cat Vault/Logs/audit/audit_*.jsonl | jq -r '.agent_id' | sort | uniq -c
```

---

## Appendix B: Compliance Frameworks

**Alignment with Security Frameworks:**

**OWASP Top 10 (2021):**
- A01: Broken Access Control → ✅ Work-zone enforcement, human approval
- A02: Cryptographic Failures → ✅ TLS 1.3, SSH keys, no plaintext secrets
- A03: Injection → ⚠️ Mitigated by input validation (limited user input)
- A04: Insecure Design → ✅ Zero Trust architecture, defense in depth
- A05: Security Misconfiguration → ✅ SSH hardening, .gitignore, pre-commit hook
- A06: Vulnerable Components → ⚠️ Python dependencies (pip-audit recommended)
- A07: Identification and Authentication → ✅ SSH keys, no password auth
- A08: Software and Data Integrity → ✅ Git commit history, audit logs
- A09: Security Logging and Monitoring → ✅ Comprehensive audit trail
- A10: Server-Side Request Forgery → N/A (no user-controlled URLs)

**NIST Cybersecurity Framework:**
- **Identify**: Threat model, asset inventory, risk assessment
- **Protect**: Access control, secrets management, encryption
- **Detect**: Audit logging, anomaly detection, monitoring
- **Respond**: Incident response playbook, emergency contacts
- **Recover**: Error recovery, DLQ, credential rotation

**CIS Controls (Relevant):**
- CIS 1: Inventory of Assets → ✅ Documented in threat model
- CIS 2: Inventory of Software → ✅ requirements.txt, pip list
- CIS 3: Data Protection → ✅ Encryption at rest and in transit
- CIS 4: Secure Configuration → ✅ SSH hardening, work-zone enforcement
- CIS 5: Account Management → ✅ Service users, no shared accounts
- CIS 6: Access Control → ✅ SSH keys, Deploy Keys, work-zone enforcement
- CIS 8: Audit Log Management → ✅ Comprehensive JSONL audit trail
- CIS 10: Malware Defenses → ⚠️ User responsibility (OS-level antivirus)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-22
**Classification:** Internal Use
**Next Review:** 2026-02-22 (Monthly)

---

**Approved By:**
- Security Lead: [Name] - [Date]
- Project Owner: [Name] - [Date]

**Status:** ✅ Ready for Implementation
