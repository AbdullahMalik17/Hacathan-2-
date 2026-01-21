# 🟡 Email: [openai/openai-python] Can you document the streaming tool_call_id behavior (Issue #2827)

## Metadata
- **Source:** Gmail
- **From:** "🦦" <notifications@github.com>
- **Date:** Tue, 20 Jan 2026 14:09:18 -0800
- **Importance:** MEDIUM
- **Message ID:** 19bdd747ecc998cf
- **Created:** 2026-01-21T10:51:33.587083
- **Sender Reputation:** github.com

---

## Summary
s-banach created an issue (openai/openai-python#2827) Confirm this is a feature request for the Python library and not the underlying OpenAI API. This is a feature request for the Python library

---

## Full Content
s-banach created an issue (openai/openai-python#2827)

### Confirm this is a feature request for the Python library and not the underlying OpenAI API.

- [x] This is a feature request for the Python library

### Describe the feature or improvement you're requesting

According to [this discussion from 2023](https://community.openai.com/t/streaming-with-tools-only-first-chunk-has-the-id/561359), the first `ChoiceDeltaToolCall` for each tool call will contain the `tool_call_id`.

The `ParsedChatCompletion` class returned by `stream.get_final_completion()` does not include `tool_call_id` with tool calls, it just throws that information away for unclear reasons.

The actual thing I would like is for ParsedChatCompletion not to throw away the ids. But if you can't do that, can you confirm that I can get the ids myself in this way? Thx.

### Additional context

_No response_

-- 
Reply to this email directly or view it on GitHub:
https://github.com/openai/openai-python/issues/2827
You are receiving this because you are subscribed to this thread.

Message ID: <openai/openai-python/issues/2827@github.com>

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

