# Research Findings: Sprint 3 (WhatsApp Watcher)

## 1. Existing Implementation (`src/watchers/whatsapp_watcher.py`)

### Capabilities
- Uses `playwright` for WhatsApp Web automation.
- Supports persistent browser context (stores login).
- Detects unread messages.
- Categorizes priority based on keywords.
- Creates Markdown tasks in `Vault/Needs_Action`.

### Gaps
- **Contact Classification**: Missing logic to distinguish between known/unknown contacts.
- **Auto-Reply**: Missing capability to respond directly.
- **Escalation**: Logic for sensitive message detection is basic keyword-based.
- **Robustness**: WhatsApp Web selectors are notoriously brittle and change frequently.

## 2. Technical Decisions

### Contact Management
- **Choice**: `config/known_contacts.json`.
- **Structure**: `{"Name/Phone": {"priority": "high", "auto_reply": true}}`.
- **Reasoning**: Local, simple, easy for user to edit in Obsidian or directly.

### Auto-Reply Logic
- Should be restricted to `known_contacts` with `auto_reply: true`.
- Should have a cooldown (e.g. once per day per contact) to avoid loops.
- Message: "Hi, I've received your message and notified [User]. I'll get back to you soon if urgent."

### Escalation
- If contact is unknown AND priority is "high/urgent", flag as "ESCALATION".
