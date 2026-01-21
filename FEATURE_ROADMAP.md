# Digital FTE Feature Roadmap & Planning

**Date Updated:** 2026-01-21
**Status:** Platinum Tier Phase
**Tier Target:** Platinum (Integration & Scale)

---

## Overview

We have successfully implemented the core Gold Tier features. The focus now shifts to optimization, stability (Platinum), and advanced integrations.

**Completed Features:**
1. **WhatsApp Watcher** ✅
2. **Filesystem Watcher** ✅
3. **Email Sender MCP** ✅
4. **Weekly CEO Briefing** ✅
5. **Laptop Startup/Reload** ✅

This document outlines the next phase of development.

---

### Feature 1: WhatsApp Watcher

### Overview
Monitor WhatsApp messages and convert them to vault tasks, enabling the FTE to respond to WhatsApp messages autonomously.

### Status & Priority
- **Current Status:** ✅ Completed (Gold Tier)
- **Priority:** Medium (requires Playwright, external integration)
- **Complexity:** High

### Business Goals
- 24/7 monitoring of WhatsApp Direct Messages
- Auto-reply to known contacts via handbook rules
- Escalate complex messages to human for approval

### Implementation Approach
- Use **Playwright** to automate WhatsApp Web (browser-based)
- Monitor DM inbox for unread messages
- Convert messages to markdown task files with sender, timestamp, content
- Include sender metadata (known contact? previous history?)

### Technology Stack
- `playwright` (browser automation)
- `pyperclip` (clipboard operations for sending)
- `python-dotenv` (credentials)

### Rate Limits & Safety
- Max messages processed per hour: 20
- Max replies sent per hour: 5
- All messages logged with sender, timestamp, content, action taken

### Risks
- WhatsApp Web API changes (fragile)
- Account blocking risk from automation
- Message encoding/emoji handling
- Session management complexity

---

### Feature 2: Filesystem Watcher

### Overview
Monitor local filesystem for changes (new files, modifications) and create vault tasks for FTE processing.

### Status & Priority
- **Current Status:** ✅ Completed (Gold Tier)
- **Priority:** High (foundational, useful for many workflows)
- **Complexity:** Medium

### Business Goals
- Monitor important directories for new/modified files
- Auto-categorize files by type and location
- Create structured tasks for file processing
- Enable bulk operations on watched directories

### Implementation Approach
- Use **watchdog** library (cross-platform file monitoring)
- Define "watched directories" in config (e.g., ~/Downloads, ~/Documents)
- On file event, analyze file type, size, age
- Create markdown task with file metadata and suggested action

### Technology Stack
- `watchdog` (filesystem monitoring)
- `python-magic` (file type detection)
- `pathspec` (pattern matching for ignore rules)

### Rate Limits & Safety
- Max file events per hour: 50
- Debounce: 5 seconds (group rapid changes)
- Never delete files automatically (always require approval)
- Ignore system/cache files

### Risks
- High volume of file events (debouncing critical)
- Disk I/O during large file copies
- Symlink and permission handling

---

### Feature 3: Email Sender MCP

### Overview
MCP (Model Context Protocol) server that enables the orchestrator to send emails. This is the **action layer** complementing Gmail Watcher (perception).

### Status & Priority
- **Current Status:** ✅ Completed (Silver tier)
- **Priority:** High (critical for closed-loop workflow)
- **Complexity:** Medium-High

### Business Goals
- Enable FTE to send emails autonomously
- Complete perception → reasoning → action loop
- Support templates and personalization
- Maintain audit trail of all sends

### Implementation Approach
- FastMCP or Node MCP SDK
- Define 3-5 tools for email operations
- Handle OAuth credentials securely
- Rate limiting and audit logging

### Technology Stack
- `fastmcp` (Python MCP framework) OR `mcp-sdk` (Node.js)
- `google-api-client` (Gmail API for sending)
- `jinja2` (email templates)

### Rate Limits & Safety

| Action | Limit | Period |
|--------|-------|--------|
| Emails sent | 10 | Hour |
| Emails sent | 100 | Day |
| Recipients | 5 | Single send |

**Safety Mechanisms:**
- All emails require explicit approval (no auto-send)
- Pending emails go to `Vault/Pending_Approval/email_*.md`
- Human moves to `Vault/Approved/` to trigger send
- Audit log: timestamp, sender, recipient, subject, status

### Risks
- Accidental mass emails (rate limiting critical)
- Gmail API quota exhaustion
- Spam filtering (sender reputation)
- Template variable mistakes

---

### Feature 4: Weekly CEO Briefing

### Overview
Generate an executive summary/briefing from daily activities, decisions, and outcomes. Delivered via email or markdown report.

### Status & Priority
- **Current Status:** ✅ Completed (Silver tier)
- **Priority:** Medium (advanced analytics)
- **Complexity:** Medium

### Business Goals
- Summarize week's activities for leadership review
- Highlight decisions made, approvals granted, actions taken
- Provide metrics: tasks completed, time saved, cost impact
- Enable data-driven oversight of FTE operations

### Implementation Approach
- Use Python scheduler (`schedule` or `APScheduler`)
- Read weekly logs (last 7 days)
- Analyze actions: tasks completed, decisions, approvals, failures
- Use Claude to synthesize narrative summary
- Export as markdown or email (via Email Sender MCP)

### Technology Stack
- `schedule` or `APScheduler` (scheduling)
- Log aggregation and parsing

### Risks
- Log file corruption or missing data
- Performance on large log files
- Email delivery failures
- Metric calculation errors

---

### Feature 5: Laptop Startup/Reload

### Overview
Auto-launch the FTE system when the user opens their laptop, ensuring continuous monitoring without manual intervention.

### Status & Priority
- **Current Status:** ✅ Completed (Platinum Tier)
- **Priority:** Critical (foundational for 24/7 operation)
- **Complexity:** Low-Medium

### Business Goals
- Zero manual intervention needed to start FTE
- Automatic system recovery on restart
- Graceful shutdown and cleanup
- Persistent logging of startup events

### Implementation Approaches

**Windows (Task Scheduler):**
```powershell
$ScriptPath = "D:\Hacathan_2\scripts\startup.bat"
$TaskName = "Digital FTE"

Register-ScheduledTask -TaskName $TaskName `
  -Trigger (New-ScheduledTaskTrigger -AtLogon) `
  -Action (New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c $ScriptPath")
```

**macOS (LaunchAgent):**
- Create plist in `~/Library/LaunchAgents/`
- Set `RunAtLoad` to true

**Linux (Systemd):**
- Create service in `~/.config/systemd/user/`
- Enable with `systemctl --user enable`

### Technology Stack
- OS-level scheduler (Task Scheduler, cron, systemd)
- Python subprocess management
- Optional: `supervisor` or `systemd`

### Risks
- Process hanging or zombie processes
- Environment variables not inherited
- Permissions issues on startup
- Conflicting background processes

---

## Decision Matrix: Feature Prioritization

### Evaluation Criteria

| Criteria | Weight | Impact |
|----------|--------|--------|
| Business Value | 30% | How much does it help users? |
| Technical Complexity | 20% | How hard to build? |
| Dependencies | 20% | How many external integrations? |
| Risk Level | 15% | What can go wrong? |
| Effort (Hours) | 15% | How much time required? |

### Feature Scores (1-10 scale, higher is better)

| Feature | Business | Complexity | Dependencies | Risk | Effort | **Score** |
|---------|----------|------------|-------------|------|--------|-----------|
| **Laptop Startup** | 9 | 8 | 3 | 7 | 8 | **7.0** ⭐⭐⭐ |
| **Filesystem Watcher** | 7 | 6 | 7 | 6 | 7 | **6.6** ⭐⭐⭐ |
| **Email Sender MCP** | 9 | 5 | 8 | 5 | 6 | **6.6** ⭐⭐⭐ |
| **Weekly CEO Briefing** | 6 | 4 | 7 | 8 | 5 | **6.2** ⭐⭐ |
| **WhatsApp Watcher** | 7 | 3 | 4 | 4 | 4 | **5.2** ⭐⭐ |

---

## Recommended Implementation Order

### Sprint 1 (Weeks 1-2): Foundation
1. **Laptop Startup/Reload** (4-6 hours)
   - Creates infrastructure for continuous operation
   - Enables all other features to run autonomously

2. **Email Sender MCP** (8-12 hours)
   - Completes perception → reasoning → action loop
   - Enables closed-loop email workflows

### Sprint 2 (Weeks 3-4): Expansion
3. **Filesystem Watcher** (8-10 hours)
   - Adds third input source
   - Builds on watcher pattern (Gmail already done)

4. **Weekly CEO Briefing** (6-8 hours)
   - Uses logs already being generated

### Sprint 3 (Weeks 5+): Advanced
5. **WhatsApp Watcher** (10-14 hours)
   - Most complex watcher
   - Consider after core features stable

---

## Dependency Analysis

```
Laptop Startup/Reload
  └─ Enables all other features to run 24/7

Email Sender MCP
  └─ Enables: Closed-loop workflows

Filesystem Watcher
  └─ Depends on: Laptop Startup (for continuous operation)

Weekly CEO Briefing
  └─ Uses existing logging system

WhatsApp Watcher
  └─ Most complex, implement last
```

---

## Questions for Clarification

1. **Platform Target:** Which OS is primary? (Windows/macOS/Linux?)
2. **WhatsApp Strategy:** Acceptable to use Playwright/browser automation, or prefer API?
3. **Email Volume:** Estimated emails/day to process?
4. **File Watching:** Specific directories to monitor?
5. **Approval Workflow:** Should ALL emails require approval or some auto-send?
6. **CEO Briefing:** Weekly, daily, or on-demand?

---

## Next Steps

1. **Review this roadmap** with your requirements
2. **Select features** you want to implement
3. **Create detailed spec** for chosen feature
4. **Implement incrementally** with test coverage
5. **Deploy and validate** before moving to next feature

---

**End of Feature Roadmap**  
*Created: 2026-01-15*
