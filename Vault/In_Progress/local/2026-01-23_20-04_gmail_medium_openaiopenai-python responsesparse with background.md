# 🟡 Email: [openai/openai-python] responses.parse() with background=True returns unparseable Response from retrieve() - missing ParsedResponse support for background mode (Issue #2830)

## Metadata
- **Source:** Gmail
- **From:** Adnan Boz <notifications@github.com>
- **Date:** Fri, 23 Jan 2026 06:15:33 -0800
- **Importance:** MEDIUM
- **Message ID:** 19beb35dba7c5df6
- **Created:** 2026-01-23T20:04:03.749078
- **Sender Reputation:** github.com

---

## Summary
adnanboz created an issue (openai/openai-python#2830) Confirm this is an issue with the Python library and not an underlying OpenAI API This is an issue with the Python library Describe the bug When

---

## Full Content
adnanboz created an issue (openai/openai-python#2830)

### Confirm this is an issue with the Python library and not an underlying OpenAI API

- [x] This is an issue with the Python library

### Describe the bug

When using responses.parse() with background=True and a text_format (structured output), the initial call returns a ParsedResponse wrapper. However, when polling for completion using responses.retrieve(), a plain Response object is returned instead of ParsedResponse.

This means output_parsed is not available on the retrieved response, and users must manually parse output_text using their schema's model_validate_json().

The SDK accepts background=True in parse() without warning, but doesn't provide a way to complete the workflow with proper parsing.

Expected behavior:
Either:
- retrieve() should accept a text_format parameter to return ParsedResponse
A new retrieve_parsed() method should exist
- Or parse() should raise an error/warning when background=True is used

### To Reproduce

from openai import AsyncOpenAI
from pydantic import BaseModel

class MySchema(BaseModel):
    name: str
    value: int

client = AsyncOpenAI()

# Start background request with structured output
response = await client.responses.parse(
    model="gpt-4.1",
    input="Generate a name and value",
    text_format=MySchema,
    background=True
)

# Poll for completion
while response.status in ("in_progress", "queued"):
    await asyncio.sleep(0.5)
    response = await client.responses.retrieve(response.id)

# This fails - Response has no output_parsed attribute
print(response.output_parsed)  # AttributeError: 'Response' object has no attribute 'output_parsed'

# Workaround required:
result = MySchema.model_validate_json(response.output_text)

### Code snippets

```Python

```

### OS

macOS

### Python version

Python v3.12

### Library version

openai v2.15.0

-- 
Reply to this email directly or view it on GitHub:

... [truncated]

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

