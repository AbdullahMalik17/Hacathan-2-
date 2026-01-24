# NO_AI Label Configuration Guide

> **Purpose:** Exclude specific emails from AI processing

---

## ✅ Current Status

**Label Name:** `NO_AI`
**Status:** Active in Gmail Watcher
**Effect:** Emails with this label are completely skipped

---

## 📋 Step-by-Step Setup

### Step 1: Verify Label Exists in Gmail

1. Go to Gmail (https://mail.google.com)
2. Look at left sidebar under "Labels"
3. Confirm you see **"NO_AI"** label

If not created yet:
- Click "More" → "Create new label"
- Name: `NO_AI`
- Color: Red (recommended - indicates "stop")

---

## 🎯 How to Use NO_AI Label

### Method 1: Manual Application

**For Individual Emails:**
1. Select email(s) in Gmail
2. Click label icon (tag icon in toolbar)
3. Check "NO_AI"
4. Done! Email will be excluded

**For Conversations:**
- Apply label to entire conversation thread
- All future emails in that thread get the label

### Method 2: Automatic Gmail Filters (Recommended)

This is the most powerful way - automatically label emails before AI sees them.

---

## 🔧 Gmail Filter Examples

### Filter 1: Exclude Specific Senders

**Use case:** Personal emails from family/friends

**Setup:**
1. Gmail Settings → Filters and Blocked Addresses
2. Click "Create a new filter"
3. **From:** `mom@example.com OR dad@example.com OR friend@example.com`
4. Click "Create filter"
5. ✓ Check "Apply the label:" → Select "NO_AI"
6. ✓ Check "Also apply filter to matching conversations" (optional)
7. Click "Create filter"

**Result:** All emails from these senders automatically excluded

---

### Filter 2: Exclude by Domain

**Use case:** Exclude all emails from a specific domain

**Setup:**
1. Create new filter
2. **From:** `@personaldomain.com`
3. Apply label: NO_AI

**Example:**
```
From: @family-domain.com
→ Apply label: NO_AI
```

---

### Filter 3: Exclude by Subject Keywords

**Use case:** Private/confidential emails

**Setup:**
1. Create new filter
2. **Subject:** `PRIVATE OR CONFIDENTIAL OR PERSONAL`
3. Apply label: NO_AI

**Result:** Any email with these words in subject is excluded

---

### Filter 4: Exclude Specific Email Addresses + Keep in Inbox

**Use case:** Important personal contacts you want to handle manually

**Setup:**
1. **From:** `wife@example.com OR lawyer@example.com`
2. **Actions:**
   - ✓ Apply label: NO_AI
   - ✓ Star it (optional - makes it stand out)
   - ✓ Mark as important (optional)

---

### Filter 5: Exclude by Multiple Criteria

**Use case:** Complex exclusion rules

**Setup:**
```
From: (@personal-domain.com OR mom@gmail.com OR friend@yahoo.com)
Has the words: (personal OR private)
→ Apply label: NO_AI
```

---

## 📱 Common Use Cases

### Use Case 1: Exclude Personal Communications

**Who to exclude:**
- Family members
- Close friends
- Personal contacts

**Why:**
- Too personal for AI
- Require human nuance
- Sensitive topics

**Filter:**
```
From: family1@email.com OR family2@email.com OR friend@email.com
→ NO_AI label
```

---

### Use Case 2: Exclude Sensitive Business

**What to exclude:**
- Banking/financial institutions
- Legal communications
- HR/payroll emails
- Medical/health information

**Filter:**
```
From: (@yourbank.com OR @yourlawfirm.com OR hr@company.com)
→ NO_AI label
```

---

### Use Case 3: Exclude by Email Thread

**Scenario:** Ongoing sensitive discussion

**How:**
1. Open the email thread
2. Click "More" (three dots)
3. "Filter messages like this"
4. Adjust filter criteria
5. Apply NO_AI label

---

### Use Case 4: Temporary Exclusion

**Scenario:** You want to handle certain emails manually this week

**How:**
1. Create filter with date range (if needed)
2. Apply NO_AI
3. Delete filter when done

---

## 🧪 Testing the Configuration

### Test 1: Manual Label Test

1. **Find an email** in your inbox (any email)
2. **Apply NO_AI label** manually
3. **Check Gmail watcher logs:**
   ```bash
   tail -f Vault/Logs/gmail_watcher_2026-01-17.log
   ```
4. **Look for:** `Skipping email - has NO_AI label`
5. **Verify:** No task file created in `Vault/Needs_Action/`

### Test 2: Filter Test

1. **Send yourself a test email** from excluded sender
2. **Gmail filter** should auto-apply NO_AI
3. **Wait 60 seconds** (poll interval)
4. **Check logs** - should show "Skipping email"
5. **Verify** no task file created

---

## 📊 Monitoring NO_AI Emails

### Check Logs for Excluded Emails

```bash
# See all excluded emails
grep "Skipping email" Vault/Logs/gmail_watcher_2026-01-17.log

# Count how many excluded today
grep -c "has NO_AI label" Vault/Logs/gmail_watcher_2026-01-17.log
```

### View Emails with NO_AI Label in Gmail

Gmail search:
```
label:NO_AI
```

Or:
```
label:NO_AI is:unread
```

---

## 🛠️ Advanced Configuration

### Change the Label Name

If you want to use a different label name:

**Edit:** `src/watchers/gmail_watcher.py` (line 54)

```python
# Change from:
AI_EXCLUSION_LABEL = "NO_AI"

# To your preferred name:
AI_EXCLUSION_LABEL = "PRIVATE"
# or
AI_EXCLUSION_LABEL = "SKIP_AI"
# or
AI_EXCLUSION_LABEL = "MANUAL_ONLY"
```

**Important:** After changing:
1. Restart Gmail watcher
2. Update Gmail filters to use new label name

---

### Multiple Exclusion Labels

Currently only one label is supported. To exclude multiple labels:

**Edit:** `src/watchers/gmail_watcher.py` (line 263)

```python
def has_exclusion_label(email_data: Dict[str, Any]) -> bool:
    """Check if email has exclusion labels."""
    label_ids = email_data.get('labelIds', [])

    # List of exclusion labels
    exclusion_labels = ["NO_AI", "PRIVATE", "MANUAL"]

    for label_id in label_ids:
        for exclusion in exclusion_labels:
            if exclusion.lower() in label_id.lower():
                return True

    return False
```

---

## 🔍 Troubleshooting

### Problem: Emails Still Being Processed

**Check:**
1. Label is spelled exactly: `NO_AI` (case matters in Gmail)
2. Label is applied to the email
3. Gmail watcher is running with latest code
4. Check logs: `grep "Skipping" Vault/Logs/gmail_watcher*.log`

**Debug:**
```bash
# Test label detection
cd src/watchers
python -c "
import gmail_watcher as gw
print('Exclusion label:', gw.AI_EXCLUSION_LABEL)
"
```

### Problem: Filter Not Auto-Applying Label

**Check:**
1. Gmail Settings → Filters → Verify filter exists
2. Filter criteria matches your emails
3. "Apply the label: NO_AI" is checked
4. Test by sending email that matches filter

**Fix:**
1. Delete and recreate filter
2. Test with simple criteria first
3. Expand criteria once working

### Problem: Can't Find NO_AI in Label List

**Solution:**
1. Gmail → Settings → Labels
2. Scroll down to "Labels" section
3. Find NO_AI
4. Make sure it's visible (not hidden)

---

## 📋 Pre-Made Filter Templates

Copy these directly into Gmail filters:

### Template 1: Family & Friends
```
From: (family@email.com OR friend@email.com OR spouse@email.com)
Do this: Apply label "NO_AI"
```

### Template 2: Personal Domains
```
From: (@personal-domain.com)
Do this: Apply label "NO_AI"
```

### Template 3: Sensitive Keywords
```
Subject: (PERSONAL OR PRIVATE OR CONFIDENTIAL OR SENSITIVE)
Do this: Apply label "NO_AI"
```

### Template 4: Banking & Financial
```
From: (@bank.com OR @creditcard.com OR @investment.com)
Do this: Apply label "NO_AI"
```

### Template 5: Medical & Health
```
From: (@hospital.com OR @doctor.com OR @healthinsurance.com)
Do this: Apply label "NO_AI"
```

### Template 6: Legal Communications
```
From: (@lawfirm.com OR lawyer@)
Do this: Apply label "NO_AI"
```

---

## ✅ Recommended Setup Checklist

For most users, set up these filters:

- [ ] **Personal emails** - Family and close friends
- [ ] **Banking** - Financial institutions
- [ ] **Legal** - Lawyers, legal firms
- [ ] **Medical** - Doctors, hospitals, insurance
- [ ] **HR/Payroll** - Workplace sensitive emails
- [ ] **Subject keywords** - PRIVATE, CONFIDENTIAL, PERSONAL

**Time to set up:** 10-15 minutes
**Benefit:** AI only processes business emails, personal stays private

---

## 🎯 Best Practices

1. **Start Conservative**
   - Begin with obvious exclusions (family, banking)
   - Add more filters over time as needed

2. **Test First**
   - Create one filter
   - Verify it works
   - Then add more

3. **Regular Review**
   - Monthly: Review NO_AI labeled emails
   - Remove filters if no longer needed
   - Add new ones as needed

4. **Document Your Filters**
   - Keep list of who/what you've excluded
   - Update when contacts change

5. **Monitor Initially**
   - First week: Check logs daily
   - Ensure filters working as expected
   - Adjust as needed

---

## 🔗 Quick Links

**View NO_AI emails:** Gmail → Search `label:NO_AI`
**Manage filters:** Gmail → Settings → Filters and Blocked Addresses
**Check logs:** `tail -f Vault/Logs/gmail_watcher_*.log`
**Code location:** `src/watchers/gmail_watcher.py:54`

---

## 💡 Pro Tips

1. **Color Code:** Use red color for NO_AI label (easy to spot)
2. **Nested Labels:** Create `NO_AI/Family`, `NO_AI/Banking` for organization
3. **Stars:** Star NO_AI emails that need your attention
4. **Archive:** Set filter to auto-archive + NO_AI for newsletters you keep
5. **Combine:** Use NO_AI + important for emails you want to see but not automate

---

**Last Updated:** 2026-01-17
**Gmail Watcher Version:** 2.0 with AI Exclusion
