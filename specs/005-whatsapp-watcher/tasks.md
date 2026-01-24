# Implementation Tasks: Sprint 3

## WhatsApp Watcher (005)

- [ ] **Contact Management**:
  - Create `src/utils/contacts.py` to handle loading/matching known contacts.
  - Integrate into `whatsapp_watcher.py`.
- [ ] **Auto-Reply Mechanism**:
  - Add `_send_reply(chat_name, text)` to `WhatsAppWatcher` class.
  - Logic: Click chat -> type -> press Enter.
- [ ] **Escalation Logic**:
  - Update `determine_priority` to consider contact status.
  - Update `create_task_file` template to highlight escalations.
- [ ] **Rate Limiting**:
  - Add check to prevent too many replies in short period.
- [ ] **Validation**: Verify logic with unit tests.
