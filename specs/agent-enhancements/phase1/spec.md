# Phase 1: Smart Communication

**Version:** 1.0
**Date:** 2026-01-23
**Status:** Ready for Implementation
**Duration:** 5-7 days
**Effort:** ~20 hours

---

## Overview

Phase 1 focuses on making email communication smarter and establishing a daily planning routine. By the end of this phase, Abdullah Junior will:

1. Send a morning digest with today's priorities
2. Automatically categorize incoming emails
3. Track and remind about unanswered emails
4. Summarize long email threads

---

## Feature 1: Daily Digest Email

### Description
Every morning at a configured time (default 7:00 AM), the agent sends a comprehensive digest to the user summarizing:
- Urgent items requiring attention
- Today's calendar events
- Pending drafts awaiting approval
- Follow-ups due today
- Yesterday's activity summary
- AI-generated recommendations

### User Story
> As a busy professional, I want to receive a morning briefing so that I know exactly what needs my attention today without checking multiple apps.

### Technical Design

#### Data Structure
```python
# src/models/daily_digest.py

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional
from enum import Enum

@dataclass
class EmailSummary:
    id: str
    sender: str
    subject: str
    preview: str  # First 100 chars
    category: str
    received_at: datetime
    importance_score: float

@dataclass
class TaskSummary:
    id: str
    title: str
    priority: str
    source: str  # "email", "manual", "scheduled"
    due_date: Optional[datetime]

@dataclass
class CalendarEvent:
    id: str
    title: str
    start_time: datetime
    end_time: datetime
    location: Optional[str]
    attendees: List[str]

@dataclass
class ActivitySummary:
    emails_processed: int
    tasks_completed: int
    drafts_approved: int
    drafts_rejected: int
    social_posts: int
    meetings_scheduled: int

@dataclass
class DailyDigest:
    date: date
    greeting: str
    weather: Optional[str]

    # Priority items
    urgent_emails: List[EmailSummary]
    action_items: List[TaskSummary]

    # Schedule
    todays_events: List[CalendarEvent]

    # Pending work
    pending_drafts: int
    drafts_needing_review: List[dict]

    # Follow-ups
    follow_ups_due: List[dict]
    overdue_follow_ups: List[dict]

    # Summary
    yesterday: ActivitySummary

    # AI recommendations
    recommendations: List[str]

    # Metadata
    generated_at: datetime = field(default_factory=datetime.now)
```

#### Digest Generator Service
```python
# src/services/daily_digest.py

class DailyDigestService:
    """Generates and sends daily digest emails."""

    def __init__(self, config: Config):
        self.config = config
        self.gmail = GmailClient()
        self.calendar = CalendarClient()
        self.vault = VaultReader()
        self.ai = AIClient()

    async def generate_digest(self, target_date: date = None) -> DailyDigest:
        """Generate digest for given date (default: today)."""
        target_date = target_date or date.today()

        # Gather data in parallel
        urgent_emails, action_items, events, drafts, follow_ups, yesterday = await asyncio.gather(
            self._get_urgent_emails(),
            self._get_action_items(),
            self._get_todays_events(target_date),
            self._get_pending_drafts(),
            self._get_due_follow_ups(target_date),
            self._get_yesterday_summary(),
        )

        # Generate AI recommendations
        recommendations = await self._generate_recommendations(
            urgent_emails, action_items, events, follow_ups
        )

        # Build greeting
        greeting = self._generate_greeting(target_date, len(urgent_emails))

        return DailyDigest(
            date=target_date,
            greeting=greeting,
            urgent_emails=urgent_emails,
            action_items=action_items,
            todays_events=events,
            pending_drafts=len(drafts),
            drafts_needing_review=drafts[:5],  # Top 5
            follow_ups_due=follow_ups,
            overdue_follow_ups=[f for f in follow_ups if f['days_overdue'] > 0],
            yesterday=yesterday,
            recommendations=recommendations,
        )

    async def send_digest(self, digest: DailyDigest) -> bool:
        """Send digest via email."""
        html = self._render_digest_html(digest)

        return await self.gmail.send_email(
            to=self.config.user_email,
            subject=f"☀️ Your Daily Briefing - {digest.date.strftime('%A, %B %d')}",
            html_body=html,
        )

    def _generate_greeting(self, target_date: date, urgent_count: int) -> str:
        """Generate personalized greeting."""
        hour = datetime.now().hour
        day_name = target_date.strftime('%A')

        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 17:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"

        if urgent_count == 0:
            status = "You're all caught up! 🎉"
        elif urgent_count <= 3:
            status = f"You have {urgent_count} items needing attention."
        else:
            status = f"Busy day ahead - {urgent_count} urgent items waiting."

        return f"{time_greeting}! Happy {day_name}. {status}"
```

#### Email Template
```html
<!-- src/templates/daily_digest.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; border-radius: 12px; }
        .section { background: #f8fafc; border-radius: 8px; padding: 20px; margin: 20px 0; }
        .urgent { border-left: 4px solid #ef4444; }
        .action { border-left: 4px solid #f59e0b; }
        .fyi { border-left: 4px solid #3b82f6; }
        .item { padding: 12px; border-bottom: 1px solid #e2e8f0; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; }
        .badge-urgent { background: #fef2f2; color: #dc2626; }
        .badge-action { background: #fffbeb; color: #d97706; }
        .recommendation { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 12px; margin: 8px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ greeting }}</h1>
            <p>{{ date }}</p>
        </div>

        {% if urgent_emails %}
        <div class="section urgent">
            <h2>🚨 Urgent Items ({{ urgent_emails|length }})</h2>
            {% for email in urgent_emails %}
            <div class="item">
                <strong>{{ email.sender }}</strong>
                <p>{{ email.subject }}</p>
                <small>{{ email.preview }}</small>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if todays_events %}
        <div class="section">
            <h2>📅 Today's Schedule</h2>
            {% for event in todays_events %}
            <div class="item">
                <strong>{{ event.start_time.strftime('%H:%M') }}</strong> - {{ event.title }}
                {% if event.location %}<br><small>📍 {{ event.location }}</small>{% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if follow_ups_due %}
        <div class="section action">
            <h2>⏰ Follow-ups Due</h2>
            {% for fu in follow_ups_due %}
            <div class="item">
                <strong>{{ fu.contact }}</strong> - {{ fu.subject }}
                <br><small>Sent {{ fu.days_ago }} days ago</small>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if pending_drafts > 0 %}
        <div class="section">
            <h2>📝 Drafts Awaiting Approval ({{ pending_drafts }})</h2>
            <p><a href="{{ dashboard_url }}">Review in Dashboard →</a></p>
        </div>
        {% endif %}

        {% if recommendations %}
        <div class="section">
            <h2>💡 Recommendations</h2>
            {% for rec in recommendations %}
            <div class="recommendation">{{ rec }}</div>
            {% endfor %}
        </div>
        {% endif %}

        <div class="section" style="background: #1e293b; color: white;">
            <h2>📊 Yesterday's Activity</h2>
            <p>✉️ {{ yesterday.emails_processed }} emails processed</p>
            <p>✅ {{ yesterday.tasks_completed }} tasks completed</p>
            <p>📱 {{ yesterday.social_posts }} social posts</p>
        </div>

        <footer style="text-align: center; color: #64748b; padding: 20px;">
            <p>Abdullah Junior - Your Digital FTE</p>
            <p><a href="{{ settings_url }}">Manage digest settings</a></p>
        </footer>
    </div>
</body>
</html>
```

#### Scheduler
```python
# src/services/digest_scheduler.py

class DigestScheduler:
    """Schedules daily digest generation and sending."""

    def __init__(self, config: Config):
        self.config = config
        self.digest_service = DailyDigestService(config)
        self.send_time = config.digest_send_time or time(7, 0)  # 7:00 AM default

    async def run(self):
        """Main scheduler loop."""
        while True:
            now = datetime.now()
            next_send = self._next_send_time(now)

            # Wait until send time
            wait_seconds = (next_send - now).total_seconds()
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

            # Generate and send digest
            try:
                digest = await self.digest_service.generate_digest()
                success = await self.digest_service.send_digest(digest)

                if success:
                    log_audit("DIGEST_SENT", {"date": str(digest.date)})
                else:
                    log_audit("DIGEST_FAILED", {"date": str(digest.date)})
            except Exception as e:
                log_error(f"Digest generation failed: {e}")

            # Wait for next day
            await asyncio.sleep(60)  # Check every minute to avoid drift

    def _next_send_time(self, now: datetime) -> datetime:
        """Calculate next send time."""
        today_send = now.replace(
            hour=self.send_time.hour,
            minute=self.send_time.minute,
            second=0,
            microsecond=0
        )

        if now >= today_send:
            # Already past today's send time, schedule for tomorrow
            return today_send + timedelta(days=1)
        return today_send
```

### Configuration
```yaml
# config/digest.yaml
daily_digest:
  enabled: true
  send_time: "07:00"  # 24-hour format
  timezone: "Asia/Karachi"
  include_weather: true
  max_urgent_items: 10
  max_recommendations: 5
  recipient_email: "${USER_EMAIL}"
```

### Acceptance Criteria
- [ ] Digest sent automatically at configured time
- [ ] Includes all sections: urgent, calendar, follow-ups, drafts, summary
- [ ] AI recommendations are relevant and actionable
- [ ] Email renders correctly on mobile devices
- [ ] User can configure send time
- [ ] Digest skipped on weekends (configurable)

---

## Feature 2: Email Auto-Categorization

### Description
Automatically categorize incoming emails into predefined categories to help prioritize and organize the inbox.

### Categories
| Category | Color | Criteria |
|----------|-------|----------|
| **Urgent** | Red | Keywords: urgent, ASAP, immediately, deadline today |
| **Action Required** | Orange | Questions, requests, needs response |
| **Meeting** | Purple | Calendar invites, scheduling requests |
| **Financial** | Green | Invoices, receipts, banking |
| **Newsletter** | Blue | Subscription emails, digests |
| **Promotional** | Gray | Marketing, sales, offers |
| **Personal** | Teal | Known personal contacts |
| **FYI** | Light Blue | CC'd, informational |

### Technical Design

```python
# src/intelligence/email_categorizer.py

from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple
import re

class EmailCategory(Enum):
    URGENT = "urgent"
    ACTION_REQUIRED = "action"
    MEETING = "meeting"
    FINANCIAL = "financial"
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promo"
    PERSONAL = "personal"
    FYI = "fyi"
    SPAM = "spam"

@dataclass
class CategoryResult:
    category: EmailCategory
    confidence: float  # 0-1
    reasons: List[str]

class EmailCategorizer:
    """AI-powered email categorization."""

    URGENT_KEYWORDS = [
        "urgent", "asap", "immediately", "critical", "emergency",
        "deadline", "time-sensitive", "priority", "important"
    ]

    ACTION_KEYWORDS = [
        "please", "could you", "can you", "would you", "need",
        "request", "action required", "respond", "reply", "confirm"
    ]

    MEETING_KEYWORDS = [
        "meeting", "schedule", "calendar", "invite", "call",
        "zoom", "teams", "meet", "appointment", "availability"
    ]

    FINANCIAL_KEYWORDS = [
        "invoice", "receipt", "payment", "bill", "statement",
        "transaction", "bank", "transfer", "amount", "due"
    ]

    def __init__(self, ai_client=None, contacts_db=None):
        self.ai = ai_client
        self.contacts = contacts_db or {}

    def categorize(self, email: dict) -> CategoryResult:
        """Categorize a single email."""

        # Extract features
        sender = email.get('sender', '').lower()
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()[:1000]  # First 1000 chars
        combined = f"{subject} {body}"

        # Rule-based checks first (fast)
        result = self._rule_based_categorize(sender, subject, body, combined)
        if result.confidence > 0.8:
            return result

        # AI-based categorization for uncertain cases
        if self.ai and result.confidence < 0.6:
            ai_result = self._ai_categorize(email)
            if ai_result.confidence > result.confidence:
                return ai_result

        return result

    def _rule_based_categorize(
        self, sender: str, subject: str, body: str, combined: str
    ) -> CategoryResult:
        """Rule-based categorization."""

        reasons = []
        scores = {cat: 0.0 for cat in EmailCategory}

        # Check for urgent keywords
        urgent_matches = [kw for kw in self.URGENT_KEYWORDS if kw in combined]
        if urgent_matches:
            scores[EmailCategory.URGENT] += 0.3 * len(urgent_matches)
            reasons.append(f"Contains urgent keywords: {urgent_matches[:3]}")

        # Check for action keywords
        action_matches = [kw for kw in self.ACTION_KEYWORDS if kw in combined]
        if action_matches:
            scores[EmailCategory.ACTION_REQUIRED] += 0.2 * len(action_matches)
            reasons.append(f"Contains action keywords: {action_matches[:3]}")

        # Check for meeting keywords
        meeting_matches = [kw for kw in self.MEETING_KEYWORDS if kw in combined]
        if meeting_matches:
            scores[EmailCategory.MEETING] += 0.3 * len(meeting_matches)
            reasons.append(f"Contains meeting keywords: {meeting_matches[:3]}")

        # Check for financial keywords
        financial_matches = [kw for kw in self.FINANCIAL_KEYWORDS if kw in combined]
        if financial_matches:
            scores[EmailCategory.FINANCIAL] += 0.3 * len(financial_matches)
            reasons.append(f"Contains financial keywords: {financial_matches[:3]}")

        # Check for newsletter patterns
        if self._is_newsletter(sender, subject, body):
            scores[EmailCategory.NEWSLETTER] += 0.7
            reasons.append("Matches newsletter pattern")

        # Check for promotional patterns
        if self._is_promotional(sender, subject, body):
            scores[EmailCategory.PROMOTIONAL] += 0.6
            reasons.append("Matches promotional pattern")

        # Check if personal contact
        if self._is_personal_contact(sender):
            scores[EmailCategory.PERSONAL] += 0.5
            reasons.append("From personal contact")

        # Check if CC'd (FYI)
        if email.get('is_cc', False):
            scores[EmailCategory.FYI] += 0.4
            reasons.append("You are CC'd")

        # Get highest scoring category
        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category], 1.0)

        # Default to FYI if no strong signal
        if confidence < 0.3:
            best_category = EmailCategory.FYI
            confidence = 0.5
            reasons.append("No strong category signal, defaulting to FYI")

        return CategoryResult(
            category=best_category,
            confidence=confidence,
            reasons=reasons
        )

    def _is_newsletter(self, sender: str, subject: str, body: str) -> bool:
        """Check if email is a newsletter."""
        newsletter_patterns = [
            r"unsubscribe",
            r"view in browser",
            r"email preferences",
            r"weekly digest",
            r"newsletter",
            r"noreply@",
            r"no-reply@",
        ]
        combined = f"{sender} {subject} {body}"
        return any(re.search(p, combined, re.I) for p in newsletter_patterns)

    def _is_promotional(self, sender: str, subject: str, body: str) -> bool:
        """Check if email is promotional."""
        promo_patterns = [
            r"\d+%\s*off",
            r"sale",
            r"discount",
            r"limited time",
            r"offer expires",
            r"shop now",
            r"buy now",
            r"free shipping",
        ]
        combined = f"{subject} {body}"
        return any(re.search(p, combined, re.I) for p in promo_patterns)

    def _is_personal_contact(self, sender: str) -> bool:
        """Check if sender is a known personal contact."""
        return sender in self.contacts.get('personal', [])

    async def _ai_categorize(self, email: dict) -> CategoryResult:
        """Use AI for complex categorization."""
        prompt = f"""Categorize this email into one of these categories:
- urgent: Needs immediate attention
- action: Requires response or action
- meeting: Meeting/scheduling related
- financial: Money, invoices, banking
- newsletter: Subscription content
- promo: Marketing/promotional
- personal: From friends/family
- fyi: Informational, no action needed
- spam: Junk/unwanted

Email:
From: {email.get('sender')}
Subject: {email.get('subject')}
Body: {email.get('body', '')[:500]}

Respond with JSON: {{"category": "...", "confidence": 0.X, "reason": "..."}}"""

        response = await self.ai.complete(prompt)
        # Parse AI response...
        return CategoryResult(...)
```

### Integration with Gmail Watcher
```python
# src/watchers/gmail_watcher.py (modification)

async def process_email(self, email: dict):
    """Process incoming email with categorization."""

    # Categorize email
    categorizer = EmailCategorizer(ai_client=self.ai, contacts_db=self.contacts)
    category_result = categorizer.categorize(email)

    # Add category to email metadata
    email['category'] = category_result.category.value
    email['category_confidence'] = category_result.confidence
    email['category_reasons'] = category_result.reasons

    # Log categorization
    log_audit("EMAIL_CATEGORIZED", {
        "email_id": email['id'],
        "category": category_result.category.value,
        "confidence": category_result.confidence,
    })

    # Create task with category-aware priority
    priority = self._category_to_priority(category_result.category)
    await self.create_task(email, priority=priority)
```

### Acceptance Criteria
- [ ] All incoming emails are categorized
- [ ] Categorization happens within 5 seconds
- [ ] Accuracy > 85% on test set
- [ ] Categories visible in dashboard
- [ ] User can override categories
- [ ] Learning from corrections (Phase 3)

---

## Feature 3: Follow-up Reminder System

### Description
Track sent emails and remind user when no response is received within a configurable time period.

### Technical Design

```python
# src/services/follow_up_tracker.py

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum

class FollowUpStatus(Enum):
    PENDING = "pending"       # Waiting for response
    REMINDED = "reminded"     # User has been reminded
    RESOLVED = "resolved"     # Response received or manually resolved
    DISMISSED = "dismissed"   # User dismissed reminder

@dataclass
class FollowUp:
    id: str
    email_id: str
    thread_id: str
    contact_email: str
    contact_name: str
    subject: str
    sent_date: datetime
    reminder_days: int  # Days before reminder
    reminder_date: datetime
    status: FollowUpStatus
    reminded_count: int = 0
    last_reminded: Optional[datetime] = None
    notes: Optional[str] = None

class FollowUpTracker:
    """Tracks sent emails and generates follow-up reminders."""

    DEFAULT_REMINDER_DAYS = {
        'urgent': 1,
        'action': 3,
        'meeting': 2,
        'financial': 5,
        'default': 3,
    }

    def __init__(self, storage, gmail_client, config):
        self.storage = storage
        self.gmail = gmail_client
        self.config = config

    async def track_sent_email(self, email: dict):
        """Start tracking a sent email for follow-up."""

        # Determine reminder period based on content
        reminder_days = self._determine_reminder_days(email)

        follow_up = FollowUp(
            id=f"fu_{email['id']}",
            email_id=email['id'],
            thread_id=email['thread_id'],
            contact_email=email['to'],
            contact_name=email.get('to_name', email['to']),
            subject=email['subject'],
            sent_date=datetime.now(),
            reminder_days=reminder_days,
            reminder_date=datetime.now() + timedelta(days=reminder_days),
            status=FollowUpStatus.PENDING,
        )

        await self.storage.save_follow_up(follow_up)
        log_audit("FOLLOW_UP_CREATED", {"email_id": email['id'], "reminder_days": reminder_days})

    async def check_for_responses(self):
        """Check if any tracked emails have received responses."""

        pending = await self.storage.get_pending_follow_ups()

        for follow_up in pending:
            # Check Gmail for replies in thread
            has_response = await self.gmail.check_thread_for_response(
                thread_id=follow_up.thread_id,
                since=follow_up.sent_date
            )

            if has_response:
                follow_up.status = FollowUpStatus.RESOLVED
                await self.storage.update_follow_up(follow_up)
                log_audit("FOLLOW_UP_RESOLVED", {"id": follow_up.id, "reason": "response_received"})

    async def get_due_reminders(self) -> List[FollowUp]:
        """Get all follow-ups that are due for reminder."""

        pending = await self.storage.get_pending_follow_ups()
        now = datetime.now()

        due = []
        for follow_up in pending:
            if now >= follow_up.reminder_date:
                due.append(follow_up)

        return sorted(due, key=lambda f: f.reminder_date)

    async def send_reminder(self, follow_up: FollowUp):
        """Send reminder notification to user."""

        days_waiting = (datetime.now() - follow_up.sent_date).days

        # Create reminder notification
        notification = {
            "type": "follow_up_reminder",
            "title": f"No response from {follow_up.contact_name}",
            "body": f"'{follow_up.subject}' - sent {days_waiting} days ago",
            "actions": [
                {"action": "send_follow_up", "label": "Send Follow-up"},
                {"action": "dismiss", "label": "Dismiss"},
                {"action": "snooze", "label": "Remind Tomorrow"},
            ],
            "data": {
                "follow_up_id": follow_up.id,
                "email_id": follow_up.email_id,
                "contact": follow_up.contact_email,
            }
        }

        # Update follow-up status
        follow_up.status = FollowUpStatus.REMINDED
        follow_up.reminded_count += 1
        follow_up.last_reminded = datetime.now()
        # Set next reminder for 2 days later
        follow_up.reminder_date = datetime.now() + timedelta(days=2)

        await self.storage.update_follow_up(follow_up)

        return notification

    async def generate_follow_up_draft(self, follow_up: FollowUp) -> dict:
        """Generate a follow-up email draft."""

        days_waiting = (datetime.now() - follow_up.sent_date).days

        # AI-generated follow-up
        draft_content = await self._generate_follow_up_content(follow_up, days_waiting)

        draft = {
            "to": follow_up.contact_email,
            "subject": f"Re: {follow_up.subject}",
            "body": draft_content,
            "thread_id": follow_up.thread_id,
            "action_type": "follow_up_email",
            "metadata": {
                "original_email_id": follow_up.email_id,
                "days_since_original": days_waiting,
            }
        }

        return draft

    async def _generate_follow_up_content(self, follow_up: FollowUp, days: int) -> str:
        """Generate polite follow-up email content."""

        templates = {
            'short': f"""Hi {follow_up.contact_name.split()[0]},

Just following up on my email from {days} days ago regarding "{follow_up.subject}".

Would love to hear your thoughts when you have a moment.

Best regards""",

            'medium': f"""Hi {follow_up.contact_name.split()[0]},

I wanted to follow up on my previous email about "{follow_up.subject}" sent on {follow_up.sent_date.strftime('%B %d')}.

I understand you're busy, but I wanted to make sure this didn't slip through the cracks.

Please let me know if you need any additional information from my end.

Best regards""",
        }

        return templates['short'] if days < 5 else templates['medium']

    def _determine_reminder_days(self, email: dict) -> int:
        """Determine reminder period based on email content."""

        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()

        # Check for urgency indicators
        if any(word in subject for word in ['urgent', 'asap', 'critical']):
            return self.DEFAULT_REMINDER_DAYS['urgent']

        # Check for meeting-related
        if any(word in subject for word in ['meeting', 'schedule', 'call']):
            return self.DEFAULT_REMINDER_DAYS['meeting']

        # Check for financial
        if any(word in subject for word in ['invoice', 'payment', 'quote']):
            return self.DEFAULT_REMINDER_DAYS['financial']

        return self.DEFAULT_REMINDER_DAYS['default']
```

### Storage Schema
```python
# Database/file storage for follow-ups

# Vault/Data/follow_ups.json
{
    "follow_ups": [
        {
            "id": "fu_abc123",
            "email_id": "abc123",
            "thread_id": "thread_xyz",
            "contact_email": "client@example.com",
            "contact_name": "John Smith",
            "subject": "Project Proposal",
            "sent_date": "2026-01-20T10:30:00Z",
            "reminder_days": 3,
            "reminder_date": "2026-01-23T10:30:00Z",
            "status": "pending",
            "reminded_count": 0,
            "last_reminded": null
        }
    ]
}
```

### Acceptance Criteria
- [ ] Sent emails automatically tracked
- [ ] Reminders generated after X days (configurable)
- [ ] Response detection marks as resolved
- [ ] One-click follow-up email generation
- [ ] Snooze option for reminders
- [ ] Dismiss option to stop tracking
- [ ] Follow-ups visible in dashboard

---

## Feature 4: Email Summarization

### Description
Generate concise summaries of long email threads to quickly understand context without reading entire conversations.

### Technical Design

```python
# src/intelligence/email_summarizer.py

from dataclasses import dataclass
from typing import List

@dataclass
class EmailSummary:
    thread_id: str
    subject: str
    participants: List[str]
    message_count: int
    summary: str
    key_points: List[str]
    action_items: List[str]
    sentiment: str  # positive, negative, neutral
    generated_at: datetime

class EmailSummarizer:
    """AI-powered email thread summarization."""

    def __init__(self, ai_client):
        self.ai = ai_client

    async def summarize_thread(self, thread: dict) -> EmailSummary:
        """Summarize an email thread."""

        messages = thread.get('messages', [])

        # Skip if too short
        if len(messages) < 3:
            return None

        # Prepare thread content
        thread_content = self._format_thread(messages)

        # Generate summary with AI
        prompt = f"""Summarize this email thread concisely:

{thread_content}

Provide:
1. A 2-3 sentence summary
2. Key points (bullet list)
3. Any action items mentioned
4. Overall sentiment (positive/negative/neutral)

Format as JSON:
{{
    "summary": "...",
    "key_points": ["...", "..."],
    "action_items": ["...", "..."],
    "sentiment": "..."
}}"""

        response = await self.ai.complete(prompt)
        result = json.loads(response)

        return EmailSummary(
            thread_id=thread['id'],
            subject=thread['subject'],
            participants=list(set(m['from'] for m in messages)),
            message_count=len(messages),
            summary=result['summary'],
            key_points=result['key_points'],
            action_items=result['action_items'],
            sentiment=result['sentiment'],
            generated_at=datetime.now(),
        )

    def _format_thread(self, messages: List[dict]) -> str:
        """Format messages for AI processing."""

        formatted = []
        for msg in messages[-10:]:  # Last 10 messages max
            formatted.append(f"""
From: {msg['from']}
Date: {msg['date']}
---
{msg['body'][:500]}
""")
        return "\n---\n".join(formatted)

    async def summarize_for_digest(self, emails: List[dict]) -> List[str]:
        """Generate brief summaries for daily digest."""

        summaries = []
        for email in emails[:10]:  # Top 10 emails
            summary = f"**{email['sender']}**: {email['subject']}"

            # Add brief AI summary if long
            if len(email.get('body', '')) > 500:
                brief = await self._generate_brief(email)
                summary += f"\n  _{brief}_"

            summaries.append(summary)

        return summaries

    async def _generate_brief(self, email: dict) -> str:
        """Generate one-line summary."""

        prompt = f"Summarize in one sentence (max 15 words):\n{email['body'][:300]}"
        return await self.ai.complete(prompt)
```

### Acceptance Criteria
- [ ] Threads with 3+ messages get summaries
- [ ] Summary includes key points and action items
- [ ] Sentiment analysis accurate
- [ ] Summaries cached to avoid re-generation
- [ ] One-click summarize in dashboard
- [ ] Summaries included in relevant tasks

---

## Implementation Tasks

### Task P1-001: Daily Digest System
**Effort:** 4 hours

1. Create `src/models/daily_digest.py` with data structures
2. Create `src/services/daily_digest.py` with generation logic
3. Create `src/templates/daily_digest.html` email template
4. Create `src/services/digest_scheduler.py` for scheduling
5. Add configuration options to `config/digest.yaml`
6. Integrate with orchestrator startup
7. Write tests

### Task P1-002: Email Categorization
**Effort:** 6 hours

1. Create `src/intelligence/email_categorizer.py`
2. Implement rule-based categorization
3. Add AI fallback for uncertain cases
4. Integrate with Gmail watcher
5. Add category to task metadata
6. Update dashboard to show categories
7. Write tests

### Task P1-003: Follow-up Tracker
**Effort:** 6 hours

1. Create `src/services/follow_up_tracker.py`
2. Create storage for follow-ups
3. Implement response detection
4. Create reminder notification system
5. Add follow-up draft generation
6. Integrate with email sending workflow
7. Add to daily digest
8. Write tests

### Task P1-004: Email Summarization
**Effort:** 4 hours

1. Create `src/intelligence/email_summarizer.py`
2. Implement thread summarization
3. Add caching for summaries
4. Integrate with task creation
5. Add to daily digest
6. Write tests

---

## Testing Plan

### Unit Tests
- [ ] Categorizer correctly classifies sample emails
- [ ] Follow-up tracker calculates dates correctly
- [ ] Digest generator includes all sections
- [ ] Summarizer handles edge cases

### Integration Tests
- [ ] End-to-end digest generation and sending
- [ ] Gmail watcher with categorization
- [ ] Follow-up tracking through email lifecycle

### User Acceptance Tests
- [ ] Digest arrives at configured time
- [ ] Categories match user expectations
- [ ] Reminders are timely and useful
- [ ] Summaries are accurate and helpful

---

**Next:** See `phase1/tasks.md` for detailed task breakdown with estimates.
