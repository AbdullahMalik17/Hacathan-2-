# Hackathon Submission: Digital FTE

## Project Information

| Field | Value |
|-------|-------|
| **Project Name** | Digital FTE - Personal AI Employee |
| **Tier** | Bronze (8-12 hours) |
| **Team Members** | [Your Name] |
| **GitHub Repository** | [Your GitHub URL] |
| **Demo Video** | [YouTube/Loom Link - TBD] |

---

## Executive Summary

Digital FTE is an autonomous AI agent that operates 24/7 to manage personal and business affairs. Built using Claude Code as the reasoning engine and Obsidian as the local knowledge base, it demonstrates the core concepts of building a "Digital Full-Time Equivalent" employee.

### Key Achievements
- Fully functional Gmail watcher that monitors emails in real-time
- Obsidian vault with structured folder hierarchy
- Company Handbook with auto-approve and approval-required rules
- Ralph Wiggum loop pattern for task completion assurance
- Complete audit logging for compliance

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Digital FTE System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   WATCHERS   │───▶│    VAULT     │◀───│    CLAUDE    │  │
│  │  (Sensors)   │    │  (Obsidian)  │    │    CODE      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  Perception          Memory/State        Reasoning          │
│  Gmail API           Markdown Files      Company Handbook   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Workflow: Perception → Reasoning → Action

1. **Perception**: Gmail watcher monitors inbox for new important emails
2. **Reasoning**: Claude Code analyzes emails against Company Handbook rules
3. **Action**: Auto-archive notifications OR request human approval for sensitive items

---

## Bronze Tier Checklist

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Basic Obsidian vault structure | ✅ Complete | `Vault/` with Dashboard.md, Company_Handbook.md |
| One watcher script | ✅ Complete | `src/watchers/gmail_watcher.py` |
| Claude Code integration | ✅ Complete | Orchestrator + direct Claude processing |
| Folder hierarchy | ✅ Complete | Inbox → Needs_Action → Done flow |
| Human-in-the-Loop | ✅ Complete | Pending_Approval folder workflow |
| Audit logging | ✅ Complete | JSON logs in `Vault/Logs/` |

---

## Security Disclosure

### Credential Handling
- **credentials.json**: Downloaded from Google Cloud Console, stored in `config/` folder
- **token.json**: Auto-generated during OAuth flow, stored locally
- **Both files**: Excluded from git via `.gitignore` and `config/.gitignore`
- **No credentials committed**: Repository contains only `.env.example` template

### Security Measures
1. OAuth 2.0 with minimal scopes (gmail.readonly only)
2. Rate limiting configured in Company Handbook
3. DRY_RUN mode for safe testing
4. All actions logged with timestamps

### Environment Variables
```bash
# All sensitive config via environment variables
DRY_RUN=false
GMAIL_POLL_INTERVAL=60
MAX_ITERATIONS=10
```

---

## Demo Script (5-10 minutes)

### Part 1: Introduction (1 min)
- Show the project structure in VS Code/IDE
- Explain the Digital FTE concept
- Highlight the three-layer architecture

### Part 2: Gmail Watcher Demo (2 min)
- Show `credentials.json` location (without exposing contents)
- Run `python src/watchers/gmail_watcher.py`
- Watch as new emails become markdown files in `Vault/Needs_Action/`

### Part 3: Processing Demo (2 min)
- Show the task files in Obsidian (optional) or file explorer
- Demonstrate Claude Code reading and analyzing tasks
- Show files moving to `Vault/Done/`

### Part 4: Audit Trail (1 min)
- Open `Vault/Logs/2026-01-15.json`
- Show the structured audit log entries
- Explain compliance benefits

### Part 5: Company Handbook (1 min)
- Open `Vault/Company_Handbook.md`
- Show auto-approve vs require-approval rules
- Explain how rules guide Claude's decisions

### Part 6: Wrap-up (1 min)
- Show the empty `Needs_Action/` folder (all processed)
- Summarize: 9 emails processed automatically
- Mention future enhancements (Silver+ features)

---

## Technical Specifications

### Dependencies
```
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.100.0
watchdog>=3.0.0
python-dotenv>=1.0.0
```

### Folder Structure
```
Hacathan_2/
├── Vault/                      # Obsidian knowledge base
│   ├── Dashboard.md            # Control center
│   ├── Company_Handbook.md     # Rules and guidelines
│   ├── Inbox/                  # New items
│   ├── Needs_Action/           # Pending processing
│   ├── Pending_Approval/       # HITL queue
│   ├── Approved/               # Ready to execute
│   ├── Done/                   # Completed
│   └── Logs/                   # Audit trail
├── src/
│   ├── orchestrator.py         # Ralph Wiggum loop
│   ├── watchers/
│   │   └── gmail_watcher.py    # Email monitoring
│   └── utils/                  # Helper modules
├── config/
│   └── .env.example            # Environment template
└── README.md                   # Documentation
```

---

## Innovation Highlights

1. **Ralph Wiggum Loop**: Prevents lazy agent behavior by re-injecting prompts until tasks are actually completed (files moved, not just analyzed)

2. **Markdown-First Design**: All data stored as human-readable markdown, enabling both AI processing and human review

3. **Handbook-Driven Decisions**: Externalized rules in `Company_Handbook.md` allow easy customization without code changes

4. **Complete Audit Trail**: Every decision logged with timestamp, actor, and reasoning for compliance

---

## Lessons Learned

1. **Gmail API Setup**: OAuth 2.0 requires careful test user configuration for external apps
2. **File-Based State**: Markdown files provide excellent visibility into system state
3. **Human-in-the-Loop**: Essential for trust - users need to approve sensitive actions
4. **Dry Run Mode**: Critical for safe development and testing

---

## Future Enhancements (Silver+ Roadmap)

- [ ] WhatsApp watcher using Playwright
- [ ] LinkedIn automation for professional networking
- [ ] MCP servers for sending emails (action layer)
- [ ] Odoo ERP integration for business operations
- [ ] Weekly CEO briefing generation
- [ ] Cloud deployment (Oracle Cloud free tier)

---

## Contact

- **GitHub**: [Your GitHub]
- **Email**: [Your Email]
- **LinkedIn**: [Your LinkedIn]

---

*Built for the Personal AI Employee Hackathon 0: Building Autonomous FTEs*
