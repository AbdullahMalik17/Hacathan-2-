# Digital FTE - Personal AI Employee

An autonomous AI agent operating 24/7 to manage personal and business affairs autonomously.

## Overview

Digital FTE (Full-Time Equivalent) is an AI-powered personal assistant that combines:
- **Claude Code** as the reasoning engine
- **Obsidian** as the local knowledge base
- **Python Watchers** for perception (monitoring emails, files, etc.)
- **MCP Servers** for external actions

### Key Benefits
- Operates 8,760 hours/year (vs human 2,000 hours)
- 85-90% cost savings compared to human FTE
- 24/7 availability with human-in-the-loop safety

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Digital FTE System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   WATCHERS   │───▶│    VAULT     │◀───│    CLAUDE    │  │
│  │  (Sensors)   │    │  (Obsidian)  │    │    CODE      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│        │                    │                    │          │
│        ▼                    ▼                    ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Gmail Watch  │    │ /Needs_Action│    │ Orchestrator │  │
│  │ File Watch   │    │ /Pending_App │    │ Ralph Wiggum │  │
│  │ WhatsApp     │    │ /Done        │    │    Loop      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
Hacathan_2/
├── Vault/                      # Obsidian vault (knowledge base)
│   ├── Dashboard.md            # Main control center
│   ├── Company_Handbook.md     # Rules and guidelines
│   ├── Inbox/                  # New incoming items
│   ├── Needs_Action/           # Tasks awaiting processing
│   ├── Pending_Approval/       # Tasks needing human approval
│   ├── Approved/               # Tasks human-approved for action
│   ├── Done/                   # Completed tasks
│   ├── Logs/                   # Daily JSON logs
│   ├── Templates/              # Markdown templates
│   └── Archive/                # Historical tasks (>30 days)
├── src/
│   ├── orchestrator.py         # Main loop (Ralph Wiggum pattern)
│   ├── watchers/
│   │   └── gmail_watcher.py    # Gmail monitoring daemon
│   └── utils/
│       ├── file_manager.py     # Vault file operations
│       └── logger.py           # Logging utilities
├── config/
│   ├── .env.example            # Environment template
│   └── credentials.json        # Google API credentials (not committed)
├── .claude/
│   └── hooks/                  # Claude Code integration hooks
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Quick Start

### Prerequisites
- Python 3.10+
- Claude Code CLI installed (`npm install -g @anthropic/claude-code`)
- Obsidian (optional, for GUI viewing)
- Google Cloud project with Gmail API enabled

### Installation

1. **Clone and setup environment**
```bash
cd Hacathan_2
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp config/.env.example config/.env
# Edit config/.env with your settings
```

3. **Setup Gmail API credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project and enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` to `config/` folder

4. **Authenticate Gmail Watcher**
```bash
python src/watchers/gmail_watcher.py
# Follow OAuth flow in browser (first time only)
```

### Running the System

**Start Gmail Watcher (in one terminal):**
```bash
python src/watchers/gmail_watcher.py
```

**Start Orchestrator (in another terminal):**
```bash
python src/orchestrator.py
```

**Dry run mode (no actual actions):**
```bash
python src/orchestrator.py --dry-run
```

## Workflow: Perception → Reasoning → Action

### 1. Perception (Watchers)
Watchers continuously monitor external sources:
- **Gmail Watcher**: Monitors for new important emails
- Creates markdown task files in `/Vault/Needs_Action/`

### 2. Reasoning (Claude Code)
The orchestrator invokes Claude Code to:
- Analyze tasks against Company Handbook rules
- Determine appropriate actions
- Auto-approve or request human approval

### 3. Action (Human-in-the-Loop)
Based on handbook rules:
- **Auto-approve**: Low-risk actions execute immediately
- **Require approval**: Sensitive actions go to `/Pending_Approval/`
- Human reviews and moves to `/Approved/` to execute

## The Ralph Wiggum Loop

This pattern prevents "lazy agent" behavior:

```
┌─────────────────────────────────────────┐
│           Start Processing              │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│      Invoke Claude Code with Task       │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│         Check: Task Completed?          │
└────────┬────────────────────┬───────────┘
         │ YES                │ NO
         ▼                    ▼
┌─────────────┐    ┌─────────────────────┐
│    Exit     │    │  Re-inject Prompt   │
│   Success   │    │  (max N iterations) │
└─────────────┘    └──────────┬──────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │ Back to Claude Code  │
                   └──────────────────────┘
```

## Company Handbook Rules

The `Company_Handbook.md` defines:

### Auto-Approve Actions
- Replies to known contacts
- Newsletter unsubscribes
- Recurring subscriptions under $50

### Require Approval
- Emails to new recipients
- Payments over $100
- External business communications

### Priority Keywords
| Priority | Keywords |
|----------|----------|
| URGENT | urgent, asap, emergency, deadline today |
| HIGH | important, invoice, payment, client |
| MEDIUM | question, request, update |
| LOW | newsletter, notification, digest |

## Security

### Credentials
- **Never** commit credentials to git
- Use environment variables or system keychains
- `config/.gitignore` protects sensitive files

### Rate Limits
| Action | Hourly Limit |
|--------|-------------|
| Emails sent | 10 |
| Payments | 3 |
| API calls | 100 |

### Audit Logging
Every action logs to `/Vault/Logs/YYYY-MM-DD.json`:
- Timestamp
- Action type
- Actor
- Approval status
- Result

## Hackathon Tier: Gold ⭐

This implementation covers Gold tier requirements:

### Bronze Tier ✅
- [x] Basic Obsidian vault structure
- [x] One watcher script (Gmail)
- [x] Claude Code integration
- [x] Folder hierarchy (/Inbox, /Needs_Action, /Done)
- [x] Human-in-the-loop workflow
- [x] Audit logging

### Silver Tier ✅
- [x] WhatsApp watcher
- [x] Filesystem watcher (DropFolder)
- [x] MCP servers for actions (Email sender)
- [x] Weekly CEO briefings
- [x] Multi-agent fallback system

### Gold Tier ✅ (Current)
- [x] LinkedIn automation with browser control
  - Playwright-based LinkedIn posting
  - Auto-generation from CEO Briefing
  - Approval workflow for posts
  - Rate limiting (2 posts/day, 1/hour)
  - Configurable posting schedule
- [x] Agent Skills Conversion
  - `watching-gmail` - Gmail monitoring skill
  - `watching-whatsapp` - WhatsApp monitoring skill
  - `watching-filesystem` - DropFolder monitoring skill
  - `digital-fte-orchestrator` - Main orchestrator skill
  - `generating-ceo-briefing` - CEO report generation skill
  - `sending-emails` - Email sending skill
  - `posting-linkedin` - LinkedIn posting skill
  - `managing-services` - Service management skill

### LinkedIn Posting Workflow

```
CEO Briefing → Content Generator → Pending_Approval/
Manual Queue → LinkedIn Scheduler → Pending_Approval/
                                          ↓
                                    (Human Review)
                                          ↓
                                     Approved/
                                          ↓
                                  LinkedIn Poster
                                          ↓
                                       Done/
```

## Future Enhancements (Platinum+)

- [ ] Frontend Dashboard (React/Next.js)
- [ ] Odoo ERP integration
- [ ] Cloud deployment (Kubernetes)
- [ ] Voice interaction (Whisper/TTS)
- [ ] Mobile app for approvals

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - See LICENSE file

## Acknowledgments

- Anthropic for Claude Code
- Obsidian for local-first knowledge management
- Google for Gmail API

---

**Hackathon Submission**
- Tier: Gold ⭐
- Features: LinkedIn automation, 8 agent skills, multi-agent fallback
- Demo Video: [Link TBD]
- Security: Credentials managed via environment variables, not committed