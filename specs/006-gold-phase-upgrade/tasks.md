# Gold Phase Upgrade - Tasks

**Feature Branch:** `002-gold-phase-upgrade`
**Created:** 2026-01-16
**Status:** In Progress
**Related Plan:** [plan.md](./plan.md)

---

## Task List

### Phase 1: LinkedIn Foundation ✅ COMPLETE

#### Task 1: Create LinkedIn Queue Folder Structure ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 5 mins

**Description:**
Create folder structure for manual LinkedIn post queue.

**Acceptance Criteria:**
- [x] `Vault/LinkedIn_Queue/` exists
- [x] `.gitkeep` file present

**Test:**
```bash
ls Vault/LinkedIn_Queue/.gitkeep
```

**Completed:** 2026-01-16

---

#### Task 2: Implement LinkedIn Poster (Browser Automation) ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 2-3 hours

**Description:**
Implement `src/linkedin/linkedin_poster.py` with Playwright browser automation for LinkedIn posting.

**Acceptance Criteria:**
- [x] Class `LinkedInPoster` implemented
- [x] `authenticate()` method for login/session handling
- [x] `create_post()` method for posting content
- [x] Rate limiting (max 2 posts/day, 1/hour)
- [x] Error handling and logging
- [x] Persistent browser context

**Test:**
```python
# Manual test in DRY_RUN mode
python src/linkedin/linkedin_poster.py --dry-run
```

**Completed:** 2026-01-16

---

#### Task 3: Implement Content Generator ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 1-2 hours

**Description:**
Implement `src/linkedin/content_generator.py` for generating LinkedIn posts from various sources.

**Acceptance Criteria:**
- [x] Class `ContentGenerator` implemented
- [x] `from_ceo_briefing()` method
- [x] `from_template()` method for Jinja2 rendering
- [x] Hashtag suggestion logic

**Test:**
```python
# Test with CEO briefing
python -c "from src.linkedin.content_generator import ContentGenerator; cg = ContentGenerator(); print(cg.from_ceo_briefing('Vault/CEO_Briefing_2026-01-16.md'))"
```

**Completed:** 2026-01-16

---

#### Task 4: Create Jinja2 Templates ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 30 mins

**Description:**
Create Jinja2 templates for different LinkedIn post types.

**Acceptance Criteria:**
- [x] `src/templates/linkedin/weekly_update.j2` exists
- [x] `src/templates/linkedin/achievement.j2` exists
- [x] `src/templates/linkedin/engagement.j2` exists
- [x] Templates use proper variables and formatting

**Test:**
```bash
ls src/templates/linkedin/*.j2
```

**Completed:** 2026-01-16

---

### Phase 2: LinkedIn Integration 🔄 IN PROGRESS

#### Task 5: Create LinkedIn Scheduler ⏳
**Status:** TODO
**Priority:** P1
**Estimated Effort:** 1-2 hours

**Description:**
Implement `src/linkedin/linkedin_scheduler.py` to schedule posts from queue.

**Acceptance Criteria:**
- [ ] Class `LinkedInScheduler` implemented
- [ ] Reads from `Vault/LinkedIn_Queue/` and `Vault/Approved/`
- [ ] Schedules posts based on config
- [ ] Moves posts through workflow (Queue → Pending_Approval → Approved → Done)
- [ ] Respects rate limits

**Test:**
```python
# Test scheduler with mock posts
python src/linkedin/linkedin_scheduler.py --test
```

**Files to Create:**
- `src/linkedin/linkedin_scheduler.py`

---

#### Task 6: Add LinkedIn Configuration ⏳
**Status:** TODO
**Priority:** P1
**Estimated Effort:** 15 mins

**Description:**
Create LinkedIn configuration file with posting preferences and schedule.

**Acceptance Criteria:**
- [ ] `config/linkedin_config.json` created
- [ ] Contains posting schedule (days, times)
- [ ] Contains rate limits
- [ ] Contains approval workflow settings

**Test:**
```bash
cat config/linkedin_config.json | python -m json.tool
```

**Files to Create:**
- `config/linkedin_config.json`

**Example Structure:**
```json
{
  "posting_schedule": {
    "days": ["Monday", "Wednesday", "Friday"],
    "preferred_times": ["09:00", "15:00"]
  },
  "rate_limits": {
    "max_per_day": 2,
    "max_per_hour": 1
  },
  "approval_required": true,
  "default_hashtags": ["AIAutomation", "Productivity"]
}
```

---

#### Task 7: Integrate LinkedIn into Orchestrator ⏳
**Status:** TODO
**Priority:** P1
**Estimated Effort:** 1 hour

**Description:**
Add LinkedIn posting workflow to the orchestrator's task processing loop.

**Acceptance Criteria:**
- [ ] Orchestrator checks `Vault/Approved/` for LinkedIn posts
- [ ] LinkedIn posts are processed by linkedin_poster
- [ ] Audit log updated after posting
- [ ] Error handling for LinkedIn failures

**Test:**
```bash
# Place approved post in Vault/Approved/
# Run orchestrator
python src/orchestrator.py --max-iterations 1
# Verify post was processed
```

**Files to Modify:**
- `src/orchestrator.py` (lines 80-200)

---

### Phase 3: Skills Conversion - Watchers ✅ COMPLETE

#### Task 8: Create `watching-gmail` Skill ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 45 mins

**Acceptance Criteria:**
- [x] `.claude/skills/watching-gmail/SKILL.md` with proper frontmatter
- [x] `scripts/verify.py` works
- [x] `scripts/run.py` executes gmail_watcher
- [x] References existing `src/watchers/gmail_watcher.py`

**Test:**
```bash
cd .claude/skills/watching-gmail
python scripts/verify.py
```

**Completed:** 2026-01-16

---

#### Task 9: Create `watching-whatsapp` Skill ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 45 mins

**Acceptance Criteria:**
- [x] `.claude/skills/watching-whatsapp/SKILL.md` with proper frontmatter
- [x] `scripts/verify.py` works
- [x] `scripts/run.py` executes whatsapp_watcher
- [x] References existing `src/watchers/whatsapp_watcher.py`

**Test:**
```bash
cd .claude/skills/watching-whatsapp
python scripts/verify.py
```

**Completed:** 2026-01-16

---

#### Task 10: Create `watching-filesystem` Skill ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 45 mins

**Acceptance Criteria:**
- [x] `.claude/skills/watching-filesystem/SKILL.md` with proper frontmatter
- [x] `scripts/verify.py` works
- [x] `scripts/run.py` executes filesystem_watcher
- [x] References existing `src/watchers/filesystem_watcher.py`

**Test:**
```bash
cd .claude/skills/watching-filesystem
python scripts/verify.py
```

**Completed:** 2026-01-16

---

#### Task 11: Verify All Watcher Skills ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 15 mins

**Acceptance Criteria:**
- [x] All 3 watcher skills pass verification
- [x] Skills can be invoked via Claude Code
- [x] Skills documentation is complete

**Test:**
```bash
python scripts/verify.py
# Expected output: ✓ watching-gmail valid, ✓ watching-whatsapp valid, ✓ watching-filesystem valid
```

**Completed:** 2026-01-16

---

### Phase 4: Skills Conversion - Core ✅ COMPLETE

#### Task 12: Create `digital-fte-orchestrator` Skill ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 1 hour

**Acceptance Criteria:**
- [x] `.claude/skills/digital-fte-orchestrator/SKILL.md` with proper frontmatter
- [x] Documents Ralph Wiggum loop pattern
- [x] `scripts/verify.py` works
- [x] `scripts/run.py` executes orchestrator

**Test:**
```bash
cd .claude/skills/digital-fte-orchestrator
python scripts/verify.py
```

**Completed:** 2026-01-16

---

#### Task 13: Create `generating-ceo-briefing` Skill ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 45 mins

**Acceptance Criteria:**
- [x] `.claude/skills/generating-ceo-briefing/SKILL.md` with proper frontmatter
- [x] `scripts/verify.py` works
- [x] `scripts/run.py` executes ceo_briefing generator
- [x] References existing `src/reports/ceo_briefing.py`

**Test:**
```bash
cd .claude/skills/generating-ceo-briefing
python scripts/verify.py
```

**Completed:** 2026-01-16

---

#### Task 14: Create `sending-emails` Skill ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 45 mins

**Acceptance Criteria:**
- [x] `.claude/skills/sending-emails/SKILL.md` with proper frontmatter
- [x] `scripts/verify.py` works
- [x] `scripts/run.py` uses email_sender MCP
- [x] References existing `src/mcp_servers/email_sender.py`

**Test:**
```bash
cd .claude/skills/sending-emails
python scripts/verify.py
```

**Completed:** 2026-01-16

---

#### Task 15: Create `posting-linkedin` Skill ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 45 mins

**Acceptance Criteria:**
- [x] `.claude/skills/posting-linkedin/SKILL.md` with proper frontmatter
- [x] `scripts/verify.py` works
- [x] `scripts/run.py` executes linkedin_poster
- [x] References `src/linkedin/linkedin_poster.py`

**Test:**
```bash
cd .claude/skills/posting-linkedin
python scripts/verify.py
```

**Completed:** 2026-01-16

---

#### Task 16: Create `managing-services` Skill ✅
**Status:** DONE
**Priority:** P1
**Estimated Effort:** 45 mins

**Acceptance Criteria:**
- [x] `.claude/skills/managing-services/SKILL.md` with proper frontmatter
- [x] `scripts/verify.py` works
- [x] `scripts/run.py` uses service_manager
- [x] References existing `src/service_manager.py`

**Test:**
```bash
cd .claude/skills/managing-services
python scripts/verify.py
```

**Completed:** 2026-01-16

---

### Phase 5: Integration & Testing ⏳ PENDING

#### Task 17: Update Service Manager for Skills ⏳
**Status:** TODO
**Priority:** P2
**Estimated Effort:** 1 hour

**Description:**
Update `src/service_manager.py` to work seamlessly with the skill-based architecture.

**Acceptance Criteria:**
- [ ] Service manager can start all watchers via skills
- [ ] Service manager can start orchestrator via skill
- [ ] Health checks work with skill-based services
- [ ] Auto-restart functionality preserved

**Test:**
```bash
python src/service_manager.py --start-all
python src/service_manager.py --status
# Verify all services running
```

**Files to Modify:**
- `src/service_manager.py`

---

#### Task 18: End-to-End Testing ⏳
**Status:** TODO
**Priority:** P1
**Estimated Effort:** 2 hours

**Description:**
Perform comprehensive end-to-end testing of the entire system.

**Acceptance Criteria:**
- [ ] All watchers can be started via skills
- [ ] Orchestrator processes tasks correctly
- [ ] LinkedIn posting workflow works end-to-end
- [ ] CEO briefing generation works
- [ ] Email sending works via skill
- [ ] No regressions in existing functionality

**Test Scenarios:**
1. **Gmail → Orchestrator → Done**
   - Send test email
   - Verify task created in Needs_Action
   - Verify task processed to Done

2. **LinkedIn Queue → Pending → Approved → Posted**
   - Create manual post in LinkedIn_Queue
   - Verify moves to Pending_Approval
   - Approve post
   - Verify posted and moved to Done

3. **CEO Briefing → LinkedIn Post**
   - Generate CEO briefing
   - Verify LinkedIn post created
   - Verify approval workflow

**Test:**
```bash
# Run full system test
python tests/e2e_gold_phase_test.py
```

---

#### Task 19: Update Documentation ⏳
**Status:** TODO
**Priority:** P2
**Estimated Effort:** 1 hour

**Description:**
Update all documentation to reflect Gold Phase changes.

**Acceptance Criteria:**
- [ ] README.md updated with skills information
- [ ] SKILLS-INDEX.md lists all 8 custom skills
- [ ] Each skill's SKILL.md is complete and accurate
- [ ] LinkedIn posting workflow documented
- [ ] Environment variables documented in `.env.example`

**Test:**
```bash
# Verify documentation completeness
cat README.md | grep -i "skills"
cat .claude/skills/SKILLS-INDEX.md
```

**Files to Modify:**
- `README.md`
- `.claude/skills/SKILLS-INDEX.md`
- `config/.env.example`

---

## Progress Summary

### Overall Status: 75% Complete

**Completed:** 16 tasks
**In Progress:** 0 tasks
**Remaining:** 3 tasks

### Phase Status:
- ✅ Phase 1: LinkedIn Foundation (4/4 tasks)
- 🔄 Phase 2: LinkedIn Integration (0/3 tasks)
- ✅ Phase 3: Skills Conversion - Watchers (4/4 tasks)
- ✅ Phase 4: Skills Conversion - Core (5/5 tasks)
- ⏳ Phase 5: Integration & Testing (0/3 tasks)

---

## Remaining Work

### Critical Path:
1. Task 5: Create LinkedIn Scheduler
2. Task 6: Add LinkedIn Configuration
3. Task 7: Integrate LinkedIn into Orchestrator
4. Task 18: End-to-End Testing

### Non-Critical:
- Task 17: Update Service Manager (enhancement)
- Task 19: Update Documentation (polish)

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| LinkedIn scheduler complexity | Medium | Keep logic simple, use existing patterns |
| Orchestrator integration breaks existing flow | High | Test thoroughly, maintain backward compatibility |
| Skills verification issues | Low | Already verified, just need final checks |

---

## Next Steps

1. **Immediate:** Complete Task 5 (LinkedIn Scheduler)
2. **Then:** Complete Task 6 (LinkedIn Config)
3. **Then:** Complete Task 7 (Orchestrator Integration)
4. **Finally:** Tasks 17-19 (Testing & Documentation)

---

**Notes:**
- All watcher and core skills are implemented and functional
- LinkedIn foundation is solid, just needs scheduling and integration
- Testing will be crucial to ensure no regressions
