# 🟡 Email: [openai/openai-python] AzureOpenAI models does not support files (Issue #2826)

## Metadata
- **Source:** Gmail
- **From:** Javier <notifications@github.com>
- **Date:** Mon, 19 Jan 2026 03:25:02 -0800
- **Importance:** MEDIUM
- **Message ID:** 19bd6004ce98e47d
- **Created:** 2026-01-19T22:58:48.108067
- **Sender Reputation:** github.com

---

## Summary
jsancs created an issue (openai/openai-python#2826) Confirm this is an issue with the Python library and not an underlying OpenAI API This is an issue with the Python library Describe the bug Using

---

## Full Content
jsancs created an issue (openai/openai-python#2826)

### Confirm this is an issue with the Python library and not an underlying OpenAI API

- [x] This is an issue with the Python library

### Describe the bug

Using OpenAI models with Azure does not allow files to be processed. However, the same implementation with the same model directly to OpenAI does work.
According to the official Azure documentation, these models do support file input as bytes:
https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses?view=foundry-classic&tabs=rest-api#convert-pdf-to-base64-and-analyze

### To Reproduce

Agents with OpenAI model can process files as bytes:
```
agent = Agent(model="openai:gpt-5-mini")
await agent.run(
    [
        SYSTEM_PROMPT,
        BinaryContent(data=doc_bytes, media_type='application/pdf'),
    ]
)
```
This works correctly.


However, the same code and model with an Azure OpenAI model generates an error:
```
agent = Agent(model="azure:gpt-5-mini")
await agent.run(
    [
        SYSTEM_PROMPT,
        BinaryContent(data=doc_bytes, media_type='application/pdf'),
    ]
)
```
Error:
```
pydantic_ai.exceptions.ModelHTTPError: status_code: 400, model_name: gpt-5-mini, body: {'message': "Invalid Value: 'file'. This model does not support file content types.", 'type': 'invalid_request_error', 'param': 'messages[0].content[1].type', 'code': 'invalid_value'}
```

### Code snippets

```Python

```

### OS

Windows

### Python version

3.11.13

### Library version

1.44.0

-- 
Reply to this email directly or view it on GitHub:
https://github.com/openai/openai-python/issues/2826
You are receiving this because you are subscribed to this thread.

Message ID: <openai/openai-python/issues/2826@github.com>

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

