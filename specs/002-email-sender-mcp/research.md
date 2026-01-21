# Research Findings: Email Sender MCP

## 1. Existing Implementation Analysis

### Codebase (`src/mcp_servers/email_sender.py`)
- **Status**: Mostly Implemented.
- **Framework**: `FastMCP`.
- **Capabilities**:
  - `send_email`: Sends via Gmail API or queues for approval.
  - `send_from_template`: Uses Jinja2.
  - `check_rate_limits`: Enforces hourly/daily limits.
  - `log_audit`: Writes to Markdown log.

### Architecture Alignment
- Fits the "Hands" component of the Digital FTE architecture.
- Uses `Vault/Pending_Approval` for HITL (Human-in-the-Loop), consistent with spec.

## 2. Technical Decisions

### Template Engine
- **Choice**: Jinja2.
- **Rationale**: Standard Python templating, flexible, supports logic (if/else).
- **Subject Handling**: Subject is expected to be passed in `variables` dict for `send_from_template`.

### Audit Logging
- **Choice**: Local Markdown file (`email_audit_log.md`).
- **Rationale**: Simple, human-readable, integrates with Obsidian dashboard.

## 3. Gaps & Requirements

- **Recipient Limit**: Spec FR-003 requires "5 recipients max". Current code does not enforce this on CC/BCC lists.
- **Subject in Template**: `send_from_template` relies on the user providing `subject` in the variables. It might be better to allow the template to define the subject (e.g. via a block) or strictly require it in the function signature.
- **Testing**: No dedicated tests found.
