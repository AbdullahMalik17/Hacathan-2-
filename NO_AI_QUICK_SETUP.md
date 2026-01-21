# NO_AI Label - Quick Setup Guide

> **5-Minute Setup** - Exclude personal emails from AI processing

---

## ✅ You Already Have: NO_AI label created in Gmail

---

## 🚀 Quick Setup (Choose Your Method)

### Method A: Manual (Good for Testing)

**Right now, for any email:**
1. Open Gmail
2. Select an email
3. Click label icon (tag) in toolbar
4. Check "NO_AI"
5. Done!

**That email won't be processed by AI**

---

### Method B: Automatic Filters (Recommended)

**Set it once, works forever**

---

## 📝 Common Filter Setups

### 1. Exclude Family & Friends (Most Common)

**Steps:**
1. Gmail → Settings (gear icon) → "See all settings"
2. "Filters and Blocked Addresses" tab
3. "Create a new filter"
4. In "From" field, enter:
   ```
   mom@gmail.com OR dad@email.com OR friend@yahoo.com
   ```
   (Replace with actual emails, separate with OR)
5. Click "Create filter"
6. ✓ Check "Apply the label:" → Select "NO_AI"
7. ✓ Check "Also apply filter to matching conversations" (optional)
8. Click "Create filter"

**Done!** All emails from these people are now excluded.

---

### 2. Exclude Personal Domain

**If you have a personal email domain:**

**From field:**
```
@your-personal-domain.com
```

**Example:**
```
@familyname.com
```

---

### 3. Exclude by Subject Keywords

**For emails marked as private:**

**Subject field:**
```
PRIVATE OR CONFIDENTIAL OR PERSONAL
```

**Any email with these words in subject → excluded**

---

### 4. Exclude Banking/Financial

**From field:**
```
@yourbank.com OR @creditcard.com OR @investment.com
```

**Replace with your actual banks**

---

### 5. Exclude Medical/Legal

**From field:**
```
@hospital.com OR @lawyer.com OR @insurance.com
```

---

## 🎯 Recommended First Setup

**Start with these 3 filters:**

**Filter 1: Personal Contacts**
```
From: [your family and close friends emails with OR between them]
Label: NO_AI
```

**Filter 2: Sensitive Institutions**
```
From: [your bank, lawyer, doctor with OR between them]
Label: NO_AI
```

**Filter 3: Private Keywords**
```
Subject: PRIVATE OR PERSONAL OR CONFIDENTIAL
Label: NO_AI
```

**Time:** 5 minutes
**Benefit:** AI won't touch personal/sensitive emails

---

## 🧪 Test It Works

### Quick Test:

1. **Send yourself an email** with subject: "PRIVATE Test Email"
2. **Wait 1 minute**
3. **Check Gmail** - email should have NO_AI label
4. **Check logs:**
   ```bash
   tail Vault/Logs/gmail_watcher_2026-01-17.log
   ```
5. **Look for:** "Skipping email - has NO_AI label"
6. **Verify:** No task file in `Vault/Needs_Action/`

**Success!** 🎉 NO_AI is working

---

## 📋 Your Custom Setup

**Fill in your details:**

**Personal Contacts to Exclude:**
- [ ] _________________ (name/email)
- [ ] _________________ (name/email)
- [ ] _________________ (name/email)

**Sensitive Senders:**
- [ ] Bank: _________________
- [ ] Lawyer: _________________
- [ ] Doctor: _________________
- [ ] Other: _________________

**Create these filters in Gmail now** (5 min)

---

## 🔍 View Excluded Emails

**In Gmail, search:**
```
label:NO_AI
```

**Shows all emails that AI is skipping**

---

## 💡 Pro Tips

1. **Start Small:** Add 2-3 filters first, test, then add more
2. **Use OR:** Combine multiple emails in one filter
3. **Test:** Send yourself test emails to verify
4. **Color:** Make NO_AI label red (easy to spot)
5. **Review:** Check `label:NO_AI` weekly to ensure working

---

## ⚙️ Current Configuration

**Label Name:** NO_AI
**Case Sensitive:** Yes (must be exactly "NO_AI")
**Effect:** Complete exclusion from AI
**What's Excluded:**
- ✗ No task file created
- ✗ No auto-reply
- ✗ No importance classification
- ✗ No sender reputation tracking

**What Still Happens:**
- ✓ Email stays in your Gmail inbox
- ✓ You can read it normally
- ✓ AI just ignores it

---

## 🆘 Troubleshooting

**Q: Email still being processed?**
- Check label is exactly "NO_AI" (case matters)
- Check label is applied to email
- Wait 60 seconds for next poll
- Check logs for "Skipping email" message

**Q: Filter not working?**
- Verify filter in Gmail Settings → Filters
- Test by sending yourself matching email
- Check "Apply label: NO_AI" is selected

**Q: Want to change label name?**
- Edit `src/watchers/gmail_watcher.py` line 54
- Change `AI_EXCLUSION_LABEL = "NO_AI"` to your preferred name
- Restart watcher

---

## 📚 Full Documentation

**Detailed guide:** `docs/NO_AI_LABEL_SETUP.md`
**Gmail watcher guide:** `docs/GMAIL_WATCHER_GUIDE.md`

---

**Setup Time:** 5-10 minutes
**Maintenance:** None (filters run automatically)
**Privacy:** 100% (local processing only)

You're all set! 🎉
