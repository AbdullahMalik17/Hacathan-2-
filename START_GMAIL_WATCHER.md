# How to Run Gmail Watcher

> **Quick Reference Guide**

---

## ⚡ QUICK START (Recommended)

### Method 1: Use the Main Launcher (Easiest)

This starts ALL services including Gmail watcher:

```powershell
# In PowerShell (as Administrator recommended)
.\Launch_Abdullah_Junior.ps1
```

This starts:
- 🧠 Orchestrator (task processor)
- 📬 **Gmail Watcher** (email monitoring)
- 📁 Filesystem Watcher
- 💬 WhatsApp Watcher
- 🖥️ Frontend Dashboard (optional)

**Status:** All services run in background windows

---

## 🎯 Method 2: Run ONLY Gmail Watcher

If you only want to run the Gmail watcher:

### Option A: Direct Python Command

```bash
# Navigate to project root
cd D:\Hacathan_2

# Run directly
python src/watchers/gmail_watcher.py
```

### Option B: Via Skill Wrapper

```bash
# Navigate to project root
cd D:\Hacathan_2

# Run via skill
python .claude/skills/watching-gmail/scripts/run.py
```

### Option C: Via Service Manager

```bash
# Start only Gmail watcher
python src/service_manager.py start watching-gmail

# Or start all watchers
python src/service_manager.py start
```

---

## 🔧 First-Time Setup (IMPORTANT!)

Since we added new features, you need to **re-authenticate** first:

### Step 1: Delete Old Token

```bash
# This forces re-authentication with new permissions
rm config/token.json
```

Or in PowerShell:
```powershell
Remove-Item config\token.json
```

### Step 2: Run Watcher (Will Prompt for Auth)

```bash
python src/watchers/gmail_watcher.py
```

**What happens:**
1. Browser opens automatically
2. Sign in to your Google account
3. Grant permissions (read, modify, send)
4. Browser shows "Authentication successful"
5. Watcher starts monitoring

**New Token Created:** `config/token.json` (with new permissions)

---

## 🎮 Control Commands

### Check if Running

```powershell
# PowerShell
Get-Process python | Where-Object {$_.CommandLine -like "*gmail*"}
```

```bash
# Bash
ps aux | grep gmail_watcher
```

### Stop Gmail Watcher

```powershell
# PowerShell - Stop all Python processes (careful!)
Stop-Process -Name python

# Or find specific process
Get-Process python | Where-Object {$_.CommandLine -like "*gmail*"} | Stop-Process
```

```bash
# Bash - Find and kill
pkill -f gmail_watcher

# Or specific PID
ps aux | grep gmail_watcher
kill <PID>
```

### Restart Gmail Watcher

```bash
# Stop
pkill -f gmail_watcher

# Start
python src/watchers/gmail_watcher.py &
```

---

## 📊 Monitoring

### View Real-Time Logs

```bash
# Watch log file
tail -f Vault/Logs/gmail_watcher_2026-01-17.log
```

```powershell
# PowerShell equivalent
Get-Content Vault\Logs\gmail_watcher_2026-01-17.log -Wait
```

### Check Activity

```bash
# View today's activity
cat Vault/Logs/2026-01-17.json | jq '.[] | select(.action == "email_processed")'
```

### Check Task Files Created

```bash
# List recent email tasks
ls -lt Vault/Needs_Action/*gmail* | head -10
```

---

## ⚙️ Configuration Options

### Enable Auto-Reply

Before running, set environment variable:

```bash
# Linux/Mac
export AUTO_REPLY_ENABLED=true
python src/watchers/gmail_watcher.py

# Or inline
AUTO_REPLY_ENABLED=true python src/watchers/gmail_watcher.py
```

```powershell
# PowerShell
$env:AUTO_REPLY_ENABLED="true"
python src/watchers/gmail_watcher.py
```

### Change Poll Interval

```bash
# Check every 30 seconds instead of 60
export GMAIL_POLL_INTERVAL=30
python src/watchers/gmail_watcher.py
```

### Dry Run (Test Mode)

```bash
# Test without creating files
DRY_RUN=true python src/watchers/gmail_watcher.py
```

---

## 🚨 Troubleshooting

### Problem: "Token has been expired or revoked"

**Solution:**
```bash
rm config/token.json
python src/watchers/gmail_watcher.py
# Re-authenticate in browser
```

### Problem: "credentials.json not found"

**Solution:**
1. Go to Google Cloud Console
2. Enable Gmail API
3. Download credentials.json
4. Place in `config/credentials.json`

### Problem: "No new messages found" (but you have unread emails)

**Possible causes:**
1. Emails have `NO_AI` label → Working as intended
2. Already processed → Check `config/processed_emails.json`
3. Not in inbox → Check Gmail filters

**Reset processed IDs:**
```bash
rm config/processed_emails.json
# Will reprocess all unread emails
```

### Problem: Watcher crashes/stops

**Check logs:**
```bash
tail -50 Vault/Logs/gmail_watcher_2026-01-17.log
```

**Common issues:**
- Network timeout → Automatic retry
- API quota exceeded → Wait 24 hours
- Invalid token → Re-authenticate

---

## 🔍 Verify It's Working

After starting, verify operation:

### 1. Check Process Running

```bash
ps aux | grep gmail_watcher
# Should show Python process
```

### 2. Check Logs

```bash
tail Vault/Logs/gmail_watcher_2026-01-17.log

# Should see:
# "Gmail Watcher Starting..."
# "Successfully authenticated with Gmail API"
# "Checking for new emails..."
```

### 3. Send Test Email

1. Send yourself an email with subject: `URGENT: Test Email`
2. Wait 60 seconds
3. Check: `ls Vault/Needs_Action/*gmail_important*`
4. Should see new task file created

### 4. Check Auto-Reply (if enabled)

1. Gmail → Drafts
2. Should see draft reply to test email

---

## 📝 Example: Complete Startup

```bash
# 1. Navigate to project
cd D:\Hacathan_2

# 2. Re-authenticate (first time only)
rm config/token.json

# 3. Start with auto-reply enabled
AUTO_REPLY_ENABLED=true python src/watchers/gmail_watcher.py

# Output should show:
# ==================================================
# Gmail Watcher Starting...
# Vault Path: D:\Hacathan_2\Vault
# Poll Interval: 60 seconds
# Dry Run: False
# ==================================================
# Refreshing expired credentials...  (if token deleted)
# <Browser opens for auth>
# Successfully authenticated with Gmail API
# Logging to file: Vault/Logs/gmail_watcher_2026-01-17.log
# Checking for new emails...
```

**Press Ctrl+C to stop**

---

## 🎯 Recommended Production Setup

### Run in Background

```bash
# Linux/Mac
nohup python src/watchers/gmail_watcher.py > /dev/null 2>&1 &

# Get PID
echo $! > gmail_watcher.pid
```

```powershell
# PowerShell - Background
Start-Process powershell -ArgumentList "-NoProfile -Command python src/watchers/gmail_watcher.py" -WindowStyle Hidden
```

### Or Use Service Manager

```bash
# Start all services
python src/service_manager.py start

# Check status
python src/service_manager.py status

# Stop all
python src/service_manager.py stop
```

---

## 🔗 Related Files

- **Main Script:** `src/watchers/gmail_watcher.py`
- **Skill Wrapper:** `.claude/skills/watching-gmail/scripts/run.py`
- **Service Manager:** `src/service_manager.py`
- **Main Launcher:** `Launch_Abdullah_Junior.ps1`
- **Logs:** `Vault/Logs/gmail_watcher_*.log`
- **Activity:** `Vault/Logs/YYYY-MM-DD.json`
- **Task Files:** `Vault/Needs_Action/`
- **Config:** `config/token.json`, `config/credentials.json`
- **Reputation:** `config/known_senders.json`
- **Processed:** `config/processed_emails.json`

---

## 💡 Pro Tips

1. **Always check logs first** when troubleshooting
2. **Use dry run** to test configuration changes
3. **Monitor for 24 hours** after enabling auto-reply
4. **Create NO_AI label** in Gmail before starting
5. **Configure important domains** in code before first run
6. **Start with auto-reply disabled**, enable after testing

---

## ✅ Quick Checklist

Before running for the first time:

- [ ] `config/credentials.json` exists
- [ ] Deleted `config/token.json` (for new permissions)
- [ ] Created `NO_AI` label in Gmail
- [ ] Configured important domains (optional)
- [ ] Set `AUTO_REPLY_ENABLED=false` (for testing)
- [ ] Ready to authenticate in browser

Then run:
```bash
python src/watchers/gmail_watcher.py
```

Done! 🎉
