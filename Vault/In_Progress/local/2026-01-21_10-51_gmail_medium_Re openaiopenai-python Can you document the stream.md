# 🟡 Email: Re: [openai/openai-python] Can you document the streaming tool_call_id behavior (Issue #2827)

## Metadata
- **Source:** Gmail
- **From:** "🦦" <notifications@github.com>
- **Date:** Tue, 20 Jan 2026 14:16:25 -0800
- **Importance:** MEDIUM
- **Message ID:** 19bdd7b073362b68
- **Created:** 2026-01-21T10:51:33.577531
- **Sender Reputation:** github.com

---

## Summary
s-banach left a comment (openai/openai-python#2827) Edit: I guess you can do event.snapshot.choices[0].message.tool_calls when event.type == &quot;chunk&quot; . — Reply to this email directly, view it

---

## Full Content
s-banach left a comment (openai/openai-python#2827)

Edit: I guess you can do `event.snapshot.choices[0].message.tool_calls` when `event.type == "chunk"`.

-- 
Reply to this email directly or view it on GitHub:
https://github.com/openai/openai-python/issues/2827#issuecomment-3775205480
You are receiving this because you are subscribed to this thread.

Message ID: <openai/openai-python/issues/2827/3775205480@github.com>

---

## Suggested Actions
- [ ] Read and understand the email
- [ ] Determine if response is needed
- [ ] Draft response (if applicable)
- [ ] Archive or follow up

---

## Decision Required
- [ ] **No action needed** - Archive this email
- [ ] **Reply needed** - Draft response for approval
- [ ] **Forward to human** - Requires human attention
- [ ] **Schedule follow-up** - Set reminder for later

---

## Notes
_Add any notes or context here_

