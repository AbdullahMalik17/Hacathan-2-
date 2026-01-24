# Platinum Tier Operations Manual

**Version:** 1.0
**Date:** 2026-01-22
**Status:** Production Ready
**Audience:** System Operators, Developers

---

## Table of Contents

1. [Quick Reference](#1-quick-reference)
2. [System Operations](#2-system-operations)
3. [Deployment Procedures](#3-deployment-procedures)
4. [Monitoring & Health Checks](#4-monitoring--health-checks)
5. [Troubleshooting Guide](#5-troubleshooting-guide)
6. [Maintenance Tasks](#6-maintenance-tasks)
7. [Disaster Recovery](#7-disaster-recovery)
8. [Performance Tuning](#8-performance-tuning)

---

## 1. Quick Reference

### 1.1 Essential Commands

**Cloud Agent (Oracle VM):**
```bash
# SSH access
ssh ubuntu@<PUBLIC_IP>

# Check service status
sudo systemctl status digitalfte-cloud.service

# View live logs
sudo journalctl -u digitalfte-cloud.service -f

# Restart service
sudo systemctl restart digitalfte-cloud.service

# Stop service (for maintenance)
sudo systemctl stop digitalfte-cloud.service

# Start service
sudo systemctl start digitalfte-cloud.service
```

**Local Agent:**
```bash
# Start agent
cd D:\Hacathan_2
python src\orchestrator.py

# Or use startup script
.\Start_Local_Agent.ps1

# Stop agent
# Press Ctrl+C or:
pkill -f orchestrator.py

# View logs
tail -f logs/orchestrator.log
```

**Common Tasks:**
```bash
# Check Git sync status
git status
git log -5 --oneline

# View Dashboard
cat Vault\Dashboard.md

# View recent audit events
cat Vault\Logs\audit\audit_$(date +%Y-%m-%d).jsonl | tail -20 | jq

# Check pending drafts
ls Vault\Drafts\

# Check DLQ for failed tasks
ls Vault\Dead_Letter_Queue\
```

### 1.2 Emergency Contacts

**Escalation Path:**
1. **First Responder**: On-call engineer (check Dashboard for issues)
2. **Escalation**: Technical Lead (if persistent issues)
3. **Critical Incident**: Project Owner + Security Team

**External Support:**
- **Oracle Cloud**: https://cloud.oracle.com/support
- **GitHub**: https://support.github.com
- **Google Workspace**: https://workspace.google.com/support

### 1.3 System Health Dashboard

**Access:** `Vault/Dashboard.md` (auto-updated every 60s)

**Key Metrics:**
- Agent Status (HEALTHY / DEGRADED / UNHEALTHY)
- Task Processing (processed, failed, pending)
- Resource Usage (CPU, memory, disk)
- Git Sync Status (last sync, failures)

**Alert Thresholds:**
- ⚠️ Warning: Failure rate >20%, Disk >80%
- 🚨 Critical: Agent down >5 min, Failure rate >50%, Disk >95%

---

## 2. System Operations

### 2.1 Starting the System

**Prerequisites:**
- Oracle Cloud VM running and accessible
- Local machine powered on
- Internet connectivity
- Git repository accessible

**Startup Sequence:**

**Step 1: Verify Cloud Agent Running**
```bash
# SSH to Oracle VM
ssh ubuntu@<PUBLIC_IP>

# Check service status
sudo systemctl status digitalfte-cloud.service

# If not running, start it
sudo systemctl start digitalfte-cloud.service

# Verify logs show normal operation
sudo journalctl -u digitalfte-cloud.service -n 50

# Expected: "Orchestrator initialized in cloud work-zone"
```

**Step 2: Pull Latest Changes (Local)**
```bash
# On local machine
cd D:\Hacathan_2

# Pull latest changes from Cloud
git pull origin main

# Verify no conflicts
git status
```

**Step 3: Start Local Agent**
```bash
# Option A: Direct invocation
export WORK_ZONE=local  # Linux/Mac
$env:WORK_ZONE="local"  # Windows PowerShell
python src/orchestrator.py

# Option B: Startup script (Windows)
.\Start_Local_Agent.ps1

# Option C: Startup script (Linux/Mac)
./start_local_agent.sh
```

**Step 4: Verify Both Agents Healthy**
```bash
# Check Dashboard
cat Vault/Dashboard.md

# Expected: Both Cloud and Local agents show "HEALTHY"
# Expected: Recent activity from both agents
```

**Verification Checklist:**
- [ ] Cloud Agent running (systemctl status = active)
- [ ] Local Agent running (process visible in Task Manager/htop)
- [ ] Git sync working (recent commits from both agents)
- [ ] Watchers active (Dashboard shows last check times)
- [ ] No alerts in Dashboard

**Typical Startup Time:** 2-3 minutes

---

### 2.2 Stopping the System

**Shutdown Sequence:**

**Step 1: Stop Local Agent (Graceful)**
```bash
# If running interactively, press Ctrl+C

# If running as background process
pkill -TERM -f orchestrator.py

# Wait for graceful shutdown (up to 30s)
sleep 30

# Verify stopped
ps aux | grep orchestrator.py
# Expected: No processes found
```

**Step 2: Git Push Final State (Local)**
```bash
# Ensure all changes committed
cd D:\Hacathan_2
git add Approved/ Done/ Logs/
git commit -m "shutdown: final state before stopping local agent"
git push origin main
```

**Step 3: Stop Cloud Agent (If Needed)**
```bash
# SSH to Oracle VM
ssh ubuntu@<PUBLIC_IP>

# Stop service
sudo systemctl stop digitalfte-cloud.service

# Verify stopped
sudo systemctl status digitalfte-cloud.service
# Expected: "inactive (dead)"
```

**When to Stop Cloud Agent:**
- Maintenance window (OS updates, hardware maintenance)
- Emergency shutdown (security incident)
- End of project (permanent shutdown)

**When NOT to Stop Cloud Agent:**
- Normal operation (designed to run 24/7)
- Local machine offline (Cloud should continue monitoring)
- Git sync issues (troubleshoot instead of stopping)

---

### 2.3 Restarting the System

**When to Restart:**
- After configuration changes (environment variables)
- After software updates (new code deployed)
- To recover from errors (if health checks failing)
- After credential rotation

**Restart Sequence:**

**Cloud Agent:**
```bash
ssh ubuntu@<PUBLIC_IP>
sudo systemctl restart digitalfte-cloud.service

# Verify restart successful
sudo systemctl status digitalfte-cloud.service
# Expected: "active (running)" with recent start time

# Check logs for errors
sudo journalctl -u digitalfte-cloud.service -n 50
# Expected: "Orchestrator initialized in cloud work-zone"
```

**Local Agent:**
```bash
# Stop (if running)
pkill -f orchestrator.py

# Pull latest changes
cd D:\Hacathan_2
git pull origin main

# Restart
python src/orchestrator.py &

# Or use startup script
.\Start_Local_Agent.ps1
```

**Verification After Restart:**
- [ ] No errors in logs (first 60 seconds)
- [ ] Git sync working (Dashboard shows recent sync)
- [ ] Watchers active (Dashboard shows recent checks)
- [ ] Dashboard updated (timestamp within 60s)

**Downtime:** <30 seconds (Cloud), <60 seconds (Local)

---

## 3. Deployment Procedures

### 3.1 Initial Deployment

**Objective:** Deploy Platinum Tier from scratch

**Time Required:** 4-6 hours

**Prerequisites:**
- Oracle Cloud account (free tier)
- GitHub account
- Gmail account with app password
- Local development machine (Windows/Mac/Linux)

**Deployment Steps:**

See `docs/PLATINUM_DEPLOYMENT.md` for complete step-by-step guide.

**Summary:**
1. Provision Oracle Cloud VM (1-2h)
2. Configure SSH access and security
3. Install Python and dependencies
4. Clone Git repository
5. Configure environment (.env files)
6. Set up systemd service (Cloud)
7. Test both agents
8. Verify end-to-end workflow

---

### 3.2 Code Updates

**Objective:** Deploy code changes to production

**Frequency:** As needed (bug fixes, new features)

**Procedure:**

**Step 1: Test Locally**
```bash
# On local machine
cd D:\Hacathan_2

# Pull latest code
git pull origin main

# Run tests
pytest tests/ -v

# Verify all tests pass
```

**Step 2: Commit Changes**
```bash
# Stage changes
git add src/ tests/

# Commit with clear message
git commit -m "feat: implement <feature>"

# Push to remote
git push origin main
```

**Step 3: Deploy to Cloud**
```bash
# SSH to Oracle VM
ssh ubuntu@<PUBLIC_IP>

# Navigate to repo
cd ~/Hacathan_2

# Pull latest code
git pull origin main

# Restart service
sudo systemctl restart digitalfte-cloud.service

# Verify no errors
sudo journalctl -u digitalfte-cloud.service -n 50
```

**Step 4: Deploy to Local**
```bash
# Already pulled in Step 1

# Restart Local Agent
pkill -f orchestrator.py
python src/orchestrator.py &
```

**Rollback Procedure (If Issues):**
```bash
# Revert to previous commit
git revert HEAD

# Or reset to specific commit
git reset --hard <previous-commit-sha>

# Push rollback
git push origin main --force

# Restart agents (both Cloud and Local)
```

---

### 3.3 Configuration Changes

**Objective:** Update environment variables or configuration

**Common Changes:**
- API credentials rotation
- Work-zone settings
- Watcher poll intervals
- Resource limits

**Procedure:**

**Cloud Agent Configuration:**
```bash
# SSH to Oracle VM
ssh ubuntu@<PUBLIC_IP>

# Edit environment file
nano ~/Hacathan_2/.env

# Modify variables (e.g., increase LOOP_INTERVAL)
# LOOP_INTERVAL=60  # Change from 30 to 60 seconds

# Save and exit (Ctrl+X, Y, Enter)

# Restart service to apply changes
sudo systemctl restart digitalfte-cloud.service

# Verify changes applied
sudo journalctl -u digitalfte-cloud.service | grep "LOOP_INTERVAL"
```

**Local Agent Configuration:**
```bash
# On local machine
cd D:\Hacathan_2

# Edit environment file
notepad .env  # Windows
nano .env     # Linux/Mac

# Modify variables

# Restart agent
pkill -f orchestrator.py
python src/orchestrator.py &
```

**Systemd Service Configuration (Cloud):**
```bash
# SSH to Oracle VM
ssh ubuntu@<PUBLIC_IP>

# Edit service file
sudo nano /etc/systemd/system/digitalfte-cloud.service

# Modify (e.g., change resource limits)
# MemoryLimit=16G  # Increase from 8G

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart digitalfte-cloud.service
```

---

## 4. Monitoring & Health Checks

### 4.1 Real-Time Monitoring

**Dashboard (Vault/Dashboard.md):**
- **Update Frequency:** Every 60 seconds
- **Access:** Open in Obsidian or text editor
- **Key Metrics:**
  - Agent Status: HEALTHY / DEGRADED / UNHEALTHY
  - Task Metrics: Processed, failed, pending counts
  - Resource Usage: CPU, memory, disk percentages
  - Git Sync: Last sync time, failures

**How to Monitor:**
```bash
# View Dashboard
cat Vault/Dashboard.md

# Continuously monitor (updates every 60s)
watch -n 60 cat Vault/Dashboard.md
```

**Cloud Agent Logs:**
```bash
# SSH to Oracle VM
ssh ubuntu@<PUBLIC_IP>

# View live logs
sudo journalctl -u digitalfte-cloud.service -f

# View recent errors
sudo journalctl -u digitalfte-cloud.service -p err -n 50

# View logs for specific time range
sudo journalctl -u digitalfte-cloud.service --since "1 hour ago"
```

**Local Agent Logs:**
```bash
# View live logs (if logging to file)
tail -f logs/orchestrator.log

# Or view stdout if running interactively
# (logs appear in terminal)
```

---

### 4.2 Health Check Scripts

**Cloud Agent Health Check:**
```bash
#!/bin/bash
# check_cloud_agent.sh

echo "=== Cloud Agent Health Check ==="

# Check service status
if systemctl is-active --quiet digitalfte-cloud.service; then
    echo "✓ Service: Running"
else
    echo "✗ Service: NOT RUNNING"
    exit 1
fi

# Check recent activity (logs within last 5 minutes)
if journalctl -u digitalfte-cloud.service --since "5 minutes ago" | grep -q "Git sync"; then
    echo "✓ Activity: Recent git sync detected"
else
    echo "⚠ Activity: No recent git sync (may be idle)"
fi

# Check resource usage
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM=$(free | grep Mem | awk '{print ($3/$2) * 100.0}' | cut -d'.' -f1)
DISK=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)

echo "✓ Resources: CPU ${CPU}%, Memory ${MEM}%, Disk ${DISK}%"

if (( $(echo "$DISK > 90" | bc -l) )); then
    echo "⚠ WARNING: Disk usage high (${DISK}%)"
fi

echo "=== Health Check Complete ==="
```

**Local Agent Health Check:**
```bash
#!/bin/bash
# check_local_agent.sh

echo "=== Local Agent Health Check ==="

# Check if process running
if pgrep -f orchestrator.py > /dev/null; then
    echo "✓ Process: Running"
    PID=$(pgrep -f orchestrator.py)
    echo "  PID: $PID"
else
    echo "✗ Process: NOT RUNNING"
    exit 1
fi

# Check Git sync status
cd D:\Hacathan_2
if git status | grep -q "Your branch is up to date"; then
    echo "✓ Git: Synced with remote"
else
    echo "⚠ Git: Out of sync (pull needed)"
fi

# Check recent activity in Dashboard
if grep -q "$(date +%Y-%m-%d)" Vault/Dashboard.md; then
    echo "✓ Dashboard: Updated today"
else
    echo "⚠ Dashboard: Not updated today"
fi

echo "=== Health Check Complete ==="
```

**Automated Health Monitoring (Cron Job):**
```bash
# Add to crontab (Linux/Mac)
# crontab -e

# Run health check every 5 minutes, log results
*/5 * * * * /home/digitalfte/check_cloud_agent.sh >> /home/digitalfte/health_check.log 2>&1

# Alert if health check fails
*/5 * * * * /home/digitalfte/check_cloud_agent.sh || echo "Cloud Agent unhealthy at $(date)" | mail -s "ALERT: Cloud Agent Down" admin@example.com
```

---

### 4.3 Performance Metrics

**Key Performance Indicators (KPIs):**

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| **Task Processing Rate** | >10/hour | <5/hour | <1/hour |
| **Task Failure Rate** | <5% | 5-20% | >20% |
| **Git Sync Latency** | <30s | 30-60s | >60s |
| **CPU Usage** | <50% | 50-80% | >80% |
| **Memory Usage** | <60% | 60-90% | >90% |
| **Disk Usage** | <70% | 70-90% | >90% |
| **Agent Uptime** | 99.5% | 99-99.5% | <99% |

**How to Measure:**

**Task Processing Rate:**
```bash
# Count tasks processed in last hour
cat Vault/Logs/audit/audit_$(date +%Y-%m-%d).jsonl | \
    jq -r 'select(.event == "COMPLETED") | .timestamp' | \
    grep "$(date +%Y-%m-%dT%H)" | \
    wc -l
```

**Task Failure Rate:**
```bash
# Calculate failure rate (last 24h)
COMPLETED=$(cat Vault/Logs/audit/audit_*.jsonl | jq -r 'select(.event == "COMPLETED")' | wc -l)
FAILED=$(cat Vault/Logs/audit/audit_*.jsonl | jq -r 'select(.event == "FAILED")' | wc -l)
TOTAL=$((COMPLETED + FAILED))
FAILURE_RATE=$(echo "scale=2; $FAILED / $TOTAL * 100" | bc)
echo "Failure Rate: ${FAILURE_RATE}%"
```

**Git Sync Latency:**
```bash
# Check time between commits (Cloud and Local)
# (Average time for changes to propagate)
# Manual measurement: Create test file, measure time until appears on other agent
```

**Resource Usage:**
```bash
# Cloud Agent (SSH to Oracle VM)
ssh ubuntu@<PUBLIC_IP> 'top -bn1 | head -20'

# CPU
ssh ubuntu@<PUBLIC_IP> 'top -bn1 | grep Cpu | awk "{print \$2}"'

# Memory
ssh ubuntu@<PUBLIC_IP> 'free -h | grep Mem'

# Disk
ssh ubuntu@<PUBLIC_IP> 'df -h /'
```

---

## 5. Troubleshooting Guide

### 5.1 Common Issues

#### Issue 1: Cloud Agent Not Starting

**Symptoms:**
- `systemctl status digitalfte-cloud.service` shows "failed"
- No recent logs in journalctl
- Dashboard shows Cloud agent as "UNHEALTHY" or missing

**Diagnosis:**
```bash
# Check service status
ssh ubuntu@<PUBLIC_IP> 'sudo systemctl status digitalfte-cloud.service'

# View error logs
ssh ubuntu@<PUBLIC_IP> 'sudo journalctl -u digitalfte-cloud.service -n 100'

# Look for error patterns:
# - "ModuleNotFoundError" → Missing dependencies
# - "PermissionError" → File permissions issue
# - "Connection refused" → Network issue
```

**Solutions:**

**Missing Dependencies:**
```bash
# SSH to Oracle VM
ssh ubuntu@<PUBLIC_IP>

# Reinstall dependencies
cd ~/Hacathan_2
source .venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart digitalfte-cloud.service
```

**File Permissions:**
```bash
# Fix ownership
ssh ubuntu@<PUBLIC_IP>
sudo chown -R digitalfte:digitalfte ~/Hacathan_2

# Fix vault permissions
chmod 755 ~/Hacathan_2/Vault
chmod 644 ~/Hacathan_2/Vault/**/*.md

# Restart service
sudo systemctl restart digitalfte-cloud.service
```

**Configuration Error:**
```bash
# Check .env file exists and is valid
ssh ubuntu@<PUBLIC_IP>
cat ~/Hacathan_2/.env | grep WORK_ZONE
# Expected: WORK_ZONE=cloud

# Verify no syntax errors in Python code
cd ~/Hacathan_2
source .venv/bin/activate
python -c "from src.orchestrator import Orchestrator"
# Expected: No errors
```

---

#### Issue 2: Git Sync Failures

**Symptoms:**
- Dashboard shows "Git sync failures: X"
- Audit log shows "GIT_SYNC" events with "success: false"
- Changes not propagating between Cloud and Local

**Diagnosis:**
```bash
# Check Git status
cd D:\Hacathan_2  # Or ~/Hacathan_2 on Cloud
git status

# Look for:
# - "Your branch is behind" → Need to pull
# - "Your branch is ahead" → Need to push
# - "You have unmerged paths" → Merge conflict
# - "fatal: unable to access" → Network issue

# Check Git remote
git remote -v
# Expected: git@github.com:username/repo.git
```

**Solutions:**

**Merge Conflict:**
```bash
# View conflicts
git status | grep "both modified"

# Auto-resolve (Local wins)
git checkout --ours <conflicted-file>
git add <conflicted-file>
git rebase --continue

# Or abort and retry
git rebase --abort
git pull origin main --rebase
```

**Network Issue:**
```bash
# Test GitHub SSH connection
ssh -T git@github.com
# Expected: "Hi username/repo! You've successfully authenticated..."

# If fails, check SSH key
cat ~/.ssh/id_ed25519_cloud.pub  # Cloud
cat ~/.ssh/id_rsa.pub            # Local

# Verify key added to GitHub Deploy Keys
```

**Permission Issue:**
```bash
# Check GitHub Deploy Key has write permission
# GitHub → Repository Settings → Deploy Keys
# Verify: "Read/Write" permission enabled

# If not, remove and re-add with write permission
```

---

#### Issue 3: Drafts Not Appearing on Local

**Symptoms:**
- Cloud Agent creates drafts (visible in Cloud VM)
- Local Agent pulls from Git (no errors)
- Drafts folder empty on Local machine

**Diagnosis:**
```bash
# Check Cloud Agent created draft
ssh ubuntu@<PUBLIC_IP> 'ls -la ~/Hacathan_2/Vault/Drafts/'
# Expected: Draft files present

# Check Cloud Agent pushed to Git
ssh ubuntu@<PUBLIC_IP> 'cd ~/Hacathan_2 && git log -1 --oneline'
# Expected: Recent commit with "draft:" prefix

# Check Local Agent pulled
cd D:\Hacathan_2
git log -1 --oneline
# Expected: Same commit as Cloud

# Check Drafts folder on Local
ls -la Vault\Drafts\
# If empty: Git didn't sync files
```

**Solutions:**

**Git Not Syncing Files:**
```bash
# Force pull (may lose local changes)
git fetch origin main
git reset --hard origin/main

# Verify files now present
ls -la Vault\Drafts\
```

**Git Ignored Drafts Folder:**
```bash
# Check .gitignore
cat .gitignore | grep Drafts
# Expected: No match (Drafts should NOT be in .gitignore)

# If Drafts is ignored, remove from .gitignore
nano .gitignore
# Remove "Drafts/" line if present

# Add and commit Drafts
git add Vault/Drafts/
git commit -m "fix: track Drafts folder"
git push origin main
```

---

#### Issue 4: High Failure Rate

**Symptoms:**
- Dashboard shows ">20% failure rate"
- Many tasks in Dead Letter Queue
- Audit log shows frequent "FAILED" events

**Diagnosis:**
```bash
# Review failed tasks
cat Vault/Logs/audit/audit_*.jsonl | jq 'select(.event == "FAILED")'

# Look for patterns:
# - Same action_type failing (e.g., all "send_email" fail)
# - Same error message (e.g., "Authentication failed")
# - Specific agent failing (Cloud vs Local)

# Check DLQ for details
ls -la Vault/Dead_Letter_Queue/
cat Vault/Dead_Letter_Queue/<failed-task>.md
```

**Solutions:**

**Credential Issue:**
```bash
# Test MCP server credentials
# Example: Email MCP
python -c "
from src.mcp_servers.email_sender import test_connection
test_connection()
"

# If fails: Rotate credential
# Update .env with new credential
nano .env
# GMAIL_APP_PASSWORD=<new-password>

# Restart agent
pkill -f orchestrator.py
python src/orchestrator.py &
```

**MCP Server Bug:**
```bash
# Review MCP server logs
cat logs/mcp_server.log

# Test MCP server in isolation
python src/mcp_servers/email_sender.py --test

# If bug found: Fix code, commit, deploy
git add src/mcp_servers/
git commit -m "fix: resolve email MCP issue"
git push origin main
```

**Network Issue:**
```bash
# Test external API connectivity
curl -I https://gmail.com
curl -I https://api.twitter.com

# If fails: Check firewall, VPN, network settings
```

---

### 5.2 Diagnostic Tools

**Log Analysis:**
```bash
# Find errors in logs (last 24h)
sudo journalctl -u digitalfte-cloud.service --since "24 hours ago" -p err

# Find specific error message
sudo journalctl -u digitalfte-cloud.service | grep "ConnectionError"

# Count error frequency
sudo journalctl -u digitalfte-cloud.service | grep "ERROR" | wc -l
```

**Git Diagnostics:**
```bash
# Check repository integrity
git fsck --full

# View file history (if file missing)
git log --all --full-history -- Vault/Drafts/<file>.md

# View all branches
git branch -a

# View remote tracking
git remote show origin
```

**System Diagnostics:**
```bash
# Check disk I/O (if slow)
ssh ubuntu@<PUBLIC_IP> 'iostat -x 5'

# Check network latency (if Git slow)
ping github.com
traceroute github.com

# Check DNS resolution
nslookup github.com
```

---

## 6. Maintenance Tasks

### 6.1 Daily Maintenance

**Time Required:** 5-10 minutes

**Tasks:**
1. **Check Dashboard** (2 min)
   ```bash
   cat Vault/Dashboard.md
   # Verify: Both agents HEALTHY, no alerts
   ```

2. **Review Audit Log** (3 min)
   ```bash
   # Check for EXECUTION_BLOCKED events (should be from Cloud only)
   cat Vault/Logs/audit/audit_$(date +%Y-%m-%d).jsonl | \
       jq 'select(.event == "EXECUTION_BLOCKED")'

   # Check for FAILED events
   cat Vault/Logs/audit/audit_$(date +%Y-%m-%d).jsonl | \
       jq 'select(.event == "FAILED")'
   ```

3. **Check DLQ** (2 min)
   ```bash
   # Count failed tasks
   ls Vault/Dead_Letter_Queue/ | wc -l

   # If >5 tasks, investigate
   cat Vault/Dead_Letter_Queue/<task>.md
   ```

4. **Verify Git Sync** (1 min)
   ```bash
   git status
   # Expected: "Your branch is up to date with 'origin/main'"
   ```

---

### 6.2 Weekly Maintenance

**Time Required:** 30-45 minutes

**Tasks:**
1. **Security Validation** (10 min)
   ```bash
   # Verify .gitignore unchanged
   git diff origin/main -- .gitignore
   # Expected: No changes

   # Verify no secrets in Git
   git log -p | grep -iE "password|api_key" | head -20
   # Expected: No secrets found

   # Check unauthorized access
   ssh ubuntu@<PUBLIC_IP> 'sudo grep "Failed password" /var/log/auth.log | tail -20'
   # Expected: No failed attempts (or very few)
   ```

2. **Performance Review** (10 min)
   ```bash
   # Calculate metrics for last 7 days
   # Task processing rate
   # Failure rate
   # Resource usage trends

   # View resource usage over time
   ssh ubuntu@<PUBLIC_IP> 'sar -u 1 10'  # CPU
   ssh ubuntu@<PUBLIC_IP> 'sar -r 1 10'  # Memory
   ```

3. **Log Rotation** (5 min)
   ```bash
   # Archive old audit logs (>30 days)
   find Vault/Logs/audit/ -name "audit_*.jsonl" -mtime +30 -exec gzip {} \;

   # Delete very old logs (>90 days)
   find Vault/Logs/audit/ -name "audit_*.jsonl.gz" -mtime +90 -delete
   ```

4. **DLQ Cleanup** (10 min)
   ```bash
   # Review failed tasks
   ls -la Vault/Dead_Letter_Queue/

   # Retry manually or move to archive
   for task in Vault/Dead_Letter_Queue/*.md; do
       echo "Review: $task"
       cat "$task"
       # Decide: Retry, Archive, or Delete
   done
   ```

5. **Backup Verification** (5 min)
   ```bash
   # Verify Git repository backed up
   git remote -v
   # Verify GitHub has latest commits
   git log origin/main -1

   # Verify local backup (if configured)
   # rsync or backup tool status
   ```

---

### 6.3 Monthly Maintenance

**Time Required:** 2-3 hours

**Tasks:**
1. **Full Security Audit** (30 min)
   - See `specs/platinum/security.md` - Section 7.2

2. **Credential Rotation** (30 min)
   - Gmail app password (optional, recommended quarterly)
   - Review all credentials for expiration
   - Update .env if needed

3. **Dependency Updates** (30 min)
   ```bash
   # Check for outdated packages
   cd D:\Hacathan_2
   pip list --outdated

   # Update packages (test first!)
   pip install --upgrade <package>

   # Regenerate requirements.txt
   pip freeze > requirements.txt

   # Commit and deploy
   git add requirements.txt
   git commit -m "chore: update dependencies"
   git push origin main

   # Deploy to Cloud
   ssh ubuntu@<PUBLIC_IP>
   cd ~/Hacathan_2
   git pull origin main
   source .venv/bin/activate
   pip install -r requirements.txt
   sudo systemctl restart digitalfte-cloud.service
   ```

4. **Performance Tuning** (30 min)
   - Review resource usage trends
   - Adjust loop intervals if needed
   - Optimize slow operations
   - See [Section 8: Performance Tuning](#8-performance-tuning)

5. **Documentation Review** (30 min)
   - Update this operations manual with new learnings
   - Document any issues encountered
   - Update troubleshooting guide

---

## 7. Disaster Recovery

### 7.1 Backup Strategy

**What to Backup:**
1. **Git Repository** (GitHub remote)
   - Frequency: Continuous (every git push)
   - Retention: Indefinite
   - Recovery Time: Immediate (git clone)

2. **Environment Configuration** (Manual backup)
   - Frequency: After each change
   - Location: Secure offline storage (USB, password manager)
   - Files: .env (Local), .env (Cloud)

3. **Audit Logs** (Git repository)
   - Frequency: Continuous (synced via Git)
   - Retention: 90 days in repo, archive older
   - Recovery Time: Immediate (git clone)

**Backup Verification:**
```bash
# Verify Git remote has all commits
git log origin/main -5
git diff main origin/main
# Expected: No differences

# Verify can clone fresh copy
git clone git@github.com:username/digital-fte-vault.git /tmp/test-clone
cd /tmp/test-clone
ls -la
# Expected: All files present

# Cleanup
rm -rf /tmp/test-clone
```

---

### 7.2 Recovery Procedures

#### Scenario 1: Oracle VM Lost

**Impact:** Cloud Agent offline, 24/7 monitoring stopped

**Recovery Time:** 2-4 hours

**Procedure:**
1. **Provision New Oracle VM** (1h)
   - See `docs/PLATINUM_DEPLOYMENT.md` - Section "Oracle Cloud VM Provisioning"

2. **Install Dependencies** (30 min)
   - Python 3.14, Git, system packages

3. **Clone Repository** (5 min)
   ```bash
   ssh ubuntu@<NEW_PUBLIC_IP>
   git clone git@github.com:username/digital-fte-vault.git ~/Hacathan_2
   ```

4. **Configure Environment** (15 min)
   ```bash
   cp config/.env.cloud.example .env
   # Verify WORK_ZONE=cloud, no credentials
   ```

5. **Setup Systemd Service** (15 min)
   ```bash
   sudo cp systemd/digitalfte-cloud.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable digitalfte-cloud.service
   sudo systemctl start digitalfte-cloud.service
   ```

6. **Verify Recovery** (15 min)
   ```bash
   sudo systemctl status digitalfte-cloud.service
   sudo journalctl -u digitalfte-cloud.service -n 50
   cat ~/Hacathan_2/Vault/Dashboard.md
   ```

**Data Loss:** None (all data in Git)

---

#### Scenario 2: Local Machine Lost

**Impact:** Cannot approve drafts, cannot execute actions

**Recovery Time:** 1-2 hours

**Procedure:**
1. **Setup New Local Machine** (30 min)
   - Install Git, Python 3.14
   - Clone repository:
     ```bash
     git clone git@github.com:username/digital-fte-vault.git D:\Hacathan_2
     ```

2. **Restore Environment File** (15 min)
   - Retrieve .env from backup (USB, password manager)
   - Place in project root: `D:\Hacathan_2\.env`
   - Verify all credentials present

3. **Install Dependencies** (15 min)
   ```bash
   cd D:\Hacathan_2
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Start Local Agent** (5 min)
   ```bash
   python src\orchestrator.py
   ```

5. **Verify Recovery** (15 min)
   - Check Dashboard shows Local agent
   - Pull drafts from Cloud
   - Approve and execute test task

**Data Loss:** None (all data in Git), except credentials (restore from backup)

---

#### Scenario 3: Git Repository Deleted

**Impact:** Complete system failure, data loss risk

**Recovery Time:** Varies (immediate if fresh clone available)

**Prevention:**
- ✅ Private repository (prevents accidental public deletion)
- ✅ Multiple clones (Cloud VM, Local machine)
- ⚠️ Offsite backup (future: automated daily clone to S3)

**Procedure (If Deleted):**
1. **Restore from Local Clone** (Immediate)
   ```bash
   # Create new repository on GitHub
   # Push from local clone
   cd D:\Hacathan_2
   git remote set-url origin git@github.com:username/new-repo.git
   git push origin main --force
   ```

2. **Restore from Cloud Clone** (If local unavailable)
   ```bash
   ssh ubuntu@<PUBLIC_IP>
   cd ~/Hacathan_2
   git remote set-url origin git@github.com:username/new-repo.git
   git push origin main --force
   ```

**Data Loss:** Minimal if recent clone available

---

## 8. Performance Tuning

### 8.1 Optimization Targets

**Current Performance (Baseline):**
- Task Processing: 4-5s average
- Git Sync: 30s interval, <5s latency
- Memory Usage: 4-6 GB (Cloud), 2-4 GB (Local)
- CPU Usage: 20-30% (Cloud), 5-15% (Local)

**Optimization Goals:**
- Task Processing: <3s average
- Git Sync: Maintain 30s interval, optimize large files
- Memory Usage: <8 GB (Cloud), <4 GB (Local)
- CPU Usage: <50% (both)

---

### 8.2 Tuning Parameters

**Loop Intervals:**
```bash
# .env configuration

# Orchestrator main loop (how often to scan for tasks)
LOOP_INTERVAL=30  # seconds
# Reduce to 15s for faster response (higher CPU)
# Increase to 60s for lower load (slower response)

# Watcher poll intervals
GMAIL_POLL_INTERVAL=300   # 5 minutes
WHATSAPP_POLL_INTERVAL=120  # 2 minutes
LINKEDIN_POLL_INTERVAL=600  # 10 minutes

# Reduce for more frequent checks (higher load)
# Increase for less frequent checks (lower load)
```

**Git Sync Optimization:**
```bash
# Git configuration for faster syncing

# Increase pack window (better compression, slower)
git config pack.window 50

# Use delta compression
git config core.compression 9

# Prune old objects
git gc --aggressive --prune=now

# Optimize repository
git repack -a -d --depth=250 --window=250
```

**Resource Limits:**
```bash
# Systemd service (/etc/systemd/system/digitalfte-cloud.service)

[Service]
# Memory limit (soft)
MemoryLimit=8G

# CPU quota (200% = 2 full cores)
CPUQuota=200%

# Maximum file descriptors
LimitNOFILE=4096

# Restart daemon after changes
sudo systemctl daemon-reload
sudo systemctl restart digitalfte-cloud.service
```

---

### 8.3 Performance Monitoring

**Continuous Monitoring:**
```bash
# Resource usage over time (Cloud)
ssh ubuntu@<PUBLIC_IP> 'sar -u 60 10'  # CPU every 60s, 10 samples
ssh ubuntu@<PUBLIC_IP> 'sar -r 60 10'  # Memory every 60s
ssh ubuntu@<PUBLIC_IP> 'sar -d 60 10'  # Disk I/O every 60s

# Process-level monitoring
ssh ubuntu@<PUBLIC_IP> 'top -b -n 10 -d 60 | grep orchestrator'
```

**Benchmarking:**
```bash
# Task processing time (average)
cat Vault/Logs/audit/audit_*.jsonl | \
    jq -r 'select(.details.processing_time) | .details.processing_time' | \
    awk '{sum+=$1; count++} END {print "Avg:", sum/count, "seconds"}'

# Git operations time
time git pull origin main
time git push origin main
```

**Optimization Checklist:**
- [ ] Loop intervals tuned for workload
- [ ] Git repository optimized (gc, repack)
- [ ] Resource limits appropriate
- [ ] No memory leaks (memory stable over 24h)
- [ ] No CPU spikes (CPU usage consistent)
- [ ] Disk I/O reasonable (<50% iowait)

---

## Appendix A: Runbook Templates

### Template: Incident Response

```markdown
# Incident Report: <ID>-YYYY-MM-DD

**Severity:** P0 / P1 / P2 / P3
**Reported By:** [Name]
**Reported At:** [Timestamp]
**Resolved At:** [Timestamp]
**Duration:** [X hours]

## Summary
Brief description of incident (1-2 sentences).

## Impact
- Users affected: [Number or scope]
- Services impacted: [Cloud Agent / Local Agent / Git sync]
- Data loss: [Yes/No, details]

## Timeline
- [HH:MM] Event 1
- [HH:MM] Event 2
- [HH:MM] Resolution

## Root Cause
Detailed explanation of what caused the incident.

## Resolution
Steps taken to resolve the incident.

## Follow-Up Actions
- [ ] Action item 1
- [ ] Action item 2

## Lessons Learned
What went well, what didn't, what to improve.
```

---

### Template: Maintenance Window

```markdown
# Maintenance Window: <Date>

**Start Time:** [YYYY-MM-DD HH:MM UTC]
**End Time:** [YYYY-MM-DD HH:MM UTC]
**Duration:** [X hours]
**Impact:** [Cloud Agent / Local Agent / Both]

## Objective
Brief description of maintenance goals.

## Pre-Maintenance Checklist
- [ ] Notify users (if applicable)
- [ ] Backup critical data
- [ ] Verify rollback procedure

## Maintenance Steps
1. Step 1
2. Step 2
3. Step 3

## Post-Maintenance Checklist
- [ ] Verify services running
- [ ] Check logs for errors
- [ ] Update Dashboard
- [ ] Notify users of completion

## Rollback Procedure (If Needed)
1. Rollback step 1
2. Rollback step 2
```

---

## Appendix B: Quick Reference Cards

### Card: Essential Commands

**Cloud Agent:**
```
Status:  ssh <IP> 'sudo systemctl status digitalfte-cloud.service'
Logs:    ssh <IP> 'sudo journalctl -u digitalfte-cloud.service -f'
Restart: ssh <IP> 'sudo systemctl restart digitalfte-cloud.service'
```

**Local Agent:**
```
Start:   python src\orchestrator.py
Stop:    Ctrl+C or pkill -f orchestrator.py
Logs:    tail -f logs/orchestrator.log
```

**Git:**
```
Status:  git status
Pull:    git pull origin main
Push:    git push origin main
Sync:    git pull && git push
```

**Monitoring:**
```
Dashboard: cat Vault\Dashboard.md
Audit:     cat Vault\Logs\audit\audit_$(date +%Y-%m-%d).jsonl | jq
Drafts:    ls Vault\Drafts\
DLQ:       ls Vault\Dead_Letter_Queue\
```

---

**Document Version:** 1.0
**Last Updated:** 2026-01-22
**Status:** Production Ready
**Next Review:** 2026-03-22 (Quarterly)
