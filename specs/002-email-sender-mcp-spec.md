# Feature Specification: Email Sender MCP

**Feature Branch**: `002-email-sender-mcp`  
**Created**: 2026-01-15  
**Status**: Draft  
**Input**: User selection from Digital FTE roadmap - MCP server for sending emails

## User Scenarios & Testing

### User Story 1 - Send Email via MCP Tool (Priority: P1)

Claude reasoning engine invokes MCP tool to send emails with subject and body to specified recipients.

**Why this priority**: Critical - enables closed-loop automation where FTE can respond to emails.

**Independent Test**: Invoke MCP send_email tool with valid recipient and verify email arrives.

**Acceptance Scenarios**:

1. **Given** orchestrator has an email task to send, **When** it invokes send_email MCP tool, **Then** email is sent to recipient
2. **Given** email is sent, **When** rate limit allows, **Then** sender receives confirmation with message_id
3. **Given** multiple emails needed, **When** rate limit is respected, **Then** all emails sent without exceeding hourly quota

---

### User Story 2 - Send Email from Template (Priority: P2)

Claude can specify template_id and variables, MCP server substitutes variables and sends resulting email.

**Why this priority**: High - enables personalized emails without manual drafting each time.

**Independent Test**: Invoke send_from_template with template_id and variables, verify email content is correct.

**Acceptance Scenarios**:

1. **Given** template exists with variables, **When** send_from_template invoked with values, **Then** variables are substituted
2. **Given** substitution is complete, **When** email is sent, **Then** recipient receives correctly formatted email
3. **Given** invalid template_id provided, **When** MCP is invoked, **Then** error returned with helpful message

---

### User Story 3 - Require Approval Before Sending (Priority: P1)

Emails requiring human approval are moved to Pending_Approval folder. Human reviews and moves to Approved before sending.

**Why this priority**: Critical for safety - prevents accidental mass emails or sensitive messages.

**Independent Test**: Create approval-required email, verify it lands in Pending_Approval, then move to Approved and verify it sends.

**Acceptance Scenarios**:

1. **Given** email requires approval per handbook, **When** MCP is invoked, **Then** email moved to Pending_Approval instead of sending
2. **Given** human reviews email in Pending_Approval, **When** moved to Approved folder, **Then** system sends it
3. **Given** email in Approved folder, **When** approval_email tool invoked, **Then** email sent with audit log entry

---

### Edge Cases

- What happens if recipient email is invalid?
- How to handle rate limit exceeded?
- What if template has required variables missing?
- How to handle Gmail API quota exceeded?
- What if email is very large (attachment)?

## Requirements

### Functional Requirements

- **FR-001**: MCP MUST expose send_email(to, subject, body, cc, bcc) tool
- **FR-002**: MCP MUST expose send_from_template(template_id, to, variables) tool
- **FR-003**: MCP MUST enforce rate limits (10/hour, 100/day, 5 recipients max)
- **FR-004**: MCP MUST implement approval workflow for sensitive emails
- **FR-005**: MCP MUST return message_id and timestamp on successful send
- **FR-006**: MCP MUST return descriptive errors for failures
- **FR-007**: MCP MUST log all send attempts with outcome and recipient

### Key Entities

- **EmailTask**: Represents email to be sent
  - to, cc, bcc, subject, body, template_id, variables, requires_approval, status
  
- **EmailTemplate**: Reusable email template with Jinja2 substitution
  - id, subject_template, body_template, variables_required, auto_approve_rules

- **EmailAuditLog**: Records all send attempts
  - timestamp, recipient, subject, outcome (success/failed/pending_approval), message_id, error_message

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% delivery - all emails successfully sent or properly escalated for approval
- **SC-002**: <5 second send latency - email delivered within 5 seconds of MCP invocation
- **SC-003**: Zero unintended sends - all safety mechanisms working
- **SC-004**: Complete audit trail - every send attempt logged
- **SC-005**: Template reusability - 5+ email templates created and working
