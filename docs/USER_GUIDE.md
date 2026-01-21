# Digital FTE - User Manual (Platinum Tier)

Welcome to your Digital FTE, **Abdullah Junior**. This autonomous agent manages your emails, files, WhatsApp messages, social media, and accounting 24/7.

## 🚀 Quick Start

### 1. Launch the System
```powershell
./Launch_Abdullah_Junior.ps1
```
This starts:
- **Orchestrator**: The brain processing tasks.
- **Frontend Dashboard**: Visual interface at `http://localhost:3000`.
- **Watchers**: Background monitors for Gmail, Files, WhatsApp.

### 2. Configure Credentials
Edit `config/.env`:
- **WhatsApp**: Requires scanning QR code in the browser window on first run.
- **Gmail/Calendar**: Requires `credentials.json` from Google Cloud.
- **Odoo**: Set `ODOO_URL`, `ODOO_USERNAME`, `ODOO_PASSWORD`.
- **Social**: Set tokens for Meta/Twitter.

---

## 🖥️ Using the Dashboard

Access at `http://localhost:3000`.

### Command Chat
- Type natural language commands: "Draft an invoice for Client X for $500", "Post update to LinkedIn about our new feature".
- Set priority (Low/Medium/High/Urgent).

### Live Terminal
- Watch real-time logs of the agent's thinking process and actions.

### Task Board
- **Pending**: Items waiting for action or human approval.
- **Completed**: History of executed tasks.

### Widgets
- **Financial Health**: Real-time Revenue/Expense/Profit from Odoo.
- **Social Pulse**: Engagement stats from Twitter/LinkedIn/Meta.

---

## 🤖 Capabilities

### 📧 Email & Calendar
- **Monitor**: Reads emails, categorizes priority.
- **Respond**: Drafts replies (auto-sends to known contacts if enabled).
- **Calendar**: "Schedule a meeting with X on Tuesday" -> Checks availability and creates event.

### 💬 WhatsApp
- **Monitor**: Reads messages. Escalate urgent ones from unknown numbers.
- **Reply**: Auto-replies to known contacts (24h cooldown).
- **Send**: "WhatsApp Alice that I'm running late" -> Queues message.

### 💼 Accounting (Odoo)
- **Invoicing**: "Create invoice for Acme Corp for Web Design, qty 1, price 1000".
- **Expenses**: "Record bill from AWS for Hosting, $50".
- **Reporting**: Weekly CEO Briefing includes real-time P&L.

### 📱 Social Media
- **LinkedIn**: Auto-generates posts from weekly updates.
- **Twitter/Meta**: Posts updates, tracks engagement.

---

## ☁️ Platinum Features (Cloud/Local)

- **Cloud Mode**: Runs on a VPS (24/7). Monitors and Drafts.
- **Local Mode**: Runs on your laptop. Approves and Executes.
- **Sync**: Git-based sync keeps them in step every 5 minutes.

---

## 🛠️ Troubleshooting

**Logs**: Check `Vault/Logs/YYYY-MM-DD.json` for detailed execution history.
**Restart**: If a service hangs, the Service Manager auto-restarts it. Run `python src/service_manager.py --status` to check.
