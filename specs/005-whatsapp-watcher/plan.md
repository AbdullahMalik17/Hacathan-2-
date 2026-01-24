# Implementation Plan: Sprint 3

## 1. WhatsApp Watcher Enhancements

- **Contact Logic**: 
  - Load `config/known_contacts.json`.
  - In `get_unread_chats`, match `chat_name` against the list.
  - Add `is_known` flag to `message_data`.

- **Auto-Reply (P2)**:
  - Add `reply_to_chat(chat_name, message)` method using Playwright.
  - Check if `auto_reply` is enabled for contact.
  - Implement 24h cooldown per contact.

- **Improved Task Templates**:
  - Add "ESCALATION" status to Markdown if unknown + high priority.

## 2. Configuration

- Create `config/known_contacts.json.example`.
- Add `WHATSAPP_AUTO_REPLY` environment variable.

## 3. Validation

- Manual testing (requires real WhatsApp session).
- Mock testing for message processing logic.
