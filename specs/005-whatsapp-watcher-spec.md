# Feature Specification: WhatsApp Watcher

**Feature Branch**: `005-whatsapp-watcher`  
**Created**: 2026-01-15  
**Status**: Draft  
**Input**: User selection from Digital FTE roadmap - Monitor WhatsApp messages

## User Scenarios & Testing

### User Story 1 - Detect New WhatsApp Messages (Priority: P1)

System monitors WhatsApp Web and detects unread messages from direct message inbox.

**Why this priority**: Core functionality - enables WhatsApp automation workflows.

**Independent Test**: Send WhatsApp message and verify task appears in Needs_Action within 30 seconds.

**Acceptance Scenarios**:

1. **Given** WhatsApp watcher is running, **When** unread message arrives in DM inbox, **Then** task created in Needs_Action
2. **Given** task is created, **When** examined, **Then** it contains sender, timestamp, message content, contact info
3. **Given** multiple messages arrive, **When** tasks created, **Then** each message generates exactly one task

---

### User Story 2 - Identify Known vs Unknown Contacts (Priority: P1)

Watcher analyzes sender to determine if known contact, extracts previous interaction history.

**Why this priority**: High - enables smarter approval/auto-reply decisions based on trust level.

**Independent Test**: Send message from known and unknown contact, verify contact status is correctly identified.

**Acceptance Scenarios**:

1. **Given** message from contact in address book, **When** task created, **Then** is_known_contact = true
2. **Given** known contact with 5+ previous interactions, **When** task created, **Then** previous_interactions = 5
3. **Given** unknown contact, **When** task created, **Then** is_known_contact = false and requires approval

---

### User Story 3 - Auto-Reply to Known Contacts (Priority: P2)

For low-risk greetings/status messages from known contacts, system auto-replies per handbook rules.

**Why this priority**: High - enables automation of routine messages without approval.

**Independent Test**: Send greeting message from known contact, verify auto-reply sent within 5 seconds.

**Acceptance Scenarios**:

1. **Given** greeting message from known contact, **When** handbook says auto-approve, **Then** auto-reply sent
2. **Given** auto-reply sent, **When** message delivered, **Then** task marked as completed
3. **Given** status update request from known contact, **When** FTE has response, **Then** auto-reply sent with status

---

### User Story 4 - Escalate Sensitive Messages (Priority: P2)

Messages requiring approval (unknown senders, sensitive content, requests) go to Pending_Approval for human review.

**Why this priority**: Critical for safety - prevents FTE from making inappropriate commitments on WhatsApp.

**Independent Test**: Send sensitive message, verify it goes to Pending_Approval, never auto-replied.

**Acceptance Scenarios**:

1. **Given** message from unknown contact requesting personal information, **When** task created, **Then** goes to Pending_Approval
2. **Given** message contains payment request, **When** task analyzed, **Then** escalated to Pending_Approval
3. **Given** human reviews and approves, **When** moved to Approved folder, **Then** system sends reply

---

### Edge Cases

- What happens with group messages (not handled initially)?
- How to handle media/images in messages?
- What if WhatsApp session expires?
- How to detect and prevent double-replies?
- What happens if contact changes their number?
- How to handle message encoding (emoji, special chars)?

## Requirements

### Functional Requirements

- **FR-001**: System MUST monitor WhatsApp Web DM inbox for unread messages
- **FR-002**: System MUST extract sender, timestamp, content from messages
- **FR-003**: System MUST identify known vs unknown contacts
- **FR-004**: System MUST create markdown task in Needs_Action
- **FR-005**: System MUST auto-reply to known contacts per handbook rules
- **FR-006**: System MUST escalate sensitive messages to Pending_Approval
- **FR-007**: System MUST enforce rate limits (max 20 messages/hour, 5 replies/hour)
- **FR-008**: System MUST log all messages and actions with sender and content
- **FR-009**: System MUST handle emoji and special character encoding correctly
- **FR-010**: System MUST gracefully handle WhatsApp Web session expiration

### Key Entities

- **WhatsAppMessage**: Incoming message from contact
  - sender, sender_id, timestamp, content, is_known_contact, previous_interactions, priority_level
  
- **WhatsAppTask**: Markdown task for message processing
  - sender, message_content, timestamp, is_known_contact, requires_approval, status, suggested_action

- **WhatsAppContact**: Contact information and history
  - name, phone_number, is_known, interaction_count, last_interaction, auto_reply_enabled

## Success Criteria

### Measurable Outcomes

- **SC-001**: <30 second detection latency - task created within 30 seconds of message arrival
- **SC-002**: 100% accurate contact classification - known vs unknown
- **SC-003**: Zero missed messages - all messages detected and tasked
- **SC-004**: Safe auto-replies - 0 inappropriate replies sent
- **SC-005**: <5% false escalations - only genuinely sensitive messages escalated
- **SC-006**: 99% uptime for WhatsApp monitoring
