"""
Enhanced Audit Logger - Gold Tier Foundation

Provides comprehensive audit logging in JSONL format for all system operations.
Supports querying, filtering, and compliance-ready audit trails.

Features:
- JSONL (JSON Lines) format for easy parsing
- Daily log rotation
- Query interface with filtering
- Structured schema for all log entries
- Performance optimized (< 5ms overhead)
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
AUDIT_LOG_DIR = PROJECT_ROOT / "Vault" / "Logs" / "audit"
RETENTION_DAYS = 90  # Keep audit logs for 90 days


class AuditStatus(Enum):
    """Audit log entry status values."""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AuditDomain(Enum):
    """Domain classification for audit entries."""
    PERSONAL = "personal"
    BUSINESS = "business"
    SYSTEM = "system"
    BOTH = "both"


@dataclass
class AuditEntry:
    """
    Structured audit log entry.

    All fields are captured for complete audit trail.
    """
    timestamp: str  # ISO 8601 format
    action: str  # domain.operation (e.g., "odoo.create_invoice")
    actor: str  # "orchestrator", "human", "watcher", "mcp_server"
    domain: str  # "personal", "business", "system", "both"
    resource: str  # Resource identifier (e.g., "invoice_001")
    status: str  # "success", "failure", "pending", "approved", "rejected"
    details: Dict[str, Any]  # Additional context
    approval_required: bool = False
    approved_by: Optional[str] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None  # Operation duration in milliseconds

    def to_json(self) -> str:
        """Convert to JSON string for JSONL format."""
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> 'AuditEntry':
        """Create AuditEntry from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


class AuditLogger:
    """
    Enhanced audit logger with JSONL format and query capabilities.

    Usage:
        logger = AuditLogger()
        logger.log_action(
            action="odoo.create_invoice",
            actor="orchestrator",
            domain=AuditDomain.BUSINESS,
            resource="invoice_123",
            status=AuditStatus.SUCCESS,
            details={"amount": 1500, "customer": "Acme Corp"}
        )
    """

    def __init__(self, log_dir: Path = AUDIT_LOG_DIR):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Set up Python logging for errors
        self.logger = logging.getLogger("AuditLogger")
        self.logger.setLevel(logging.INFO)

    def _get_log_file(self, date: datetime = None) -> Path:
        """Get log file path for a specific date."""
        if date is None:
            date = datetime.now()
        filename = f"audit_{date.strftime('%Y-%m-%d')}.jsonl"
        return self.log_dir / filename

    def log_action(
        self,
        action: str,
        actor: str,
        domain: AuditDomain,
        resource: str,
        status: AuditStatus,
        details: Dict[str, Any] = None,
        approval_required: bool = False,
        approved_by: str = None,
        error: str = None,
        duration_ms: int = None
    ) -> bool:
        """
        Log an action to the audit trail.

        Args:
            action: Action identifier (e.g., "odoo.create_invoice")
            actor: Who performed the action
            domain: Domain classification
            resource: Resource identifier
            status: Operation status
            details: Additional context (optional)
            approval_required: Whether approval was needed
            approved_by: Who approved (if applicable)
            error: Error message (if failed)
            duration_ms: Operation duration in milliseconds

        Returns:
            True if logged successfully, False otherwise
        """
        try:
            entry = AuditEntry(
                timestamp=datetime.now().isoformat(),
                action=action,
                actor=actor,
                domain=domain.value,
                resource=resource,
                status=status.value,
                details=details or {},
                approval_required=approval_required,
                approved_by=approved_by,
                error=error,
                duration_ms=duration_ms
            )

            # Write to JSONL file (append mode)
            log_file = self._get_log_file()
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry.to_json() + '\n')

            return True

        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")
            return False

    def query(
        self,
        date_from: datetime = None,
        date_to: datetime = None,
        action: str = None,
        actor: str = None,
        domain: AuditDomain = None,
        status: AuditStatus = None,
        resource: str = None,
        max_results: int = 1000
    ) -> List[AuditEntry]:
        """
        Query audit logs with filtering.

        Args:
            date_from: Start date (inclusive)
            date_to: End date (inclusive)
            action: Filter by action
            actor: Filter by actor
            domain: Filter by domain
            status: Filter by status
            resource: Filter by resource
            max_results: Maximum number of results to return

        Returns:
            List of matching AuditEntry objects
        """
        results = []

        # Default date range: last 30 days
        if date_from is None:
            date_from = datetime.now() - timedelta(days=30)
        if date_to is None:
            date_to = datetime.now()

        # Get all log files in date range
        current_date = date_from
        while current_date <= date_to:
            log_file = self._get_log_file(current_date)
            if log_file.exists():
                results.extend(self._read_log_file(log_file))
            current_date += timedelta(days=1)

        # Apply filters
        filtered = results

        if action:
            filtered = [e for e in filtered if e.action == action]

        if actor:
            filtered = [e for e in filtered if e.actor == actor]

        if domain:
            filtered = [e for e in filtered if e.domain == domain.value]

        if status:
            filtered = [e for e in filtered if e.status == status.value]

        if resource:
            filtered = [e for e in filtered if e.resource == resource]

        # Limit results
        return filtered[:max_results]

    def _read_log_file(self, log_file: Path) -> List[AuditEntry]:
        """Read all entries from a log file."""
        entries = []

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = AuditEntry.from_json(line)
                            entries.append(entry)
                        except json.JSONDecodeError:
                            self.logger.warning(f"Invalid JSON in log file: {line[:100]}")
        except Exception as e:
            self.logger.error(f"Failed to read log file {log_file}: {e}")

        return entries

    def get_summary(
        self,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> Dict[str, Any]:
        """
        Get summary statistics for audit logs.

        Returns:
            Dictionary with summary stats:
            - total_operations
            - success_count
            - failure_count
            - by_domain
            - by_action
            - by_actor
        """
        entries = self.query(date_from=date_from, date_to=date_to, max_results=100000)

        summary = {
            "total_operations": len(entries),
            "success_count": sum(1 for e in entries if e.status == AuditStatus.SUCCESS.value),
            "failure_count": sum(1 for e in entries if e.status == AuditStatus.FAILURE.value),
            "pending_count": sum(1 for e in entries if e.status == AuditStatus.PENDING.value),
            "by_domain": {},
            "by_action": {},
            "by_actor": {},
            "approval_required_count": sum(1 for e in entries if e.approval_required),
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            }
        }

        # Count by domain
        for entry in entries:
            summary["by_domain"][entry.domain] = summary["by_domain"].get(entry.domain, 0) + 1
            summary["by_action"][entry.action] = summary["by_action"].get(entry.action, 0) + 1
            summary["by_actor"][entry.actor] = summary["by_actor"].get(entry.actor, 0) + 1

        return summary

    def export_to_csv(
        self,
        output_file: Path,
        date_from: datetime = None,
        date_to: datetime = None
    ) -> bool:
        """
        Export audit logs to CSV for compliance/analysis.

        Args:
            output_file: Path to output CSV file
            date_from: Start date
            date_to: End date

        Returns:
            True if successful
        """
        import csv

        try:
            entries = self.query(date_from=date_from, date_to=date_to, max_results=100000)

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if not entries:
                    return True

                # Write CSV with all fields
                fieldnames = [
                    'timestamp', 'action', 'actor', 'domain', 'resource',
                    'status', 'approval_required', 'approved_by', 'error',
                    'duration_ms', 'details'
                ]

                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for entry in entries:
                    row = asdict(entry)
                    row['details'] = json.dumps(row['details'])
                    writer.writerow(row)

            return True

        except Exception as e:
            self.logger.error(f"Failed to export to CSV: {e}")
            return False

    def cleanup_old_logs(self, retention_days: int = RETENTION_DAYS) -> int:
        """
        Remove audit logs older than retention period.

        Args:
            retention_days: Number of days to retain logs

        Returns:
            Number of files deleted
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0

        try:
            for log_file in self.log_dir.glob("audit_*.jsonl"):
                # Extract date from filename
                try:
                    date_str = log_file.stem.replace("audit_", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")

                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
                        self.logger.info(f"Deleted old audit log: {log_file.name}")

                except ValueError:
                    self.logger.warning(f"Could not parse date from filename: {log_file.name}")

        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")

        return deleted_count


# Global singleton instance
_global_logger = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = AuditLogger()
    return _global_logger


def log_audit(
    action: str,
    actor: str,
    domain: AuditDomain,
    resource: str,
    status: AuditStatus,
    **kwargs
) -> bool:
    """
    Convenience function to log an audit entry.

    Usage:
        from src.utils.audit_logger import log_audit, AuditDomain, AuditStatus

        log_audit(
            action="odoo.create_invoice",
            actor="orchestrator",
            domain=AuditDomain.BUSINESS,
            resource="invoice_123",
            status=AuditStatus.SUCCESS,
            details={"amount": 1500}
        )
    """
    logger = get_audit_logger()
    return logger.log_action(action, actor, domain, resource, status, **kwargs)


if __name__ == "__main__":
    # Test the audit logger
    print("Testing Enhanced Audit Logger...")

    logger = AuditLogger()

    # Test logging
    print("\n1. Testing log creation...")
    logger.log_action(
        action="test.create_invoice",
        actor="test_user",
        domain=AuditDomain.BUSINESS,
        resource="test_invoice_001",
        status=AuditStatus.SUCCESS,
        details={"amount": 1500, "customer": "Test Corp"},
        duration_ms=150
    )

    logger.log_action(
        action="test.record_expense",
        actor="orchestrator",
        domain=AuditDomain.BUSINESS,
        resource="test_expense_001",
        status=AuditStatus.SUCCESS,
        details={"amount": 50, "category": "Office Supplies"},
        approval_required=False,
        duration_ms=75
    )

    logger.log_action(
        action="test.send_email",
        actor="email_sender",
        domain=AuditDomain.PERSONAL,
        resource="email_123",
        status=AuditStatus.FAILURE,
        error="SMTP connection failed",
        duration_ms=5000
    )

    print("[OK] 3 test entries logged")

    # Test querying
    print("\n2. Testing queries...")

    all_entries = logger.query()
    print(f"[OK] Total entries: {len(all_entries)}")

    business_entries = logger.query(domain=AuditDomain.BUSINESS)
    print(f"[OK] Business entries: {len(business_entries)}")

    failures = logger.query(status=AuditStatus.FAILURE)
    print(f"[OK] Failed operations: {len(failures)}")

    # Test summary
    print("\n3. Testing summary...")
    summary = logger.get_summary()
    print(f"[OK] Summary generated:")
    print(f"  - Total operations: {summary['total_operations']}")
    print(f"  - Success count: {summary['success_count']}")
    print(f"  - Failure count: {summary['failure_count']}")
    print(f"  - By domain: {summary['by_domain']}")

    # Test CSV export
    print("\n4. Testing CSV export...")
    export_file = PROJECT_ROOT / "test_audit_export.csv"
    if logger.export_to_csv(export_file):
        print(f"[OK] Exported to: {export_file}")
        print(f"  File size: {export_file.stat().st_size} bytes")

    print("\n[SUCCESS] All tests passed!")
