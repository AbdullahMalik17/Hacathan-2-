# Enhanced Gmail Watcher - Complete Guide

> **Version:** 2.0 | **Last Updated:** 2026-01-17

This document explains the enhanced Gmail watcher with AI exclusion, 3-tier importance classification, and auto-reply capabilities.

---

## Table of Contents

1. [Overview](#overview)
2. [How It's Triggered](#how-its-triggered)
3. [AI Exclusion Label](#ai-exclusion-label)
4. [Importance Classification](#importance-classification)
5. [Auto-Reply System](#auto-reply-system)
6. [Sender Reputation](#sender-reputation)
7. [Configuration](#configuration)
8. [Usage Examples](#usage-examples)

---

## Overview

The Gmail Watcher is a polling-based system that:
- Monitors your Gmail inbox every 60 seconds
- Classifies emails by importance (important/medium/not important)
- Creates task files in the Obsidian vault
- Automatically generates reply drafts for important emails
- Learns from sender history to improve classification
- Excludes emails labeled with `NO_AI` from processing

---

## How It's Triggered

### Triggering Mechanism

**Location:** `src/watchers/gmail_watcher.py:639`

```python
while True:
    # Check Gmail every 60 seconds
    new_emails = fetch_new_emails(service)
    # Process each email...
    time.sleep(POLL_INTERVAL)  # Default: 60 seconds
```

**Process Flow:**

1. **Poll Gmail API** (every 60 seconds)
   - Query: `is:unread in:inbox`
   - Fetches up to 20 unread emails

2. **Check Exclusion Label**
   - If email has `NO_AI` label → Skip and mark as processed
   - Otherwise → Continue to classification

3. **Determine Importance**
   - Check sender domain reputation
   - Check sender history (last 10 emails)
   - Match keywords in subject/snippet
   - Classify as: important, medium, or not_important

4. **Create Task File**
   - Generate markdown file in `Vault/Needs_Action/`
   - Include metadata, content, suggested actions
   - Add auto-reply recommendation (if important)

5. **Handle Auto-Reply**
   - If importance = "important" AND auto-reply enabled
   - Create draft reply in Gmail
   - Log draft ID for reference

6. **Update Reputation**
   - Track sender email and classification
   - Update sender reputation database
   - Learn patterns over time

---

## AI Exclusion Label

### Setting Up the NO_AI Label

**Step 1: Create Label in Gmail**

1. Go to Gmail Settings → Labels
2. Create new label: `NO_AI`
3. Choose a color (e.g., red for "stop")

**Step 2: Apply to Emails**

**Manual:**
- Select email(s)
- Click label icon
- Select `NO_AI`

**Automatic (Gmail Filters):**
1. Gmail Settings → Filters and Blocked Addresses
2. Create new filter:
   ```
   From: personal-friend@example.com
   Apply label: NO_AI
   ```

### What Happens to NO_AI Emails

```python
# src/watchers/gmail_watcher.py:569
if has_exclusion_label(full_msg):
    logger.info(f"Skipping email - has NO_AI label")
    processed_ids.add(msg['id'])  # Mark as processed
    continue  # Skip all processing
```

**Effects:**
- ✅ Email remains in your inbox (untouched)
- ✅ Marked as "processed" (won't be checked again)
- ❌ No task file created
- ❌ No auto-reply
- ❌ No importance classification
- ❌ No sender reputation tracking

### Best Practices

**Use NO_AI for:**
- Personal emails from family/friends
- Confidential business communications
- Banking/financial sensitive emails
- Legal correspondence you want to handle personally
- Anything requiring human nuance

**Don't use NO_AI for:**
- Routine business emails
- Newsletters (use "not_important" classification instead)
- Emails you want tracked but not auto-replied

---

## Importance Classification

### 3-Tier System

#### 🔴 IMPORTANT (Immediate Attention)

**Triggers:**
```python
# Keywords
"urgent", "asap", "emergency", "security alert", "breach"
"payment due", "invoice due", "deadline today"
"client emergency", "production down", "critical bug"
"legal notice", "court", "compliance"
```

**Sender-based:**
- Domain in `KNOWN_IMPORTANT_DOMAINS` (banks, lawyers, clients)
- Sender has 3+ important emails in last 10 classifications

**Actions:**
- Creates task file with auto-reply recommendation
- Generates draft reply (if AUTO_REPLY_ENABLED=true)
- Response expected within 1 hour
- Logs to daily activity log

**Example Task File:**
```markdown
# 🔴 Email: Payment Due Today - Invoice #1234

## Metadata
- **Importance:** IMPORTANT
- **Sender Reputation:** clientdomain.com

## 🤖 Auto-Reply Recommendation
**Status:** Ready to send automatic acknowledgment

**Actions:**
- [ ] Auto-send acknowledgment
- [ ] Draft for approval
- [ ] Skip auto-reply
```

#### 🟡 MEDIUM (24-Hour Review)

**Triggers:**
```python
"important", "invoice", "payment", "meeting", "client"
"question", "request", "update", "information", "follow-up"
```

**Actions:**
- Creates task file
- No auto-reply (unless manually configured)
- Tracks sender reputation
- Response within 24 hours

#### 🟢 NOT IMPORTANT (Low Priority)

**Triggers:**
```python
"newsletter", "notification", "subscription", "digest"
"promotional", "marketing", "social media"
```

**Actions:**
- Creates task file (can be auto-archived)
- No auto-reply
- Can be bulk-processed
- Review within 72 hours or archive

### Classification Algorithm

**Location:** `src/watchers/gmail_watcher.py:193`

```python
def determine_importance(subject, snippet, sender):
    # 1. Check domain reputation (highest priority)
    if domain in KNOWN_IMPORTANT_DOMAINS:
        return "important"

    # 2. Check sender history (3+ important = important)
    if sender has 3+ important emails in last 10:
        return "important"

    # 3. Keyword matching (ordered by importance)
    for importance, keywords in IMPORTANCE_KEYWORDS.items():
        if any(keyword in text):
            return importance

    # 4. Default to medium
    return "medium"
```

---

## Auto-Reply System

### Configuration

**Environment Variables:**
```bash
# .env or system environment
AUTO_REPLY_ENABLED=true   # Enable auto-reply drafts
GMAIL_POLL_INTERVAL=60    # Check every 60 seconds
```

**Code Configuration:**
```python
# src/watchers/gmail_watcher.py:81
AUTO_REPLY_ENABLED = os.getenv("AUTO_REPLY_ENABLED", "false").lower() == "true"
AUTO_REPLY_IMPORTANT_ONLY = True  # Only for important emails
```

### Auto-Reply Templates

**Important Email Template:**
```
Hi [Sender Name],

Thank you for your message regarding "[Subject]".

I've received your email and marked it as high priority.
I'm reviewing it now and will respond with a detailed
reply within the next hour.

If this is extremely urgent, please feel free to call
me directly.

Best regards,
Abdullah Junior
(Automated Response - Digital FTE)
```

**Medium Priority Template:**
```
Hi [Sender Name],

Thank you for your email about "[Subject]".

I've received your message and will review it shortly.
You can expect a response within 24 hours.

If this requires immediate attention, please reply with
"URGENT" in the subject line.

Best regards,
Abdullah Junior
(Automated Response - Digital FTE)
```

### Draft vs. Auto-Send

**Current Implementation: DRAFT (Safer)**

```python
# src/watchers/gmail_watcher.py:664
draft_id = create_auto_reply_draft(service, email, importance)
```

**Benefits:**
- ✅ Human review before sending
- ✅ Can edit before sending
- ✅ Prevents accidental sends
- ✅ Safer for testing

**To Enable Auto-Send (Advanced):**

Replace in main loop:
```python
if filepath and importance == "important":
    if AUTO_REPLY_ENABLED:
        # Auto-send instead of draft
        success = send_auto_reply(service, email, importance)
```

⚠️ **Warning:** Auto-send can be risky. Start with drafts.

---

## Sender Reputation

### How It Works

**Data Structure:**
```json
{
  "sender@example.com": {
    "first_seen": "2026-01-17T10:00:00",
    "last_seen": "2026-01-17T15:00:00",
    "email_count": 5,
    "importance_history": [
      "important",
      "important",
      "medium",
      "important",
      "medium"
    ]
  }
}
```

**Storage:** `config/known_senders.json`

**Update Mechanism:**
```python
# src/watchers/gmail_watcher.py:162
def update_sender_reputation(sender_email, importance):
    # Add to history (max 10)
    # Track first_seen, last_seen, email_count
```

**Classification Impact:**
```python
# If sender has 3+ important emails out of last 10
if important_count >= 3:
    return "important"
```

### Managing Reputation

**View Reputation:**
```bash
cat config/known_senders.json | jq
```

**Add Important Sender:**
```python
# Edit src/watchers/gmail_watcher.py:85
KNOWN_IMPORTANT_DOMAINS = {
    "your-client.com": "important",
    "your-bank.com": "important",
}
```

**Reset Reputation:**
```bash
rm config/known_senders.json
# Will rebuild from scratch
```

---

## Configuration

### Required Scopes

```python
# src/watchers/gmail_watcher.py:36
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/gmail.modify',    # Add labels
    'https://www.googleapis.com/auth/gmail.send'       # Send/draft
]
```

**⚠️ Important:** After changing scopes, delete `config/token.json` and re-authenticate.

### Environment Variables

```bash
# Required
GMAIL_CREDENTIALS_PATH=config/credentials.json

# Optional
GMAIL_POLL_INTERVAL=60        # Seconds between checks (default: 60)
AUTO_REPLY_ENABLED=true       # Enable auto-reply drafts (default: false)
DRY_RUN=false                 # Test mode without creating files (default: false)
```

### Important Domain Configuration

**Edit:** `src/watchers/gmail_watcher.py:85-93`

```python
KNOWN_IMPORTANT_DOMAINS = {
    # Add your important domains
    "client.com": "important",
    "bank.com": "important",
    "lawyer.com": "important",
    # Medium importance
    "vendor.com": "medium",
    "partner.com": "medium"
}
```

---

## Usage Examples

### Example 1: Exclude Personal Emails

**Scenario:** You want to exclude all emails from your family.

**Solution:**
1. Create Gmail filter:
   ```
   From: mom@example.com OR dad@example.com OR sister@example.com
   Apply label: NO_AI
   ```

2. Emails automatically excluded from AI processing

### Example 2: Prioritize Client Emails

**Scenario:** All emails from `bigclient.com` should be important.

**Solution:**
1. Edit `src/watchers/gmail_watcher.py`:
   ```python
   KNOWN_IMPORTANT_DOMAINS = {
       "bigclient.com": "important",
   }
   ```

2. Restart watcher
3. All emails from `@bigclient.com` → classified as important → auto-reply draft created

### Example 3: Test Auto-Reply

**Scenario:** Test the auto-reply system safely.

**Steps:**
1. Set `AUTO_REPLY_ENABLED=true` in environment
2. Send yourself a test email with subject: "URGENT: Test Email"
3. Wait 60 seconds for watcher to poll
4. Check `Vault/Needs_Action/` for task file
5. Check Gmail → Drafts for auto-reply
6. Review draft, edit if needed, send manually

### Example 4: Monitor Logs

**Check watcher activity:**
```bash
# Real-time monitoring
tail -f Vault/Logs/gmail_watcher_2026-01-17.log

# Check processed emails
cat Vault/Logs/2026-01-17.json | jq '.[] | select(.action == "email_processed")'
```

**Sample log entry:**
```json
{
  "timestamp": "2026-01-17T10:30:00",
  "action": "email_processed",
  "actor": "gmail_watcher",
  "message_id": "abc123",
  "subject": "Invoice Due",
  "sender": "vendor@example.com",
  "importance": "important",
  "task_file": "Vault/Needs_Action/2026-01-17_10-30_gmail_important_Invoice Due.md",
  "auto_reply_draft": "draft_xyz789",
  "result": "success"
}
```

---

## Troubleshooting

### Issue: Emails Not Being Processed

**Check:**
1. Is watcher running? `ps aux | grep gmail_watcher`
2. Check logs: `tail Vault/Logs/gmail_watcher_*.log`
3. Verify credentials: `ls config/token.json`
4. Check processed IDs: `cat config/processed_emails.json`

### Issue: Wrong Importance Classification

**Solutions:**
1. Add domain to `KNOWN_IMPORTANT_DOMAINS`
2. Check keyword matching in `IMPORTANCE_KEYWORDS`
3. Review sender reputation: `cat config/known_senders.json`

### Issue: Auto-Reply Not Created

**Check:**
1. `AUTO_REPLY_ENABLED=true` in environment
2. Email classified as "important"
3. Gmail API scopes include `gmail.send`
4. Re-authenticate if scopes changed: `rm config/token.json`

### Issue: NO_AI Label Not Working

**Check:**
1. Label name matches exactly: `NO_AI` (case-sensitive in Gmail)
2. Email actually has the label (check in Gmail)
3. Watcher logs show "Skipping email - has NO_AI label"

---

## Advanced Customization

### Custom Importance Keywords

**Edit:** `src/watchers/gmail_watcher.py:57-78`

```python
IMPORTANCE_KEYWORDS = {
    "important": [
        # Add your custom keywords
        "project deadline",
        "board meeting",
        "quarterly review"
    ],
    # ...
}
```

### Custom Auto-Reply Template

**Edit:** `src/watchers/gmail_watcher.py:283-307`

```python
reply_templates = {
    "important": f"""Your custom template here

    Use {sender_name} and {subject} variables
    """,
}
```

### Change AI Exclusion Label

**Edit:** `src/watchers/gmail_watcher.py:54`

```python
AI_EXCLUSION_LABEL = "PRIVATE"  # Use any label name
```

---

## Performance & Limits

### API Quotas
- Gmail API: 1 billion quota units/day
- Each list call: ~5 units
- Each get call: ~10 units
- At 60s interval: ~1,440 checks/day ≈ 20,000 units (well within limit)

### Disk Usage
- Task files: ~2-5 KB each
- Known senders: ~1-2 KB per 100 senders
- Logs: ~10-20 MB/month

### Processing Speed
- Email classification: <100ms
- Task file creation: <50ms
- Draft creation: ~200-500ms
- Total per email: ~500-1000ms

---

## Security Considerations

1. **Credentials Storage**
   - Store `credentials.json` and `token.json` securely
   - Add to `.gitignore`
   - Use environment variables for sensitive config

2. **Auto-Reply Safety**
   - Start with drafts (not auto-send)
   - Review templates before enabling
   - Test with personal emails first

3. **Label Privacy**
   - NO_AI label visible to you only
   - No data sent to external services
   - All processing local

4. **Sender Reputation**
   - Stored locally in `config/known_senders.json`
   - Cleared with file deletion
   - Not shared with any service

---

## Migration from Old Version

If upgrading from the old Gmail watcher:

1. **Backup:**
   ```bash
   cp config/processed_emails.json config/processed_emails.backup.json
   ```

2. **Update Scopes:**
   ```bash
   rm config/token.json  # Force re-authentication
   ```

3. **Test:**
   ```bash
   DRY_RUN=true python src/watchers/gmail_watcher.py
   ```

4. **Deploy:**
   - Remove DRY_RUN
   - Enable auto-reply if desired
   - Monitor logs for 24 hours

---

## Support & Feedback

**Logs Location:** `Vault/Logs/`
**Config Location:** `config/`
**Task Files:** `Vault/Needs_Action/`

**Common Files:**
- `config/credentials.json` - Google OAuth credentials
- `config/token.json` - Authentication token
- `config/processed_emails.json` - Processed message IDs
- `config/known_senders.json` - Sender reputation database
