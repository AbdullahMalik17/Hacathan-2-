# 🟡 Email: Re: [openai/openai-python] Slow import times (due to openai.types) (Issue #2819)

## Metadata
- **Source:** Gmail
- **From:** Shay Nehmad <notifications@github.com>
- **Date:** Thu, 15 Jan 2026 11:31:09 -0800
- **Importance:** MEDIUM
- **Message ID:** 19bc323eac800c0d
- **Created:** 2026-01-17T20:23:55.587856
- **Sender Reputation:** github.com

---

## Summary
TheCoreMan left a comment (openai/openai-python#2819) Seeing similar things here. We use pyleak to detect event loop blocking in our app and our CI started failing recently, with the stacktrace

---

## Full Content
TheCoreMan left a comment (openai/openai-python#2819)

Seeing similar things here. We use pyleak to detect event loop blocking in our app and our CI started failing recently, with the stacktrace pointing towards importlib when trying to import openai.

-- 
Reply to this email directly or view it on GitHub:
https://github.com/openai/openai-python/issues/2819#issuecomment-3756521974
You are receiving this because you are subscribed to this thread.

Message ID: <openai/openai-python/issues/2819/3756521974@github.com>

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

