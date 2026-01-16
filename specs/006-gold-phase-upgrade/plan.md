# Gold Phase Upgrade - Implementation Plan

**Status:** Ready for Approval
**Branch:** `002-gold-phase-upgrade` (to create)
**Date:** 2026-01-16

## Overview

This plan covers two major deliverables:
1. **LinkedIn Auto-Posting** - Hybrid browser automation + future API support
2. **Agent Skills Conversion** - Convert all core modules to Claude Code Skills

---

## Part 1: LinkedIn Auto-Posting

### 1.1 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Content Sources                         │
├─────────────────┬───────────────────────────────────────┤
│ CEO Briefing    │ Manual Queue (Vault/LinkedIn_Queue/)  │
│ (auto-generate) │ (human-written posts)                 │
└────────┬────────┴──────────────┬────────────────────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │  LinkedIn Post        │
         │  Generator            │
         │  (content + schedule) │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │  Pending_Approval/    │
         │  LinkedIn_*.md        │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │  Human Reviews &      │
         │  Approves Post        │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │  LinkedIn Poster      │
         │  (Playwright browser) │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │  Done/ + Audit Log    │
         └───────────────────────┘
```

### 1.2 Files to Create

| File | Purpose |
|------|---------|
| `src/linkedin/linkedin_poster.py` | Browser automation for posting (Playwright) |
| `src/linkedin/content_generator.py` | Generate posts from CEO Briefing data |
| `src/linkedin/linkedin_scheduler.py` | Schedule posts from queue |
| `src/templates/linkedin/weekly_update.j2` | Jinja2 template for weekly metrics posts |
| `src/templates/linkedin/achievement.j2` | Template for achievement/milestone posts |
| `src/templates/linkedin/engagement.j2` | Template for engagement/question posts |
| `config/linkedin_config.json` | LinkedIn posting schedule & preferences |
| `Vault/LinkedIn_Queue/` | Manual post queue folder |
| `Vault/Logs/linkedin_audit_log.md` | Audit trail for all LinkedIn actions |

### 1.3 LinkedIn Poster Implementation

```python
# src/linkedin/linkedin_poster.py - Core structure
class LinkedInPoster:
    """Browser automation for LinkedIn posting using Playwright."""

    async def authenticate(self) -> bool:
        """Navigate to LinkedIn, handle login/session."""

    async def create_post(self, content: str, media: List[Path] = None) -> str:
        """Create a new LinkedIn post with optional media."""

    async def schedule_post(self, content: str, scheduled_time: datetime) -> str:
        """Schedule a post for future publication."""

    async def check_session(self) -> bool:
        """Verify LinkedIn session is still valid."""
```

**Key Features:**
- Persistent browser context at `config/linkedin_data/`
- QR code / manual login flow (like WhatsApp)
- Media attachment support (images)
- Rate limiting (max 2 posts/day)
- Comprehensive error handling

### 1.4 Content Generator

```python
# src/linkedin/content_generator.py - Core structure
class ContentGenerator:
    """Generate LinkedIn posts from various sources."""

    def from_ceo_briefing(self, briefing_path: Path) -> str:
        """Extract key metrics and create professional post."""

    def from_template(self, template: str, variables: dict) -> str:
        """Render Jinja2 template with provided variables."""

    def suggest_hashtags(self, content: str) -> List[str]:
        """Suggest relevant hashtags based on content."""
```

**Content Types:**
1. **Weekly Metrics** - Auto-generated from CEO Briefing
2. **Achievements** - Milestone announcements
3. **Engagement** - Questions/polls for audience
4. **Manual** - Human-written from queue

### 1.5 Approval Workflow

Posts requiring approval create files like:
```markdown
# Vault/Pending_Approval/LinkedIn_2026-01-16_weekly.md

---
type: linkedin_post
source: ceo_briefing
scheduled: 2026-01-17T09:00:00
status: pending_approval
---

## Proposed LinkedIn Post

🚀 **Weekly AI Automation Update**

This week our Digital FTE processed:
- 47 emails automatically triaged
- 12 WhatsApp messages prioritized
- 8 files organized from DropFolder

Automation saves ~3 hours/week!

#AIAutomation #Productivity #DigitalTransformation

---

## Actions
- [ ] Approve - Move to Approved/
- [ ] Edit - Modify content above
- [ ] Reject - Delete file
```

---

## Part 2: Agent Skills Conversion

### 2.1 Skills to Create

| Skill Name | Source Module | Description |
|------------|---------------|-------------|
| `digital-fte-orchestrator` | `src/orchestrator.py` | Task processing with Ralph Wiggum loop |
| `watching-gmail` | `src/watchers/gmail_watcher.py` | Gmail inbox monitoring |
| `watching-whatsapp` | `src/watchers/whatsapp_watcher.py` | WhatsApp Web monitoring |
| `watching-filesystem` | `src/watchers/filesystem_watcher.py` | DropFolder monitoring |
| `generating-ceo-briefing` | `src/reports/ceo_briefing.py` | Weekly report generation |
| `sending-emails` | `src/mcp_servers/email_sender.py` | Email sending via MCP |
| `posting-linkedin` | `src/linkedin/linkedin_poster.py` | LinkedIn posting (new) |
| `managing-services` | `src/service_manager.py` | Process supervision |

### 2.2 Skill Structure Template

Each skill follows this structure:
```
.claude/skills/<skill-name>/
├── SKILL.md              # Required: frontmatter + instructions
├── scripts/
│   ├── verify.py         # Required: verification script
│   └── run.py            # Main execution script
└── references/
    └── config.md         # Configuration documentation
```

### 2.3 Example: `watching-gmail` Skill

```yaml
# .claude/skills/watching-gmail/SKILL.md
---
name: watching-gmail
description: |
  Monitor Gmail inbox for new emails, classify by priority, and create task files.
  Use when setting up email monitoring, processing unread messages, or configuring
  email-based task creation. NOT when sending emails (use sending-emails skill).
---

# Gmail Watcher Skill

Monitors Gmail inbox and creates task files in Obsidian vault.

## Quick Start

```bash
# Start watching
python scripts/run.py

# Verify setup
python scripts/verify.py
```

## Configuration

Required files in `config/`:
- `credentials.json` - Google OAuth client credentials
- `token.json` - Authenticated token (auto-created on first run)

Environment variables:
- `GMAIL_POLL_INTERVAL` - Seconds between checks (default: 60)
- `DRY_RUN` - Test mode without creating files (default: false)

## Priority Classification

| Priority | Keywords |
|----------|----------|
| Urgent | urgent, asap, emergency, critical |
| High | important, invoice, payment, deadline |
| Medium | question, request, update |
| Low | thanks, fyi, newsletter |

## Output

Creates markdown files in `Vault/Needs_Action/`:
```markdown
---
source: gmail
priority: high
sender: client@example.com
---
# Email: Subject Line
...
```

## Verification

Run: `python scripts/verify.py`

Expected: `✓ watching-gmail valid`
```

### 2.4 Skill Verification Script Template

```python
# scripts/verify.py
#!/usr/bin/env python3
"""Verify skill is properly configured and ready to run."""

import sys
from pathlib import Path

def verify():
    errors = []

    # Check config files
    config_path = Path(__file__).parent.parent.parent.parent / "config"
    if not (config_path / "credentials.json").exists():
        errors.append("Missing config/credentials.json")

    # Check dependencies
    try:
        import google.oauth2.credentials
    except ImportError:
        errors.append("Missing dependency: google-auth-oauthlib")

    # Check vault structure
    vault_path = Path(__file__).parent.parent.parent.parent / "Vault"
    if not (vault_path / "Needs_Action").exists():
        errors.append("Missing Vault/Needs_Action directory")

    if errors:
        print("✗ watching-gmail invalid:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("✓ watching-gmail valid")
    return 0

if __name__ == "__main__":
    sys.exit(verify())
```

---

## Part 3: Implementation Order

### Phase 1: LinkedIn Foundation (Tasks 1-4)
1. Create `Vault/LinkedIn_Queue/` folder structure
2. Implement `src/linkedin/linkedin_poster.py` (browser automation)
3. Implement `src/linkedin/content_generator.py` (post generation)
4. Create Jinja2 templates for LinkedIn posts

### Phase 2: LinkedIn Integration (Tasks 5-7)
5. Add LinkedIn to orchestrator workflow
6. Implement scheduling & approval workflow
7. Add LinkedIn audit logging

### Phase 3: Skills Conversion - Watchers (Tasks 8-11)
8. Create `watching-gmail` skill
9. Create `watching-whatsapp` skill
10. Create `watching-filesystem` skill
11. Verify all watcher skills

### Phase 4: Skills Conversion - Core (Tasks 12-16)
12. Create `digital-fte-orchestrator` skill
13. Create `generating-ceo-briefing` skill
14. Create `sending-emails` skill
15. Create `posting-linkedin` skill
16. Create `managing-services` skill

### Phase 5: Integration & Testing (Tasks 17-19)
17. Update `service_manager.py` to use skills
18. End-to-end testing of all skills
19. Update documentation

---

## File Summary

### New Files (19 total)

**LinkedIn Module (9 files):**
- `src/linkedin/__init__.py`
- `src/linkedin/linkedin_poster.py`
- `src/linkedin/content_generator.py`
- `src/linkedin/linkedin_scheduler.py`
- `src/templates/linkedin/weekly_update.j2`
- `src/templates/linkedin/achievement.j2`
- `src/templates/linkedin/engagement.j2`
- `config/linkedin_config.json`
- `Vault/LinkedIn_Queue/.gitkeep`

**Agent Skills (8 skills × 3 files = 24 files):**
- `.claude/skills/watching-gmail/SKILL.md`
- `.claude/skills/watching-gmail/scripts/verify.py`
- `.claude/skills/watching-gmail/scripts/run.py`
- (similar structure for 7 other skills)

### Modified Files (3 total)
- `src/orchestrator.py` - Add LinkedIn workflow
- `src/service_manager.py` - Integrate skills
- `config/.env.example` - Add LinkedIn env vars

---

## Acceptance Criteria

### LinkedIn Auto-Posting
- [ ] Browser automation authenticates with LinkedIn
- [ ] Posts can be created from CEO Briefing data
- [ ] Manual posts from queue are supported
- [ ] All posts go through Pending_Approval workflow
- [ ] Audit log captures all LinkedIn actions
- [ ] Rate limiting enforced (max 2 posts/day)

### Agent Skills
- [ ] All 8 skills have valid SKILL.md with proper frontmatter
- [ ] All skills have working verify.py scripts
- [ ] Skills can be invoked via Claude Code
- [ ] Existing functionality preserved after conversion
- [ ] Service manager works with skill-based architecture

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LinkedIn blocks automation | Use realistic delays, respect rate limits |
| Session expires frequently | Persistent context + session health checks |
| Breaking existing watchers | Convert incrementally, keep originals as backup |
| Skill verification fails | Template-based approach ensures consistency |

---

## Estimated Effort

- **Phase 1-2 (LinkedIn):** 8 tasks
- **Phase 3-4 (Skills):** 9 tasks
- **Phase 5 (Integration):** 3 tasks
- **Total:** 20 tasks
