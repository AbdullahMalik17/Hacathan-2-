# Data Model: Email Sender MCP

## Entities

### EmailAuditLog
*File: `Vault/Logs/email_audit_log.md`*

| Field | Description |
|-------|-------------|
| `Timestamp` | ISO 8601 or `YYYY-MM-DD HH:MM:SS` |
| `Recipient` | Primary recipient email |
| `Subject` | Email subject |
| `Outcome` | `SUCCESS`, `FAILED`, `PENDING_APPROVAL` |
| `Message ID` | Gmail Message ID or `pending:{filename}` |
| `Error` | Error details if failed |

### ApprovalRequest
*File: `Vault/Pending_Approval/email_{timestamp}.md`*

```yaml
---
type: email_approval
status: pending
created: 2026-01-21T10:00:00
to: client@example.com
subject: Invoice
---
```
**Body**: Full email body content (Markdown/Text).

### EmailTemplate
*File: `src/templates/email/{name}.j2`*

- **Format**: Jinja2 text file.
- **Variables**: `{{ variable_name }}` placeholders.
