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

> **Overall Status:** 🟡 DEGRADED | **Last Check:** 2026-01-18 11:50:42

### Services

| Service | Status | Uptime (7d) | Response Time | Last Check |
|---------|--------|-------------|---------------|------------|
| **Orchestrator** | 🟢 Healthy | 100.0% | 3ms | 11:50:40 |
| **Email Sender MCP** | 🟢 Healthy | 0.0% | 0ms | 11:50:40 |
| **Gmail Watcher** | 🔴 Unhealthy | 0.0% | 2ms | 11:50:40 |

### Performance Metrics

| Metric | Value |
|--------|-------|
| **Tasks Processed Today** | 0 |
| **Tasks Failed Today** | 0 |
| **Error Rate** | 50.0% |
| **CPU Usage** | 40.6% |
| **Memory Usage** | 86.7% |
| **Disk Usage** | 21.7% |

### Active Alerts

- 🔴 **HIGH:** Service Gmail Watcher is unhealthy: Health check failed
- 🟡 **MEDIUM:** High error rate: 50.0%

---

*Health data auto-generated from: `Dashboard_Data.json`*

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
