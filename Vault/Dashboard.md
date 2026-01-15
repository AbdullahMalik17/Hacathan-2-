# Digital FTE Dashboard

> **Status:** 🟢 Active | **Last Updated:** {{date}}

---

## Quick Stats

| Metric | Today | This Week | This Month |
|--------|-------|-----------|------------|
| Tasks Processed | 0 | 0 | 0 |
| Emails Handled | 0 | 0 | 0 |
| Approvals Pending | 0 | 0 | 0 |
| Actions Completed | 0 | 0 | 0 |

---

## Current Queues

### 📥 Inbox
```dataview
LIST FROM "Inbox"
WHERE file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

### ⚡ Needs Action
```dataview
LIST FROM "Needs_Action"
WHERE file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

### ⏳ Pending Approval
```dataview
LIST FROM "Pending_Approval"
WHERE file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

---

## Recent Activity Log

| Time | Action | Status | Details |
|------|--------|--------|---------|
| - | System initialized | ✅ | Digital FTE started |

---

## System Health

- **Orchestrator:** 🟢 Running
- **Gmail Watcher:** 🟢 Active
- **Claude Code:** 🟢 Connected

---

## Quick Actions

- [ ] Review pending approvals
- [ ] Check error logs
- [ ] Update Company Handbook

---

## Links

- [[Company_Handbook]] - Rules and guidelines
- [[Logs/]] - System logs
- [[Archive/]] - Completed tasks

---

*This dashboard updates automatically based on vault activity.*
