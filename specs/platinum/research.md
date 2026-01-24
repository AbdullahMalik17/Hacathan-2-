# Platinum Tier Research Document

**Feature:** Cloud + Local Dual-Agent Architecture
**Date:** 2026-01-22
**Status:** Research Complete
**Author:** Abdullah Junior Development Team

---

## Executive Summary

Platinum Tier transforms the Digital FTE from a single-instance local agent into a **distributed dual-agent system** with a Cloud agent (always-on, drafting) and a Local agent (approval & execution). This enables 24/7 operation while maintaining security and human oversight.

---

## Research Questions

### 1. Why Dual-Agent Architecture?

**Problem:** Single local agent requires laptop to be on 24/7
- Can't respond to emails when laptop is off
- Can't monitor social media overnight
- Can't draft responses during offline hours
- User has to keep computer running constantly

**Solution:** Dual-agent with work-zone specialization
- **Cloud Agent**: Always-on, monitoring, drafting (no secrets)
- **Local Agent**: Approval, execution, sensitive operations (has secrets)

**Benefits:**
- 24/7 availability without always-on laptop
- Security: Secrets stay local
- Cost-effective: Cloud agent does prep work, local executes
- Human-in-the-loop maintained

### 2. How Do Agents Communicate?

**Options Considered:**

| Method | Pros | Cons | Decision |
|--------|------|------|----------|
| **File-based (Git sync)** | Simple, auditable, fault-tolerant | Slower (minutes delay), potential conflicts | ✅ **Phase 1** |
| **Direct API (A2A)** | Fast (real-time), efficient | Complex, requires server, less fault-tolerant | 🔮 Phase 2 (optional) |
| **Message Queue** | Reliable, scalable | Overkill for 2 agents, requires infrastructure | ❌ No |
| **Database** | Centralized state | Requires DB server, couples agents | ❌ No |

**Decision: File-based communication via Git (Phase 1)**

**Rationale:**
- Obsidian vault is already markdown-based
- Git provides natural sync + audit trail
- Fault-tolerant: if one agent down, files remain
- Simple to debug: just look at files
- Supports claim-by-move pattern

### 3. Work-Zone Specialization - What Does Each Agent Do?

**Cloud Agent Responsibilities:**
- ✅ Monitor Gmail 24/7
- ✅ Draft email replies (no sending)
- ✅ Monitor social media mentions
- ✅ Draft social media posts
- ✅ Triage tasks by priority
- ✅ Create Plans for complex tasks
- ✅ Write to Odoo (draft invoices/expenses)
- ✅ Health monitoring and alerting
- ❌ NO access to secrets (.env, tokens, sessions)
- ❌ NO sending emails/posts
- ❌ NO WhatsApp (requires session file)
- ❌ NO payments/banking
- ❌ NO final execution of sensitive actions

**Local Agent Responsibilities:**
- ✅ Review Cloud drafts
- ✅ Human approval workflow
- ✅ Execute approved actions (send emails/posts)
- ✅ WhatsApp monitoring & sending
- ✅ Banking/payment operations
- ✅ Merge Cloud updates into Dashboard
- ✅ Own all secrets and credentials
- ❌ Doesn't need to run 24/7
- ❌ Can be offline for hours

**Work Delegation Flow:**
```
1. Email arrives at 2 AM (Local offline)
2. Cloud detects → drafts reply → saves to /Pending_Approval/cloud/
3. User wakes up at 8 AM → Local agent starts
4. Local shows pending approval in Dashboard
5. User approves → Local sends email → logs → /Done/
6. Both agents see completion via Git sync
```

### 4. Claim-by-Move Pattern - How to Prevent Duplicate Work?

**Problem:** Two agents might process the same task simultaneously

**Solution: Claim-by-move atomic filesystem operation**

```
/Needs_Action/email_001.md  ← Initial state (both can see)

Cloud tries to claim:
1. Move /Needs_Action/email_001.md → /In_Progress/cloud/email_001.md
2. If move succeeds → Cloud owns it
3. If move fails → Another agent claimed it first

Local tries to claim same file:
1. Move /Needs_Action/email_001.md → /In_Progress/local/email_001.md
2. Move fails (file already gone) → Local skips it
3. Cloud wins this task
```

**Why This Works:**
- Filesystem move is atomic on most systems
- First agent to move wins
- Loser's move fails with "file not found"
- No central coordination needed
- Git tracks who moved when (audit trail)

**Implementation:**
```python
def claim_task(task_file: Path, agent_name: str) -> bool:
    """Claim a task using atomic move. Returns True if claimed."""
    in_progress = VAULT_PATH / "In_Progress" / agent_name / task_file.name
    try:
        task_file.rename(in_progress)  # Atomic move
        return True  # We claimed it!
    except FileNotFoundError:
        return False  # Another agent claimed it
```

### 5. Vault Synchronization - Git vs Syncthing?

**Git-based Sync (Recommended):**

**Pros:**
- Full version history (audit trail)
- Conflict detection built-in
- Easy to inspect what changed
- Works with existing workflow
- Free with GitHub/GitLab
- Can review changes before accepting

**Cons:**
- Requires commits (slight delay)
- Need auto-commit script
- Conflicts possible but rare

**Implementation:**
```bash
# Cloud agent auto-commit script (runs every 60s)
while true; do
  git add Vault/
  git commit -m "Cloud update: $(date)"
  git push
  sleep 60
done

# Local agent auto-pull script (runs every 30s)
while true; do
  git pull --rebase
  sleep 30
done
```

**Syncthing (Alternative):**

**Pros:**
- Real-time sync (no delay)
- Automatic conflict handling
- No git commits needed
- Works offline better

**Cons:**
- No version history
- Harder to debug
- Conflicts create duplicate files
- Less transparent

**Decision: Git for Phase 1, Syncthing as optional upgrade**

### 6. Security Architecture - How to Keep Secrets Local?

**Threat Model:**
- Cloud agent should never access secrets
- If cloud VM compromised, no credentials leaked
- Local machine has all secrets

**Security Rules:**

1. **Secrets Never Sync**
```gitignore
# .gitignore for Vault
.env
*.json  # Except specific allowed configs
tokens/
sessions/
credentials/
*.key
*.pem
```

2. **Agent-Specific Environment**
```bash
# Cloud VM .env
FTE_ROLE=cloud
AGENT_ID=cloud-01
# NO Gmail credentials
# NO WhatsApp sessions
# NO banking tokens

# Local .env
FTE_ROLE=local
AGENT_ID=local-01
GMAIL_CREDENTIALS=<token>
WHATSAPP_SESSION=<session>
BANKING_API_KEY=<key>
```

3. **Capability-Based Design**
- Cloud has MCP servers for read-only operations
- Local has full MCP servers including send/execute
- Cloud can't call send_email even if it wanted to

4. **Audit Everything**
- All agent actions logged to Vault/Logs/
- Git history shows who did what
- Human can review before approving

### 7. Health Monitoring - How to Know If Cloud Agent Dies?

**Monitoring Strategy:**

1. **Heartbeat File**
```markdown
# Vault/Signals/cloud_heartbeat.md
---
agent: cloud
last_update: 2026-01-22T14:30:00Z
status: healthy
tasks_processed: 47
---
```

2. **Local Checks Heartbeat**
```python
def check_cloud_health():
    heartbeat = read_heartbeat("Vault/Signals/cloud_heartbeat.md")
    age = now() - heartbeat['last_update']
    if age > timedelta(minutes=10):
        alert("Cloud agent down!", age)
```

3. **Cloud VM Monitoring**
- Systemd service with auto-restart
- Uptime monitoring (e.g., UptimeRobot)
- Email alerts on service failure
- Resource monitoring (CPU, memory, disk)

4. **Recovery**
- Systemd auto-restart on crash
- Git state preserved (no data loss)
- Local can take over critical tasks
- Manual intervention for VM failures

### 8. Cloud VM Options - Where to Deploy?

**Considered Options:**

| Provider | Free Tier | Specs | Pros | Cons | Decision |
|----------|-----------|-------|------|------|----------|
| **Oracle Cloud** | Yes | 1-4 OCPU, 1-24GB RAM | Generous free tier, Always Free | Complex setup, account approval | ✅ **Primary** |
| **AWS** | 12 months | t2.micro | Well-documented | Costs after 12 months | 🔄 Backup |
| **Azure** | 12 months | B1s | Microsoft integrations | Costs after 12 months | 🔄 Backup |
| **GCP** | 90 days | e2-micro | Good docs | Short free period | ❌ No |
| **Linode/DO** | No free tier | $5/mo | Simple setup | Ongoing cost | ❌ No |

**Decision: Oracle Cloud Always Free + AWS as backup**

**Oracle Cloud Always Free Specs:**
- 4 ARM-based Ampere A1 cores
- 24 GB RAM
- 200 GB block storage
- 10 TB bandwidth/month
- **Actually free forever** (not trial)

**Setup Complexity:**
- Account approval required (can take days)
- IP allowlisting
- Instance availability varies by region

**Recommendation:** Start Oracle account approval NOW

### 9. Odoo on Cloud - How to Secure It?

**Requirements:**
- Odoo Community running 24/7
- HTTPS with Let's Encrypt
- Daily backups
- Health monitoring
- MCP integration

**Architecture:**
```
Cloud VM (Oracle)
├── Docker Compose
│   ├── Odoo (port 8069)
│   ├── PostgreSQL (port 5432)
│   └── Nginx (port 80/443)
├── Systemd services
│   ├── odoo.service
│   ├── orchestrator.service
│   └── watchers.service
└── Backup script (daily to Object Storage)
```

**Security Checklist:**
- ✅ HTTPS only (no HTTP)
- ✅ Strong Odoo admin password
- ✅ Database backups encrypted
- ✅ Firewall rules (only 80/443 open)
- ✅ Fail2ban for brute force protection
- ✅ Regular security updates

### 10. Demo Requirements - What Must Work?

**Minimum Passing Gate:**

```
Scenario: Email while Local offline

1. 2:00 AM - Email arrives from customer
2. 2:01 AM - Cloud Gmail watcher detects
3. 2:02 AM - Cloud creates task in /Needs_Action/cloud/
4. 2:03 AM - Cloud claims task, drafts reply
5. 2:05 AM - Cloud saves to /Pending_Approval/cloud/reply_draft.md
6. 2:06 AM - Cloud commits & pushes to Git

[Local is offline 2:00 AM - 8:00 AM]

7. 8:00 AM - Local agent starts
8. 8:01 AM - Local pulls from Git, sees pending approval
9. 8:02 AM - Dashboard shows: "1 email draft needs approval"
10. 8:03 AM - Human reviews draft, approves
11. 8:04 AM - Local executes send via Email MCP
12. 8:05 AM - Local logs action, moves to /Done/
13. 8:06 AM - Local commits & pushes to Git
14. 8:07 AM - Cloud pulls, sees task completed

PASS: Email sent with 6-hour delay but fully autonomous
```

**What to Demonstrate:**
- Cloud operates independently while local offline
- Human approval workflow preserved
- Git sync works bidirectionally
- Secrets stay local (Cloud never accessed Gmail credentials)
- Audit trail complete (Git log shows all steps)

---

## Technical Decisions

### Decision 1: File-Based Communication (Phase 1)

**Context:** Need agents to communicate reliably

**Options:**
1. Git-synced markdown files
2. Direct API calls (A2A)
3. Message queue (Redis, RabbitMQ)

**Decision:** Git-synced files

**Rationale:**
- Simplest to implement
- Natural fit with Obsidian vault
- Excellent audit trail
- Fault-tolerant (survives agent crashes)
- Git handles conflicts

**Trade-offs:**
- Slower than API (minutes vs seconds)
- Git conflicts possible (rare with atomic moves)

### Decision 2: Claim-by-Move Pattern

**Context:** Prevent duplicate work

**Options:**
1. Claim-by-move (atomic filesystem)
2. Central coordinator service
3. Database locks
4. Distributed consensus (Raft, Paxos)

**Decision:** Claim-by-move

**Rationale:**
- No central point of failure
- Simple to implement and debug
- Atomic at filesystem level
- Works offline

**Trade-offs:**
- Not 100% atomic on all filesystems (rare edge case)
- Requires Git to propagate claim

### Decision 3: Oracle Cloud for Deployment

**Context:** Need 24/7 cloud VM

**Options:**
1. Oracle Cloud (Always Free)
2. AWS (12-month free tier)
3. Azure (12-month free tier)
4. Paid VPS ($5-20/month)

**Decision:** Oracle Cloud primary, AWS backup

**Rationale:**
- Actually free forever (not trial)
- Generous specs (4 CPU, 24GB RAM)
- Good enough for Python + Docker

**Trade-offs:**
- Account approval delay
- Complex initial setup
- Instance availability varies

### Decision 4: Systemd for Service Management

**Context:** Keep services running 24/7

**Options:**
1. Systemd (Linux native)
2. Docker Compose restart policies
3. PM2 (Node.js)
4. Supervisor

**Decision:** Systemd + Docker Compose

**Rationale:**
- Built into Linux
- Auto-restart on crash
- Log management with journalctl
- Integration with OS

**Trade-offs:**
- Linux-only (not cross-platform)
- Requires root for setup

---

## Risks & Mitigations

### Risk 1: Git Conflicts

**Probability:** Medium (with 2 agents writing frequently)
**Impact:** Medium (blocks sync until resolved)

**Mitigation:**
- Agents write to separate directories (cloud/ vs local/)
- Dashboard.md: only Local writes, Cloud writes to /Signals/
- Atomic move reduces conflicts
- Auto-rebase on pull

**Contingency:** Manual conflict resolution + alert

### Risk 2: Cloud Agent Goes Down

**Probability:** Low (with Systemd auto-restart)
**Impact:** Medium (no drafts while down)

**Mitigation:**
- Systemd auto-restart (5s delay)
- Heartbeat monitoring
- Email alerts on failure
- Local can take over if needed

**Contingency:** Manual VM restart, or run local 24/7 temporarily

### Risk 3: Secrets Accidentally Synced

**Probability:** Low (with .gitignore)
**Impact:** Critical (credentials exposed)

**Mitigation:**
- Comprehensive .gitignore
- Pre-commit hooks to check for secrets
- Separate .env files for cloud/local
- Audit git history regularly

**Contingency:**
- Immediately rotate all credentials
- Purge git history with git-filter-repo
- Review access logs

### Risk 4: Oracle Account Not Approved

**Probability:** Medium (Oracle has manual review)
**Impact:** Medium (delays Platinum tier)

**Mitigation:**
- Apply for Oracle Cloud account NOW
- Have AWS account ready as backup
- Document both setups

**Contingency:** Use AWS 12-month free tier or paid VPS temporarily

### Risk 5: Vault Sync Lag Causes Confusion

**Probability:** Medium (Git sync every 60s)
**Impact:** Low (minor UX issue)

**Mitigation:**
- Display last sync time in Dashboard
- Pull frequently (every 30s on local)
- Use /Signals/ for status updates

**Contingency:** Switch to Syncthing for faster sync

---

## Open Questions

### Q1: How fast should Git sync be?

**Answer:**
- Cloud: Commit & push every 60 seconds
- Local: Pull every 30 seconds
- Total max latency: 90 seconds (acceptable for Platinum demo)

**Justification:** Balance between responsiveness and Git load

### Q2: Should we support more than 2 agents?

**Answer:** Not in Phase 1. Design allows it but not required.

**Justification:**
- Hackathon requires Cloud + Local
- More agents = exponentially more complexity
- Can add later without redesign

### Q3: What if user has multiple local machines?

**Answer:** One "Local" agent at a time

**Justification:**
- Simpler security model (one place has secrets)
- User can choose which machine is "Local"
- Other machines can be read-only

### Q4: How to handle time zones (Cloud in UTC, Local in user TZ)?

**Answer:** All timestamps in ISO 8601 with timezone

**Justification:**
- Standard format
- Python datetime handles conversion
- Obsidian displays correctly

---

## Performance Estimates

### Latency

| Operation | Expected Time | Acceptable Range |
|-----------|---------------|------------------|
| Cloud detects email | 30-60s | <2 min |
| Cloud drafts reply | 10-30s | <1 min |
| Cloud commits to Git | 5-10s | <30s |
| Git sync to Local | 30-90s | <5 min |
| Local pulls update | 10-30s | <1 min |
| Human approval | Variable | N/A |
| Local executes send | 5-15s | <1 min |
| **Total (no human)** | **90-225s** | **<10 min** |

### Resource Usage

**Cloud VM:**
- CPU: 10-30% avg, 80% during processing
- RAM: 500MB-2GB (Python + Docker)
- Disk: 5GB (Vault + logs)
- Network: <100MB/day (mostly API calls)

**Local:**
- CPU: 5-20% avg
- RAM: 300MB-1GB
- Disk: Same vault (10GB with history)
- Network: <50MB/day

### Cost Estimates

| Component | Cost | Notes |
|-----------|------|-------|
| Oracle Cloud VM | $0 | Always Free tier |
| Claude API (Cloud) | ~$20-50/mo | Depends on usage |
| Claude API (Local) | ~$10-30/mo | Less frequent |
| Domain + SSL | $10-15/yr | Optional for Odoo HTTPS |
| **Total** | **~$30-80/mo** | Production-ready |

---

## Success Criteria

### Must Have (Minimum Viable)

- ✅ Cloud agent runs 24/7 on Oracle Cloud
- ✅ Local agent runs on-demand
- ✅ Git sync working bidirectionally
- ✅ Claim-by-move prevents duplicate work
- ✅ Secrets stay local (.env not synced)
- ✅ Demo scenario passes (email while offline)
- ✅ Audit trail complete (Git log + Vault/Logs/)

### Should Have (Production Quality)

- ✅ Systemd services with auto-restart
- ✅ Health monitoring with alerts
- ✅ Odoo on Cloud with HTTPS
- ✅ Dashboard shows sync status
- ✅ Comprehensive documentation

### Could Have (Nice to Have)

- 🔮 A2A direct messaging (Phase 2)
- 🔮 Syncthing as faster sync option
- 🔮 Multi-local-agent support
- 🔮 Grafana dashboard for metrics

---

## Research Conclusion

Platinum Tier is **feasible and well-architected**. The dual-agent design with file-based communication is:
- **Simple:** Leverages existing tools (Git, filesystems)
- **Secure:** Secrets stay local, audit trail complete
- **Reliable:** Fault-tolerant, no single point of failure
- **Scalable:** Can add more agents later

**Estimated Implementation Time:** 40-60 hours
**Risk Level:** Medium (Oracle account approval, Git sync tuning)
**Recommendation:** Proceed with specification and planning

---

**Research Status:** ✅ Complete
**Next Step:** Create detailed specification (spec.md)
**Confidence Level:** High (8/10)

---

*Document Version: 1.0*
*Last Updated: 2026-01-22*
