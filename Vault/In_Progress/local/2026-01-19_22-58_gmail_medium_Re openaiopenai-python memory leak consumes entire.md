# 🟡 Email: Re: [openai/openai-python] memory leak, consumes entire system after just days of usage (Issue #1181)

## Metadata
- **Source:** Gmail
- **From:** Victorien <notifications@github.com>
- **Date:** Sun, 18 Jan 2026 07:04:40 -0800
- **Importance:** MEDIUM
- **Message ID:** 19bd1a305dd61b74
- **Created:** 2026-01-19T22:58:48.220565
- **Sender Reputation:** github.com

---

## Summary
Viicos left a comment (openai/openai-python#1181) I&#39;m not able to reproduce the leak. I do see a slight increase in memory usage over time, but it seems unrelated to pydantic: image.png (view on

---

## Full Content
Viicos left a comment (openai/openai-python#1181)

I'm not able to reproduce the leak. I do see a slight increase in memory usage over time, but it seems unrelated to pydantic:

<img width="1285" height="699" alt="Image" src="https://github.com/user-attachments/assets/b05b0bbe-65df-4a97-93df-4a6890f6fbbf" />

<img width="2553" height="689" alt="Image" src="https://github.com/user-attachments/assets/d0b3711e-a7f5-43b5-b401-7d5688ad26c2" />

If you can manage to provide a memray report, I could investigate further (`memray run -o openai.bin repro.py && memray flamegraph -o openai.html openai.bin`).

-- 
Reply to this email directly or view it on GitHub:
https://github.com/openai/openai-python/issues/1181#issuecomment-3765385784
You are receiving this because you are subscribed to this thread.

Message ID: <openai/openai-python/issues/1181/3765385784@github.com>

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

