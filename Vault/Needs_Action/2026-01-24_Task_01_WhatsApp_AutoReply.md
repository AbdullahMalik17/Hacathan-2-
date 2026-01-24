# Task: WhatsApp Auto-Reply System

**Priority:** High
**Domain:** Communication / Automation
**Assigned To:** Gemini Agent
**Created:** 2026-01-24
**Order:** 1 of 4

---

## Objective

Create an intelligent WhatsApp auto-reply system that:
1. Detects when user is busy/DND mode
2. Auto-replies to incoming messages with contextual responses
3. Queues important messages for later review
4. Learns which contacts need immediate vs delayed responses

---

## Requirements

### 1. Enhance WhatsApp Watcher

Update `src/watchers/whatsapp_watcher.py` to add auto-reply capability:

```python
class WhatsAppAutoReply:
    """Auto-reply to WhatsApp messages when user is busy."""

    DEFAULT_REPLIES = {
        "busy": "Hey! I'm currently busy. I'll get back to you soon. 🙏",
        "meeting": "I'm in a meeting right now. Will respond when I'm free.",
        "focus": "Deep work mode 🎯 - I'll check messages in about an hour.",
        "sleep": "It's late here. I'll reply tomorrow morning!",
        "custom": None  # User-defined message
    }

    def __init__(self):
        self.enabled = False
        self.mode = "busy"
        self.custom_message = None
        self.whitelist = []  # Contacts that bypass auto-reply
        self.replied_chats = set()  # Avoid spamming same chat

    def enable(self, mode: str = "busy", custom_message: str = None):
        """Enable auto-reply with specified mode."""
        self.enabled = True
        self.mode = mode
        self.custom_message = custom_message
        self.replied_chats.clear()

    def disable(self):
        """Disable auto-reply."""
        self.enabled = False
        self.replied_chats.clear()

    def should_reply(self, chat_name: str, sender: str) -> bool:
        """Check if we should auto-reply to this chat."""
        if not self.enabled:
            return False
        if sender in self.whitelist:
            return False
        if chat_name in self.replied_chats:
            return False  # Already replied once
        return True

    def get_reply_message(self) -> str:
        """Get the appropriate reply message."""
        if self.custom_message:
            return self.custom_message
        return self.DEFAULT_REPLIES.get(self.mode, self.DEFAULT_REPLIES["busy"])

    def mark_replied(self, chat_name: str):
        """Mark chat as replied to avoid spam."""
        self.replied_chats.add(chat_name)
```

### 2. Integration with Playwright

Add auto-reply execution to the WhatsApp watcher:

```python
async def send_auto_reply(self, page, chat_name: str):
    """Send auto-reply to a chat."""
    if not self.auto_reply.should_reply(chat_name, sender=""):
        return

    message = self.auto_reply.get_reply_message()

    # Click on the chat
    # Find message input
    # Type and send message

    # Use existing Playwright selectors
    message_input = page.locator('div[contenteditable="true"][data-tab="10"]')
    await message_input.fill(message)
    await page.keyboard.press("Enter")

    self.auto_reply.mark_replied(chat_name)
    log_audit("WHATSAPP_AUTO_REPLY", {"chat": chat_name, "mode": self.auto_reply.mode})
```

### 3. API Endpoints

Add to `src/api_server.py`:

```python
@app.post("/api/whatsapp/autoreply/enable")
async def enable_autoreply(mode: str = "busy", message: str = None):
    """Enable WhatsApp auto-reply."""
    whatsapp_watcher.auto_reply.enable(mode, message)
    return {"status": "enabled", "mode": mode}

@app.post("/api/whatsapp/autoreply/disable")
async def disable_autoreply():
    """Disable WhatsApp auto-reply."""
    whatsapp_watcher.auto_reply.disable()
    return {"status": "disabled"}

@app.get("/api/whatsapp/autoreply/status")
async def autoreply_status():
    """Get auto-reply status."""
    ar = whatsapp_watcher.auto_reply
    return {
        "enabled": ar.enabled,
        "mode": ar.mode,
        "replied_count": len(ar.replied_chats)
    }

@app.post("/api/whatsapp/autoreply/whitelist")
async def add_to_whitelist(contact: str):
    """Add contact to whitelist (bypasses auto-reply)."""
    whatsapp_watcher.auto_reply.whitelist.append(contact)
    return {"status": "added", "contact": contact}
```

### 4. Push Notification Integration

When auto-reply is sent, notify user on phone:

```python
# In whatsapp_watcher.py
async def on_auto_reply_sent(self, chat_name: str, message: str):
    """Notify user when auto-reply is sent."""
    await push_service.send_notification(NotificationPayload(
        title="📱 Auto-replied to WhatsApp",
        body=f"Sent to: {chat_name}",
        tag="whatsapp-autoreply",
        data={"chat": chat_name, "type": "auto_reply"}
    ))
```

### 5. Smart Mode Selection

Auto-select mode based on context:

```python
def get_smart_mode(self) -> str:
    """Automatically determine best auto-reply mode."""
    hour = datetime.now().hour

    # Late night
    if hour >= 23 or hour < 7:
        return "sleep"

    # Check calendar for meetings (if integrated)
    # if calendar.has_current_meeting():
    #     return "meeting"

    # Default to busy during work hours
    if 9 <= hour <= 18:
        return "focus"

    return "busy"
```

---

## Files to Modify/Create

1. `src/watchers/whatsapp_watcher.py` - Add AutoReply class
2. `src/api_server.py` - Add auto-reply endpoints
3. `config/whatsapp_autoreply.json` - Store whitelist and settings

---

## Acceptance Criteria

- [ ] Auto-reply can be enabled/disabled via API
- [ ] Supports multiple modes (busy, meeting, focus, sleep, custom)
- [ ] Only replies once per chat to avoid spam
- [ ] Whitelist contacts bypass auto-reply
- [ ] Push notification sent when auto-reply triggers
- [ ] Status visible in dashboard

---

## Testing

```bash
# Enable auto-reply
curl -X POST "http://localhost:8000/api/whatsapp/autoreply/enable?mode=busy"

# Check status
curl http://localhost:8000/api/whatsapp/autoreply/status

# Disable
curl -X POST http://localhost:8000/api/whatsapp/autoreply/disable
```
