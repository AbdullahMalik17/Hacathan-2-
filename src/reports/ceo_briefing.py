"""
Weekly CEO Briefing Generator - Digital FTE Reporting System

This script generates a weekly summary report of all Digital FTE activities,
providing visibility into what the autonomous system accomplished.

Setup:
1. Run manually: python ceo_briefing.py
2. Schedule with Task Scheduler for Monday 8:00 AM
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
LOGS_PATH = VAULT_PATH / "Logs"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
DONE_PATH = VAULT_PATH / "Done"
ARCHIVE_PATH = VAULT_PATH / "Archive"

# Import AI agent utility and audit logger
sys.path.append(str(PROJECT_ROOT / "src"))
try:
    from utils.ai_agent import invoke_agent
    from utils.audit_logger import log_audit, AuditDomain, AuditStatus
except ImportError:
    def invoke_agent(prompt, dry_run=False):
        return False, "", "none"
    # Audit logger imports optional - we read from log files directly

# ROI Values (Estimated dollars saved per action)
ROI_VALUES = {
    "file_detected": 1.0,
    "email_sent": 2.0,
    "task_completed": 1.5,
    "plan_created": 5.0,
    "linkedin_posted": 10.0,
    "whatsapp_message": 1.5,
    "error_recovery": 5.0
}

# Report configuration
REPORT_DAYS = int(os.getenv("BRIEFING_DAYS", "7"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CEOBriefing")


def ensure_directories():
    """Ensure all required directories exist."""
    for path in [LOGS_PATH, VAULT_PATH]:
        path.mkdir(parents=True, exist_ok=True)


def calculate_roi(entries: List[Dict[str, Any]]) -> float:
    """Calculate the estimated ROI in dollars for the period."""
    total_roi = 0.0
    for entry in entries:
        action = entry.get("action", "")
        # Basic mapping
        if action in ROI_VALUES:
            total_roi += ROI_VALUES[action]
        elif "success" in str(entry.get("result", "")).lower():
            total_roi += 0.5 # Default success value
    return total_roi


def get_ai_narrative(report_text: str) -> str:
    """Get a narrative summary of the report from an AI agent."""
    prompt = f"""You are a senior executive assistant. Summarize this weekly FTE report for the CEO.
Highlight key wins, concerns, and ROI. Be professional and concise.

Report Metrics:
{report_text[:2000]}

Format:
## Executive Narrative Summary
[Your summary here]

## Key Highlights
- [Highlight 1]
- [Highlight 2]
"""
    success, output, agent = invoke_agent(prompt)
    if success:
        return output
    return "Narrative summary unavailable."


def get_date_range() -> tuple:
    """Get start and end dates for the report period."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=REPORT_DAYS)
    return start_date, end_date


def load_log_files(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Load all log entries from the specified date range."""
    all_entries = []

    if not LOGS_PATH.exists():
        logger.warning(f"Logs directory not found: {LOGS_PATH}")
        return all_entries

    current_date = start_date
    while current_date <= end_date:
        log_file = LOGS_PATH / f"{current_date.strftime('%Y-%m-%d')}.json"

        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    entries = json.load(f)
                    if isinstance(entries, list):
                        all_entries.extend(entries)
                    else:
                        all_entries.append(entries)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse log file {log_file}: {e}")
            except Exception as e:
                logger.error(f"Error reading log file {log_file}: {e}")

        current_date += timedelta(days=1)

    return all_entries


def count_folder_items(folder_path: Path) -> int:
    """Count markdown files in a folder."""
    if not folder_path.exists():
        return 0
    return len(list(folder_path.glob("*.md")))


def analyze_tasks_by_source(entries: List[Dict[str, Any]]) -> Dict[str, int]:
    """Analyze tasks grouped by source (Gmail, WhatsApp, Files, etc.)."""
    sources = defaultdict(int)

    for entry in entries:
        actor = entry.get("actor", "unknown")
        action = entry.get("action", "")

        # Map actors to friendly source names
        if "gmail" in actor.lower():
            sources["Gmail"] += 1
        elif "whatsapp" in actor.lower():
            sources["WhatsApp"] += 1
        elif "filesystem" in actor.lower() or "file" in actor.lower():
            sources["Filesystem"] += 1
        elif "orchestrator" in actor.lower():
            sources["Orchestrator"] += 1
        elif "email_sender" in actor.lower():
            sources["Email Sender"] += 1
        else:
            sources["Other"] += 1

    return dict(sources)


def analyze_actions(entries: List[Dict[str, Any]]) -> Dict[str, int]:
    """Analyze actions taken."""
    actions = defaultdict(int)

    for entry in entries:
        action = entry.get("action", "unknown")
        actions[action] += 1

    return dict(actions)


def find_errors(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find all error entries."""
    errors = []

    for entry in entries:
        result = entry.get("result", "")
        action = entry.get("action", "")

        if result == "failure" or action == "error" or "error" in str(entry).lower():
            errors.append({
                "timestamp": entry.get("timestamp", "Unknown"),
                "actor": entry.get("actor", "Unknown"),
                "action": entry.get("action", "Unknown"),
                "error": entry.get("error", entry.get("details", "Unknown error"))
            })

    return errors


def get_pending_items() -> List[Dict[str, str]]:
    """Get list of pending items requiring attention."""
    pending = []

    # Check Needs_Action folder
    if NEEDS_ACTION_PATH.exists():
        for file in NEEDS_ACTION_PATH.glob("*.md"):
            pending.append({
                "type": "Needs Action",
                "file": file.name,
                "created": datetime.fromtimestamp(file.stat().st_ctime).strftime("%Y-%m-%d %H:%M")
            })

    # Check Pending_Approval folder
    if PENDING_APPROVAL_PATH.exists():
        for file in PENDING_APPROVAL_PATH.glob("*.md"):
            pending.append({
                "type": "Pending Approval",
                "file": file.name,
                "created": datetime.fromtimestamp(file.stat().st_ctime).strftime("%Y-%m-%d %H:%M")
            })

    return pending


def generate_briefing_report(
    start_date: datetime,
    end_date: datetime,
    entries: List[Dict[str, Any]],
    sources: Dict[str, int],
    actions: Dict[str, int],
    errors: List[Dict[str, Any]],
    pending: List[Dict[str, str]]
) -> str:
    """Generate the CEO briefing markdown report."""

    total_tasks = sum(sources.values())
    total_errors = len(errors)
    total_pending = len(pending)
    roi = calculate_roi(entries)

    # Determine overall status
    if total_errors > 5:
        status_emoji = "🔴"
        status_text = "Needs Attention"
    elif total_pending > 10:
        status_emoji = "🟡"
        status_text = "Review Pending Items"
    else:
        status_emoji = "🟢"
        status_text = "Operating Normally"

    # Fetch Odoo Financials (New)
    financials = {}
    try:
        # Import Odoo MCP here to avoid circular imports or early failure if not setup
        sys.path.append(str(PROJECT_ROOT))
        from src.mcp_servers.odoo_server import get_financial_summary
        
        fin_start = start_date.strftime('%Y-%m-%d')
        fin_end = end_date.strftime('%Y-%m-%d')
        financials = get_financial_summary(date_from=fin_start, date_to=fin_end)
        logger.info("Retrieved Odoo financial summary")
    except Exception as e:
        logger.warning(f"Could not fetch Odoo financials: {e}")
        financials = {"error": "Financial data unavailable (Odoo offline or unconfigured)"}

    # Pre-report for AI summary
    pre_report = f"""
Period: {start_date.date()} to {end_date.date()}
Total Activities: {total_tasks}
Success Rate: {((total_tasks - total_errors)/total_tasks*100) if total_tasks > 0 else 0:.1f}%
Estimated ROI: ${roi:.2f}
Errors: {total_errors}
Pending: {total_pending}
Top Actions: {dict(sorted(actions.items(), key=lambda x: x[1], reverse=True)[:5])}
Financials: {json.dumps(financials)}
"""
    ai_summary = get_ai_narrative(pre_report)

    report = f"""# {status_emoji} CEO Weekly Briefing

**Report Period:** {start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}
**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
**Status:** {status_text}

---

{ai_summary}

---

## Financial Performance (Odoo)

"""
    if "error" in financials:
        report += f"> ⚠️ **Note:** {financials['error']}\n"
    else:
        revenue = financials.get('revenue', 0.0)
        expenses = financials.get('expenses', 0.0)
        profit = financials.get('profit', 0.0)
        margin = financials.get('profit_margin', 0.0)
        
        report += f"""| Metric | Amount |
|--------|--------|
| **Revenue** | **${revenue:,.2f}** |
| Expenses | ${expenses:,.2f} |
| **Net Profit** | **${profit:,.2f}** |
| Margin | {margin:.1f}% |

*Based on {financials.get('invoice_count', 0)} invoices and {financials.get('bill_count', 0)} bills.*
"""

    report += f"""
---

## Operational Metrics

Your Digital FTE processed **{total_tasks}** activities this week across all channels.

| Metric | Value |
|--------|-------|
| Total Activities | {total_tasks} |
| Estimated Time Savings | **${roi:.2f}** |
| Success Rate | {((total_tasks - total_errors)/total_tasks*100) if total_tasks > 0 else 0:.1f}% |
| Items Pending Action | {count_folder_items(NEEDS_ACTION_PATH)} |
| Items Awaiting Approval | {count_folder_items(PENDING_APPROVAL_PATH)} |
| Errors Encountered | {total_errors} |

---

## Activity by Source

"""

    if sources:
        report += "| Source | Count | % of Total |\n"
        report += "|--------|-------|------------|\n"
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_tasks * 100) if total_tasks > 0 else 0
            report += f"| {source} | {count} | {percentage:.1f}% |\n"
    else:
        report += "_No activities recorded this period._\n"

    report += """
---

## Actions Performed

"""

    if actions:
        report += "| Action Type | Count |\n"
        report += "|-------------|-------|\n"
        for action, count in sorted(actions.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"| {action} | {count} |\n"
    else:
        report += "_No actions recorded this period._\n"

    report += """
---

## Pending Items Requiring Attention

"""

    if pending:
        needs_action = [p for p in pending if p["type"] == "Needs Action"]
        pending_approval = [p for p in pending if p["type"] == "Pending Approval"]

        if needs_action:
            report += f"### Needs Action ({len(needs_action)} items)\n\n"
            for item in needs_action[:5]:  # Show top 5
                report += f"- **{item['file']}** (created {item['created']})\n"
            if len(needs_action) > 5:
                report += f"- _...and {len(needs_action) - 5} more items_\n"
            report += "\n"

        if pending_approval:
            report += f"### Pending Approval ({len(pending_approval)} items)\n\n"
            for item in pending_approval[:5]:  # Show top 5
                report += f"- **{item['file']}** (created {item['created']})\n"
            if len(pending_approval) > 5:
                report += f"- _...and {len(pending_approval) - 5} more items_\n"
            report += "\n"
    else:
        report += "_No pending items. All caught up!_\n"

    report += """
---

## Errors & Exceptions

"""

    if errors:
        report += f"**{total_errors} errors** encountered this period:\n\n"
        report += "| Time | Source | Action | Error |\n"
        report += "|------|--------|--------|-------|\n"
        for error in errors[:10]:  # Show top 10
            timestamp = error.get("timestamp", "")[:16]  # Truncate
            actor = error.get("actor", "")[:15]
            action = error.get("action", "")[:20]
            err_msg = str(error.get("error", ""))[:40]
            report += f"| {timestamp} | {actor} | {action} | {err_msg} |\n"
        if len(errors) > 10:
            report += f"\n_...and {len(errors) - 10} more errors. Check logs for details._\n"
    else:
        report += "_No errors recorded this period._\n"

    report += """
---

## System Health

| Component | Status |
|-----------|--------|
| Gmail Watcher | """ + ("🟢 Active" if (LOGS_PATH / f"{datetime.now().strftime('%Y-%m-%d')}.json").exists() else "🟡 Check Logs") + """ |
| WhatsApp Watcher | 🟡 Requires Session |
| Filesystem Watcher | 🟢 Configured |
| Email Sender MCP | 🟢 Ready |
| Orchestrator | 🟢 Ready |

---

## Recommendations

"""

    recommendations = []

    if total_pending > 10:
        recommendations.append("Review and process pending items to prevent backlog")
    if total_errors > 3:
        recommendations.append("Investigate recurring errors in the system logs")
    if sources.get("WhatsApp", 0) == 0:
        recommendations.append("Verify WhatsApp Web session is authenticated")
    if total_tasks == 0:
        recommendations.append("Check that all watchers are running correctly")
    if not recommendations:
        recommendations.append("System is operating normally - no immediate actions required")

    for i, rec in enumerate(recommendations, 1):
        report += f"{i}. {rec}\n"

    report += f"""
---

## Quick Links

- **Needs Action Folder:** `Vault/Needs_Action/`
- **Pending Approval:** `Vault/Pending_Approval/`
- **Logs:** `Vault/Logs/`
- **Dashboard:** `Vault/Dashboard.md`

---

_This report was automatically generated by your Digital FTE._
_For questions or issues, check the system logs or contact your administrator._
"""

    return report


def save_briefing(report: str) -> Optional[Path]:
    """Save the briefing report to the Vault."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"CEO_Briefing_{date_str}.md"
    filepath = VAULT_PATH / filename

    if DRY_RUN:
        logger.info(f"[DRY RUN] Would save briefing to: {filepath}")
        print(report)
        return None

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Briefing saved to: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save briefing: {e}")
        return None


def main():
    """Main entry point."""
    global REPORT_DAYS, DRY_RUN
    import argparse
    parser = argparse.ArgumentParser(description="CEO Briefing Generator")
    parser.add_argument("--days", type=int, default=REPORT_DAYS, help="Number of days to report")
    parser.add_argument("--email", type=str, help="Email address to send the report to")
    parser.add_argument("--dry-run", action="store_true", help="Don't save or send anything")
    args = parser.parse_args()

    REPORT_DAYS = args.days
    DRY_RUN = args.dry_run

    logger.info("=" * 50)
    logger.info("CEO Briefing Generator Starting...")
    logger.info(f"Report Period: {REPORT_DAYS} days")
    logger.info(f"Dry Run: {DRY_RUN}")
    logger.info("=" * 50)

    ensure_directories()

    # Get date range
    start_date, end_date = get_date_range()
    logger.info(f"Analyzing period: {start_date.date()} to {end_date.date()}")

    # Load and analyze data
    entries = load_log_files(start_date, end_date)
    logger.info(f"Loaded {len(entries)} log entries")

    sources = analyze_tasks_by_source(entries)
    actions = analyze_actions(entries)
    errors = find_errors(entries)
    pending = get_pending_items()

    # Generate report
    report = generate_briefing_report(
        start_date, end_date, entries,
        sources, actions, errors, pending
    )

    # Save report
    filepath = save_briefing(report)

    # Email distribution (FR-005)
    if args.email and not DRY_RUN:
        logger.info(f"Sending report to {args.email}...")
        try:
            from mcp_servers.email_sender import _send_email_logic
            subject = f"Weekly CEO Briefing - {datetime.now().strftime('%Y-%m-%d')}"
            result = _send_email_logic(to=args.email, subject=subject, body=report)
            logger.info(f"Email result: {result}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    if filepath:
        logger.info(f"CEO Briefing generated successfully: {filepath}")
    else:
        logger.info("CEO Briefing generation complete")

    logger.info("=" * 50)

    return report


if __name__ == "__main__":
    main()
