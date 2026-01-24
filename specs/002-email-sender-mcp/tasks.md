# Implementation Tasks: Email Sender MCP

## US1: Send Email & Safety

- [ ] **Enhance Validation**: Update `send_email` in `src/mcp_servers/email_sender.py`.
  - Add check: `total_recipients = 1 + len(cc or []) + len(bcc or [])`.
  - If `total_recipients > 5`, return Error.
- [ ] **Unit Test**: Create `tests/test_email_logic.py`.
  - Test `check_rate_limits` with mocked file I/O.
  - Test validation logic.

## US2: Templates

- [ ] **Enhance Template Tool**: Update `send_from_template`.
  - Check if `subject` is in `variables`. If not, raise strict error: "Subject required in variables".
- [ ] **Verify Template**: Create a sample template `src/templates/email/test.j2` and test rendering.

## US3: Approval Workflow

- [ ] **Verify File Creation**: Ensure `Pending_Approval` files have the correct YAML frontmatter (as per Spec).
- [ ] **Manual Test**: Call `send_email(..., requires_approval=True)` and check the generated file in `Vault/Pending_Approval`.
