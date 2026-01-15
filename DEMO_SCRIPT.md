# Demo Video Script - Digital FTE

**Total Duration: 5-10 minutes**

---

## Pre-Recording Checklist

- [ ] Close unnecessary applications
- [ ] Open VS Code with project folder
- [ ] Open terminal in project directory
- [ ] Have Obsidian ready (optional)
- [ ] Ensure some unread emails exist for demo
- [ ] Clear `Vault/Needs_Action/` folder for fresh demo

### Reset for Demo (Optional)
```bash
# Move files back to Needs_Action for demo
mv Vault/Done/*.md Vault/Needs_Action/ 2>/dev/null
```

---

## SCRIPT

### Scene 1: Introduction (60 seconds)

**[Show VS Code with project open]**

> "Hi, I'm [Your Name], and this is my submission for the Personal AI Employee Hackathon - Bronze Tier.
>
> I built a Digital FTE - a Full-Time Equivalent AI employee that operates 24/7 to manage emails and tasks autonomously.
>
> Let me show you how it works."

**[Show folder structure in sidebar]**

> "The system has three main layers:
> 1. Perception - Gmail Watcher that monitors emails
> 2. Memory - An Obsidian vault storing everything as markdown
> 3. Reasoning - Claude Code that makes decisions based on a Company Handbook"

---

### Scene 2: The Vault Structure (60 seconds)

**[Navigate to Vault/ folder]**

> "Here's the Obsidian vault - the AI's brain."

**[Open Dashboard.md]**

> "The Dashboard is the control center, showing task queues and system status."

**[Open Company_Handbook.md]**

> "The Company Handbook contains all the rules - what to auto-approve, what needs human approval, priority levels, and rate limits.
>
> This is how we make the AI predictable and safe."

**[Show folder structure]**

> "Tasks flow through these folders:
> - Inbox → Needs_Action → Done (auto-approved)
> - Or → Pending_Approval → Approved → Done (needs human)"

---

### Scene 3: Gmail Watcher Demo (90 seconds)

**[Open terminal]**

> "Let's see the Gmail Watcher in action."

```bash
python src/watchers/gmail_watcher.py
```

**[Wait for output]**

> "The watcher connects to Gmail using OAuth 2.0, checks for new important emails, and creates markdown files for each one.
>
> Notice it extracts the sender, subject, priority, and full content."

**[Show created files in Needs_Action/]**

> "Each email becomes a task file with metadata, content, and suggested actions."

**[Press Ctrl+C to stop watcher]**

---

### Scene 4: Task Processing (90 seconds)

**[Open one of the task files]**

> "Here's a typical task. It's a system notification from [Service Name].
>
> Now watch as Claude Code processes it."

**[In terminal or show Claude Code processing]**

> "Claude reads the task, checks the Company Handbook rules, and decides:
> - This is a system notification
> - No reply needed
> - Auto-archive to Done"

**[Show file moved to Done/]**

> "The file is now in the Done folder. All 9 emails were processed automatically because they were all system notifications."

---

### Scene 5: Audit Trail (60 seconds)

**[Open Vault/Logs/2026-01-15.json]**

> "Every decision is logged with:
> - Timestamp
> - Action taken
> - Actor (watcher or Claude)
> - Result
>
> This audit trail is essential for compliance and debugging."

---

### Scene 6: Human-in-the-Loop (60 seconds)

**[Show Pending_Approval folder]**

> "Not everything is auto-approved. If Claude encounters:
> - Payment requests
> - Emails to new recipients
> - Anything over the limits in the handbook
>
> It moves the task here to Pending_Approval for human review."

**[Show workflow]**

> "The human reviews, moves to Approved, and then Claude executes.
>
> This keeps humans in control of sensitive decisions."

---

### Scene 7: Wrap-Up (60 seconds)

**[Show final state - empty Needs_Action, full Done]**

> "In summary:
> - Gmail Watcher created 9 task files from emails
> - Claude Code processed them all according to the handbook
> - Everything is logged for audit
>
> This is Bronze tier - the foundation for a Digital FTE."

**[Show future roadmap in SUBMISSION.md]**

> "For Silver and Gold tiers, I'd add:
> - WhatsApp watcher
> - LinkedIn automation
> - MCP servers for sending emails
> - Weekly CEO briefings
>
> Thank you for watching! Links in the description."

---

## Post-Recording

1. Upload to YouTube/Loom
2. Add timestamps in description
3. Update SUBMISSION.md with video link
4. Submit via Google Form

---

## Talking Points If Asked

**Q: Why markdown files instead of a database?**
> Human-readable, version-controllable, works with Obsidian for visualization, and Claude can read/write them directly.

**Q: What's the Ralph Wiggum loop?**
> A pattern that prevents lazy AI behavior by checking if the task file actually moved, not just if Claude said it's done. Named after a Simpsons joke about reinjecting prompts.

**Q: Is it secure?**
> Credentials never committed, OAuth uses minimal scopes (read-only for Gmail), rate limits prevent abuse, and sensitive actions require human approval.
