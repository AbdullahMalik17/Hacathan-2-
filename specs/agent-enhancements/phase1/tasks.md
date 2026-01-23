# Phase 1: Implementation Tasks

**Total Estimated Effort:** 20 hours
**Duration:** 5-7 days
**Status:** Ready to Start

---

## Task Overview

| Task ID | Title | Effort | Priority | Dependencies |
|---------|-------|--------|----------|--------------|
| P1-001 | Daily Digest System | 4h | P0 | None |
| P1-002 | Email Categorization | 6h | P0 | None |
| P1-003 | Follow-up Tracker | 6h | P0 | P1-002 |
| P1-004 | Email Summarization | 4h | P1 | P1-002 |

---

## P1-001: Daily Digest System

**Estimated Time:** 4 hours
**Priority:** P0 (Critical)
**Dependencies:** None

### Objective
Create a system that generates and sends a comprehensive morning briefing email.

### Subtasks

#### P1-001.1: Create Data Models (30 min)
```
Files to create:
- src/models/daily_digest.py

Acceptance Criteria:
- [ ] DailyDigest dataclass defined
- [ ] EmailSummary dataclass defined
- [ ] CalendarEvent dataclass defined
- [ ] ActivitySummary dataclass defined
- [ ] All fields have type hints
```

#### P1-001.2: Create Digest Generator Service (90 min)
```
Files to create:
- src/services/daily_digest.py

Functions to implement:
- generate_digest(target_date) -> DailyDigest
- _get_urgent_emails() -> List[EmailSummary]
- _get_action_items() -> List[TaskSummary]
- _get_todays_events(date) -> List[CalendarEvent]
- _get_pending_drafts() -> List[dict]
- _get_due_follow_ups(date) -> List[dict]
- _get_yesterday_summary() -> ActivitySummary
- _generate_recommendations() -> List[str]
- _generate_greeting() -> str

Acceptance Criteria:
- [ ] All data sources integrated
- [ ] Async operations for performance
- [ ] Error handling for missing data
- [ ] Logging for debugging
```

#### P1-001.3: Create Email Template (45 min)
```
Files to create:
- src/templates/email/daily_digest.html
- src/templates/email/daily_digest.txt (plain text fallback)

Sections to include:
- Header with greeting and date
- Urgent items (red accent)
- Today's calendar
- Follow-ups due
- Pending drafts count
- Yesterday's summary
- AI recommendations
- Footer with settings link

Acceptance Criteria:
- [ ] Responsive design (mobile-friendly)
- [ ] Dark mode compatible
- [ ] All sections render correctly
- [ ] Links work properly
```

#### P1-001.4: Create Scheduler Service (45 min)
```
Files to create:
- src/services/digest_scheduler.py

Functions to implement:
- run() - Main scheduler loop
- _next_send_time(now) -> datetime
- _should_send_today() -> bool (skip weekends if configured)

Acceptance Criteria:
- [ ] Sends at configured time
- [ ] Handles timezone correctly
- [ ] Recovers from missed sends
- [ ] Weekend skip option works
```

#### P1-001.5: Configuration & Integration (30 min)
```
Files to modify:
- config/.env.example (add DIGEST_* variables)
- src/orchestrator.py (start digest scheduler)
- src/utils/config.py (add digest config)

Configuration options:
- DIGEST_ENABLED=true
- DIGEST_SEND_TIME=07:00
- DIGEST_TIMEZONE=Asia/Karachi
- DIGEST_SKIP_WEEKENDS=false
- DIGEST_RECIPIENT=user@example.com

Acceptance Criteria:
- [ ] All config options work
- [ ] Digest scheduler starts with orchestrator
- [ ] Can be disabled via config
```

#### P1-001.6: Write Tests (30 min)
```
Files to create:
- tests/test_daily_digest.py

Test cases:
- test_digest_generation()
- test_greeting_generation()
- test_template_rendering()
- test_scheduler_timing()
- test_weekend_skip()

Acceptance Criteria:
- [ ] All tests pass
- [ ] >80% code coverage
```

---

## P1-002: Email Categorization

**Estimated Time:** 6 hours
**Priority:** P0 (Critical)
**Dependencies:** None

### Objective
Automatically categorize incoming emails into predefined categories.

### Subtasks

#### P1-002.1: Create Category Models (30 min)
```
Files to create:
- src/models/email_category.py

Enums/Classes:
- EmailCategory enum
- CategoryResult dataclass
- CategoryConfig dataclass

Acceptance Criteria:
- [ ] All categories defined
- [ ] Result includes confidence score
- [ ] Result includes reasoning
```

#### P1-002.2: Implement Rule-Based Categorizer (90 min)
```
Files to create:
- src/intelligence/email_categorizer.py

Functions to implement:
- categorize(email) -> CategoryResult
- _rule_based_categorize() -> CategoryResult
- _check_urgent_keywords() -> float
- _check_action_keywords() -> float
- _check_meeting_keywords() -> float
- _check_financial_keywords() -> float
- _is_newsletter() -> bool
- _is_promotional() -> bool
- _is_personal_contact() -> bool

Acceptance Criteria:
- [ ] All keyword lists comprehensive
- [ ] Scoring logic correct
- [ ] Handles edge cases
- [ ] Fast execution (<100ms)
```

#### P1-002.3: Implement AI Fallback (60 min)
```
Files to modify:
- src/intelligence/email_categorizer.py

Functions to implement:
- _ai_categorize(email) -> CategoryResult
- _build_categorization_prompt() -> str
- _parse_ai_response() -> CategoryResult

Acceptance Criteria:
- [ ] AI called only when confidence < 0.6
- [ ] Prompt is clear and constrained
- [ ] Response parsing handles errors
- [ ] Caching to avoid repeated AI calls
```

#### P1-002.4: Integrate with Gmail Watcher (60 min)
```
Files to modify:
- src/watchers/gmail_watcher.py

Changes:
- Add categorizer initialization
- Call categorize() for each email
- Add category to email metadata
- Map category to task priority
- Log categorization results

Acceptance Criteria:
- [ ] All emails categorized
- [ ] Category in task metadata
- [ ] Audit log records category
- [ ] No performance degradation
```

#### P1-002.5: Update Dashboard (60 min)
```
Files to modify:
- frontend/src/components/TaskBoard.tsx
- frontend/src/app/api/tasks/route.ts (if exists)

Changes:
- Add category badge to task cards
- Add category filter dropdown
- Color-code by category
- Show category in task details

Acceptance Criteria:
- [ ] Categories visible on cards
- [ ] Filter by category works
- [ ] Colors match category scheme
```

#### P1-002.6: Write Tests (60 min)
```
Files to create:
- tests/test_email_categorizer.py

Test cases:
- test_urgent_detection()
- test_action_detection()
- test_meeting_detection()
- test_newsletter_detection()
- test_promotional_detection()
- test_ai_fallback()
- test_confidence_scoring()

Test data:
- Create sample emails for each category
- Include edge cases and ambiguous examples

Acceptance Criteria:
- [ ] All tests pass
- [ ] Accuracy > 85% on test set
```

---

## P1-003: Follow-up Tracker

**Estimated Time:** 6 hours
**Priority:** P0 (Critical)
**Dependencies:** P1-002

### Objective
Track sent emails and remind user when no response is received.

### Subtasks

#### P1-003.1: Create Follow-up Models (30 min)
```
Files to create:
- src/models/follow_up.py

Classes:
- FollowUpStatus enum
- FollowUp dataclass
- FollowUpReminder dataclass

Acceptance Criteria:
- [ ] All statuses defined
- [ ] Date tracking fields correct
- [ ] Reminder count tracked
```

#### P1-003.2: Create Storage Layer (45 min)
```
Files to create:
- src/storage/follow_up_storage.py

Functions:
- save_follow_up(follow_up)
- get_follow_up(id) -> FollowUp
- get_pending_follow_ups() -> List[FollowUp]
- get_due_reminders(date) -> List[FollowUp]
- update_follow_up(follow_up)
- delete_follow_up(id)

Storage location:
- Vault/Data/follow_ups.json

Acceptance Criteria:
- [ ] CRUD operations work
- [ ] File-based storage persists
- [ ] Thread-safe operations
```

#### P1-003.3: Implement Tracker Service (90 min)
```
Files to create:
- src/services/follow_up_tracker.py

Functions:
- track_sent_email(email)
- check_for_responses()
- get_due_reminders() -> List[FollowUp]
- send_reminder(follow_up) -> Notification
- generate_follow_up_draft(follow_up) -> dict
- resolve_follow_up(id, reason)
- snooze_follow_up(id, days)
- dismiss_follow_up(id)
- _determine_reminder_days(email) -> int

Acceptance Criteria:
- [ ] Auto-tracking on email send
- [ ] Response detection works
- [ ] Reminder generation correct
- [ ] Draft generation helpful
```

#### P1-003.4: Integrate with Email Sending (60 min)
```
Files to modify:
- src/mcp_servers/email_sender.py
- src/local_agent.py (or wherever emails are sent)

Changes:
- Hook into email send completion
- Call track_sent_email() automatically
- Pass relevant metadata

Acceptance Criteria:
- [ ] All sent emails tracked
- [ ] Thread ID captured
- [ ] No manual tracking needed
```

#### P1-003.5: Create Reminder Notifications (45 min)
```
Files to modify:
- src/services/follow_up_tracker.py
- frontend/src/components/pwa/NotificationPrompt.tsx

Changes:
- Create notification payload
- Support action buttons (Follow-up, Dismiss, Snooze)
- Handle action callbacks

Acceptance Criteria:
- [ ] Push notifications work
- [ ] Action buttons functional
- [ ] Actions update follow-up status
```

#### P1-003.6: Add to Daily Digest (30 min)
```
Files to modify:
- src/services/daily_digest.py

Changes:
- Include due follow-ups section
- Include overdue follow-ups (highlighted)
- Sort by urgency

Acceptance Criteria:
- [ ] Follow-ups in digest
- [ ] Overdue items highlighted
- [ ] Links to dashboard work
```

#### P1-003.7: Write Tests (60 min)
```
Files to create:
- tests/test_follow_up_tracker.py

Test cases:
- test_track_new_email()
- test_response_detection()
- test_reminder_timing()
- test_draft_generation()
- test_snooze_functionality()
- test_dismiss_functionality()

Acceptance Criteria:
- [ ] All tests pass
- [ ] Edge cases covered
```

---

## P1-004: Email Summarization

**Estimated Time:** 4 hours
**Priority:** P1 (Important)
**Dependencies:** P1-002

### Objective
Generate concise summaries of long email threads.

### Subtasks

#### P1-004.1: Create Summary Models (20 min)
```
Files to create:
- src/models/email_summary.py

Classes:
- EmailSummary dataclass
- SummaryCache dataclass

Acceptance Criteria:
- [ ] All fields defined
- [ ] Cache includes TTL
```

#### P1-004.2: Implement Summarizer Service (90 min)
```
Files to create:
- src/intelligence/email_summarizer.py

Functions:
- summarize_thread(thread) -> EmailSummary
- summarize_email(email) -> str
- summarize_for_digest(emails) -> List[str]
- _format_thread(messages) -> str
- _generate_brief(email) -> str
- _extract_action_items(text) -> List[str]
- _analyze_sentiment(text) -> str

Acceptance Criteria:
- [ ] Threads summarized accurately
- [ ] Key points extracted
- [ ] Action items identified
- [ ] Sentiment correct
```

#### P1-004.3: Implement Caching (30 min)
```
Files to modify:
- src/intelligence/email_summarizer.py

Changes:
- Cache summaries by thread_id
- Set TTL (e.g., 24 hours)
- Invalidate on new message

Storage:
- Vault/Cache/summaries.json

Acceptance Criteria:
- [ ] Summaries cached
- [ ] Cache invalidation works
- [ ] No repeated AI calls
```

#### P1-004.4: Integrate with Task Creation (45 min)
```
Files to modify:
- src/watchers/gmail_watcher.py

Changes:
- Check if thread is long (3+ messages)
- Generate summary
- Add summary to task metadata

Acceptance Criteria:
- [ ] Long threads get summaries
- [ ] Summary in task card
- [ ] Can expand to see full
```

#### P1-004.5: Add Dashboard UI (45 min)
```
Files to modify:
- frontend/src/components/TaskBoard.tsx

Changes:
- Show "Summarize" button for long threads
- Display summary in expandable section
- Show key points and action items

Acceptance Criteria:
- [ ] Summarize button visible
- [ ] Summary displays nicely
- [ ] Loading state shown
```

#### P1-004.6: Write Tests (30 min)
```
Files to create:
- tests/test_email_summarizer.py

Test cases:
- test_thread_summarization()
- test_brief_generation()
- test_action_item_extraction()
- test_sentiment_analysis()
- test_caching()

Acceptance Criteria:
- [ ] All tests pass
```

---

## Definition of Done

### For Each Task
- [ ] Code implemented and working
- [ ] Unit tests written and passing
- [ ] Integration tested
- [ ] Code reviewed (self-review minimum)
- [ ] Documentation updated
- [ ] Committed with clear message

### For Phase 1 Complete
- [ ] All P0 tasks complete
- [ ] Daily digest sending successfully
- [ ] Email categorization working
- [ ] Follow-up tracking active
- [ ] Dashboard updated with new features
- [ ] No critical bugs
- [ ] User acceptance test passed

---

## Execution Order

```
Day 1:
├── P1-001.1: Create Data Models (30 min)
├── P1-001.2: Create Digest Generator (90 min)
├── P1-001.3: Create Email Template (45 min)
└── P1-002.1: Create Category Models (30 min)

Day 2:
├── P1-002.2: Rule-Based Categorizer (90 min)
├── P1-002.3: AI Fallback (60 min)
└── P1-002.4: Integrate with Gmail (60 min)

Day 3:
├── P1-003.1: Follow-up Models (30 min)
├── P1-003.2: Storage Layer (45 min)
├── P1-003.3: Tracker Service (90 min)
└── P1-003.4: Email Integration (60 min)

Day 4:
├── P1-001.4: Scheduler Service (45 min)
├── P1-001.5: Config & Integration (30 min)
├── P1-003.5: Reminder Notifications (45 min)
├── P1-003.6: Add to Digest (30 min)
└── P1-004.1-3: Summarization (2.5 hours)

Day 5:
├── P1-002.5: Dashboard Categories (60 min)
├── P1-004.4-5: Summarization UI (90 min)
├── All Tests (2 hours)
└── Final Integration Testing

Day 6-7:
├── Bug fixes
├── Performance optimization
└── User acceptance testing
```

---

## Ready to Start?

Run this command to begin:
```bash
# Create the file structure
mkdir -p src/models src/services src/intelligence src/storage src/templates/email
touch src/models/daily_digest.py
touch src/models/email_category.py
touch src/models/follow_up.py
touch src/services/daily_digest.py
touch src/services/digest_scheduler.py
touch src/services/follow_up_tracker.py
touch src/intelligence/email_categorizer.py
touch src/intelligence/email_summarizer.py
touch src/storage/follow_up_storage.py
```

Then start with **P1-001.1: Create Data Models**.
