# 🟡 Email: Re: [openai/openai-python] Cancel for streaming Responses (Issue #2643)

## Metadata
- **Source:** Gmail
- **From:** dprkh <notifications@github.com>
- **Date:** Sun, 18 Jan 2026 18:23:25 -0800
- **Importance:** MEDIUM
- **Message ID:** 19bd41071f628ccf
- **Created:** 2026-01-19T22:58:48.163496
- **Sender Reputation:** github.com

---

## Summary
dprkh left a comment (openai/openai-python#2643) It seems that cancelling a response that is both &quot;background&quot;: true and &quot;stream&quot;: true doesn&#39;t do anything. There is no

---

## Full Content
dprkh left a comment (openai/openai-python#2643)

It seems that cancelling a response that is both `"background": true` and `"stream": true` doesn't do anything. There is no streaming event for cancellation, so I expected that either `error` or `response.failed` would be sent, but no, nothing happened. During my tests, I sent a `/cancel` request, and, despite the API returning `"status": "cancelled"` in response to the cancellation request, steaming events continued to arrive, and, eventually, the response completed (`"status": "completed"`). Also, the API returned `"usage": null` in response to the cancellation request, but after the response completed, `"usage"` was not null, meaning that I *was* charged, despite cancelling the response.

-- 
Reply to this email directly or view it on GitHub:
https://github.com/openai/openai-python/issues/2643#issuecomment-3766114665
You are receiving this because you are subscribed to this thread.

Message ID: <openai/openai-python/issues/2643/3766114665@github.com>

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

