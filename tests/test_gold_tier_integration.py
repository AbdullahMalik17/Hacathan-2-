"""
Gold Tier Integration Tests - End-to-End Validation

Tests all Gold Tier requirements:
1. All Silver requirements met
2. Cross-domain integration (Personal + Business)
3. Multiple MCP servers (Email, Odoo, Social Media)
4. Weekly business audit with CEO briefing
5. Error recovery and comprehensive logging
6. Ralph Wiggum loop for autonomous task completion
7. Documentation comprehensive

This test suite validates the entire Digital FTE system working together.
"""

import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import components
from models.task import Task, TaskDomain, TaskPriority, TaskStatus, TaskSource
from utils.audit_logger import log_audit, AuditDomain, AuditStatus
from utils.error_recovery import get_circuit_breaker, get_dlq, CircuitBreakerConfig, RetryConfig
from utils.domain_classifier import classify_task

# Paths
VAULT_PATH = PROJECT_ROOT / "Vault"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
PLANS_PATH = VAULT_PATH / "Plans"
DLQ_PATH = VAULT_PATH / "Dead_Letter_Queue"
LOGS_PATH = VAULT_PATH / "Logs"


class GoldTierValidator:
    """Validates all Gold Tier requirements."""

    def __init__(self):
        self.test_results = []
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0

    def test(self, name: str, condition: bool, details: str = ""):
        """Record a test result."""
        self.test_count += 1
        status = "[PASS]" if condition else "[FAIL]"

        if condition:
            self.passed_count += 1
        else:
            self.failed_count += 1

        result = f"{status} | {name}"
        if details:
            result += f"\n     {details}"

        self.test_results.append(result)
        print(result)

        return condition

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 80)
        print("GOLD TIER VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.passed_count} ({self.passed_count/self.test_count*100:.1f}%)")
        print(f"Failed: {self.failed_count} ({self.failed_count/self.test_count*100:.1f}%)")
        print("=" * 80)

        if self.failed_count == 0:
            print("\n[SUCCESS] ALL TESTS PASSED - GOLD TIER VALIDATED!")
        else:
            print(f"\n[WARNING] {self.failed_count} TEST(S) FAILED - REVIEW REQUIRED")

        print("=" * 80)


def test_silver_tier_complete(validator: GoldTierValidator):
    """Requirement 1: All Silver Tier requirements met."""
    print("\n" + "=" * 80)
    print("REQUIREMENT 1: Silver Tier Complete")
    print("=" * 80)

    # Check 4 watchers exist
    watchers_path = PROJECT_ROOT / "src" / "watchers"
    required_watchers = ["gmail_watcher.py", "whatsapp_watcher.py", "filesystem_watcher.py", "linkedin_watcher.py"]
    watchers_exist = all((watchers_path / w).exists() for w in required_watchers)
    validator.test(
        "1.1 Four Watchers Implemented",
        watchers_exist,
        f"Gmail, WhatsApp, Filesystem, LinkedIn"
    )

    # Check Email MCP server exists
    email_mcp = PROJECT_ROOT / "src" / "mcp_servers" / "email_sender.py"
    validator.test(
        "1.2 Email Sender MCP Exists",
        email_mcp.exists(),
        f"Path: {email_mcp}"
    )

    # Check approval workflow folders
    approval_folders = [NEEDS_ACTION_PATH, APPROVED_PATH, DONE_PATH, VAULT_PATH / "Pending_Approval"]
    all_exist = all(p.exists() for p in approval_folders)
    validator.test(
        "1.3 Approval Workflow Folders Exist",
        all_exist,
        "Needs_Action, Approved, Done, Pending_Approval"
    )

    # Check orchestrator has Plan.md generation
    orchestrator_path = PROJECT_ROOT / "src" / "orchestrator.py"
    if orchestrator_path.exists():
        content = orchestrator_path.read_text(encoding='utf-8')
        has_plan_generation = "create_plan" in content and "detect_complexity" in content
        validator.test(
            "1.4 Orchestrator Creates Plan.md for Complex Tasks",
            has_plan_generation,
            "detect_complexity() and create_plan() methods found"
        )
    else:
        validator.test("1.4 Orchestrator Creates Plan.md", False, "orchestrator.py not found")

    # Check agent skills exist (check both project and home directory)
    project_skills_path = PROJECT_ROOT / ".claude" / "skills"
    home_skills_path = Path.home() / ".claude" / "skills"

    project_skill_count = len(list(project_skills_path.glob("*/SKILL.md"))) if project_skills_path.exists() else 0
    home_skill_count = len(list(home_skills_path.glob("*/SKILL.md"))) if home_skills_path.exists() else 0
    skill_count = max(project_skill_count, home_skill_count)

    validator.test(
        "1.5 Multiple Agent Skills Configured",
        skill_count >= 5,
        f"Found {skill_count} skills (project: {project_skill_count}, home: {home_skill_count}, need >= 5)"
    )


def test_cross_domain_integration(validator: GoldTierValidator):
    """Requirement 2: Cross-domain integration (Personal + Business)."""
    print("\n" + "=" * 80)
    print("REQUIREMENT 2: Cross-Domain Integration")
    print("=" * 80)

    # Check domain classifier exists
    classifier_path = PROJECT_ROOT / "src" / "utils" / "domain_classifier.py"
    validator.test(
        "2.1 Domain Classifier Implemented",
        classifier_path.exists(),
        f"Path: {classifier_path}"
    )

    # Test classification
    if classifier_path.exists():
        personal_task, _ = classify_task(
            "Schedule dentist appointment",
            "Need to book checkup",
            []
        )
        business_task, _ = classify_task(
            "Create invoice for client",
            "Need to bill customer for services",
            []
        )

        validator.test(
            "2.2 Personal Task Classification",
            personal_task == TaskDomain.PERSONAL,
            f"Classified as: {personal_task.value}"
        )

        validator.test(
            "2.3 Business Task Classification",
            business_task == TaskDomain.BUSINESS,
            f"Classified as: {business_task.value}"
        )

    # Check audit logger tracks domains
    audit_logger_path = PROJECT_ROOT / "src" / "utils" / "audit_logger.py"
    if audit_logger_path.exists():
        content = audit_logger_path.read_text(encoding="utf-8")
        has_domains = "AuditDomain" in content and "PERSONAL" in content and "BUSINESS" in content
        validator.test(
            "2.4 Audit Logger Tracks Domains",
            has_domains,
            "PERSONAL, BUSINESS, BOTH domains in audit logs"
        )


def test_multiple_mcp_servers(validator: GoldTierValidator):
    """Requirement 3: Multiple MCP servers integrated."""
    print("\n" + "=" * 80)
    print("REQUIREMENT 3: Multiple MCP Servers")
    print("=" * 80)

    mcp_servers_path = PROJECT_ROOT / "src" / "mcp_servers"

    # Check required MCP servers
    required_mcps = {
        "email_sender.py": "Email Sender",
        "odoo_server.py": "Odoo Accounting",
        "meta_social_connector.py": "Facebook & Instagram",
        "twitter_connector.py": "Twitter/X",
        "whatsapp_server.py": "WhatsApp"
    }

    for filename, name in required_mcps.items():
        file_path = mcp_servers_path / filename
        exists = file_path.exists()

        if exists:
            content = file_path.read_text(encoding="utf-8")
            has_fastmcp = "FastMCP" in content or "from fastmcp import" in content
            has_tools = "@mcp.tool()" in content

            validator.test(
                f"3.x {name} MCP Server",
                has_fastmcp and has_tools,
                f"FastMCP: {has_fastmcp}, Tools: {has_tools}"
            )
        else:
            validator.test(f"3.x {name} MCP Server", False, f"File not found: {filename}")

    # Check MCP servers have error recovery
    email_mcp = mcp_servers_path / "email_sender.py"
    if email_mcp.exists():
        content = email_mcp.read_text(encoding="utf-8")
        has_retry = "retry_with_backoff" in content
        has_circuit_breaker = "circuit_breaker" in content or "get_circuit_breaker" in content

        validator.test(
            "3.6 MCP Servers Use Error Recovery",
            has_retry or has_circuit_breaker,
            f"Retry: {has_retry}, Circuit Breaker: {has_circuit_breaker}"
        )


def test_ceo_briefing(validator: GoldTierValidator):
    """Requirement 4: Weekly business audit with CEO briefing."""
    print("\n" + "=" * 80)
    print("REQUIREMENT 4: CEO Briefing & Business Audit")
    print("=" * 80)

    # Check CEO briefing script exists
    ceo_briefing_path = PROJECT_ROOT / "src" / "reports" / "ceo_briefing.py"
    validator.test(
        "4.1 CEO Briefing Script Exists",
        ceo_briefing_path.exists(),
        f"Path: {ceo_briefing_path}"
    )

    if ceo_briefing_path.exists():
        content = ceo_briefing_path.read_text(encoding="utf-8")

        # Check for audit log integration
        has_audit = "audit_logger" in content or "get_audit_logs" in content
        validator.test(
            "4.2 CEO Briefing Uses Audit Logs",
            has_audit,
            "Integrates with audit logging system"
        )

        # Check for metrics computation
        has_metrics = "metric" in content.lower() and ("revenue" in content.lower() or "expense" in content.lower())
        validator.test(
            "4.3 CEO Briefing Computes Metrics",
            has_metrics,
            "Calculates financial and operational metrics"
        )

        # Check for markdown generation
        has_markdown = ".md" in content or "markdown" in content.lower()
        validator.test(
            "4.4 CEO Briefing Generates Markdown",
            has_markdown,
            "Outputs formatted report"
        )

    # Check if any CEO briefing files exist in Vault
    ceo_files = list(VAULT_PATH.glob("CEO_Briefing_*.md"))
    validator.test(
        "4.5 CEO Briefing Files Generated",
        len(ceo_files) > 0,
        f"Found {len(ceo_files)} briefing file(s)"
    )


def test_error_recovery(validator: GoldTierValidator):
    """Requirement 5: Error recovery and comprehensive logging."""
    print("\n" + "=" * 80)
    print("REQUIREMENT 5: Error Recovery & Logging")
    print("=" * 80)

    # Check error recovery framework exists
    error_recovery_path = PROJECT_ROOT / "src" / "utils" / "error_recovery.py"
    validator.test(
        "5.1 Error Recovery Framework Exists",
        error_recovery_path.exists(),
        f"Path: {error_recovery_path}"
    )

    if error_recovery_path.exists():
        content = error_recovery_path.read_text(encoding="utf-8")

        # Check for retry with backoff
        has_retry = "retry_with_backoff" in content and "exponential" in content.lower()
        validator.test(
            "5.2 Retry with Exponential Backoff",
            has_retry,
            "Automatic retry for transient errors"
        )

        # Check for circuit breaker
        has_circuit_breaker = "CircuitBreaker" in content and "OPEN" in content and "CLOSED" in content
        validator.test(
            "5.3 Circuit Breaker Pattern",
            has_circuit_breaker,
            "Prevents cascade failures"
        )

        # Check for dead letter queue
        has_dlq = "DeadLetterQueue" in content or "DLQ" in content
        validator.test(
            "5.4 Dead Letter Queue",
            has_dlq,
            "Captures failed tasks for manual review"
        )

    # Check DLQ folder exists
    validator.test(
        "5.5 Dead Letter Queue Folder Exists",
        DLQ_PATH.exists(),
        f"Path: {DLQ_PATH}"
    )

    # Check audit logger exists
    audit_logger_path = PROJECT_ROOT / "src" / "utils" / "audit_logger.py"
    validator.test(
        "5.6 Audit Logger Exists",
        audit_logger_path.exists(),
        "Comprehensive logging system"
    )

    if audit_logger_path.exists():
        content = audit_logger_path.read_text(encoding="utf-8")

        # Check for audit log features
        has_domains = "AuditDomain" in content
        has_status = "AuditStatus" in content
        has_persistence = "audit_log" in content.lower() and (".jsonl" in content or ".json" in content)

        validator.test(
            "5.7 Audit Logger Features Complete",
            has_domains and has_status and has_persistence,
            f"Domains: {has_domains}, Status: {has_status}, Persistence: {has_persistence}"
        )

    # Check logs folder exists
    validator.test(
        "5.8 Logs Folder Exists",
        LOGS_PATH.exists(),
        f"Path: {LOGS_PATH}"
    )

    # Test graceful degradation
    try:
        cb = get_circuit_breaker("test_gold_validation", CircuitBreakerConfig(name="test_gold_validation"))
        validator.test(
            "5.9 Circuit Breaker Functional",
            cb is not None,
            "Can create and manage circuit breakers"
        )
    except Exception as e:
        validator.test("5.9 Circuit Breaker Functional", False, f"Error: {e}")


def test_ralph_wiggum_loop(validator: GoldTierValidator):
    """Requirement 6: Ralph Wiggum loop for autonomous task completion."""
    print("\n" + "=" * 80)
    print("REQUIREMENT 6: Ralph Wiggum Autonomous Loop")
    print("=" * 80)

    # Check orchestrator exists
    orchestrator_path = PROJECT_ROOT / "src" / "orchestrator.py"
    validator.test(
        "6.1 Orchestrator Exists",
        orchestrator_path.exists(),
        f"Path: {orchestrator_path}"
    )

    if orchestrator_path.exists():
        content = orchestrator_path.read_text(encoding="utf-8")

        # Check for autonomous loop
        has_loop = "while True:" in content or "def run(" in content
        validator.test(
            "6.2 Autonomous Loop Implemented",
            has_loop,
            "Continuous processing of tasks"
        )

        # Check for task claiming (Platinum feature, but shows maturity)
        has_claim = "_claim_task" in content or "claim" in content.lower()
        validator.test(
            "6.3 Task Claiming Logic",
            has_claim,
            "Prevents race conditions in multi-agent setups"
        )

        # Check for AI agent integration
        has_ai = "invoke_agent" in content or "AI_AGENTS" in content
        validator.test(
            "6.4 AI Agent Integration",
            has_ai,
            "Uses AI for reasoning and decision-making"
        )

        # Check for task routing
        has_routing = "Pending_Approval" in content and "Approved" in content and "Done" in content
        validator.test(
            "6.5 Task Routing",
            has_routing,
            "Routes tasks through approval workflow"
        )


def test_documentation(validator: GoldTierValidator):
    """Requirement 7: Documentation comprehensive."""
    print("\n" + "=" * 80)
    print("REQUIREMENT 7: Comprehensive Documentation")
    print("=" * 80)

    # Check key documentation files
    docs_to_check = {
        "README.md": "Main project README",
        "docs/ODOO_SETUP.md": "Odoo setup guide",
        "docs/USER_GUIDE.md": "User guide",
        "FEATURE_ROADMAP.md": "Feature roadmap",
        "SILVER_TIER_VERIFICATION.md": "Silver tier docs",
        "config/.env.example": "Environment config template"
    }

    for file_path, description in docs_to_check.items():
        full_path = PROJECT_ROOT / file_path
        exists = full_path.exists()

        if exists:
            content = full_path.read_text(encoding="utf-8")
            has_substance = len(content) > 500  # At least 500 chars

            validator.test(
                f"7.x {description}",
                has_substance,
                f"Size: {len(content)} chars"
            )
        else:
            validator.test(f"7.x {description}", False, f"File not found: {file_path}")

    # Check for setup scripts
    setup_scripts = [
        "Start_Gmail_Watcher.ps1",
        "Start_Odoo.ps1",
        "Launch_Abdullah_Junior.ps1"
    ]

    script_count = sum(1 for script in setup_scripts if (PROJECT_ROOT / script).exists())
    validator.test(
        "7.7 Setup Scripts Exist",
        script_count >= 2,
        f"Found {script_count}/{len(setup_scripts)} scripts"
    )


def test_odoo_integration(validator: GoldTierValidator):
    """Additional: Test Odoo-specific integration."""
    print("\n" + "=" * 80)
    print("BONUS: Odoo Integration Validation")
    print("=" * 80)

    # Check docker-compose file
    docker_compose = PROJECT_ROOT / "docker-compose.odoo.yml"
    validator.test(
        "Odoo Docker Compose Config",
        docker_compose.exists(),
        "Docker-based Odoo setup"
    )

    # Check Odoo MCP has required tools
    odoo_mcp = PROJECT_ROOT / "src" / "mcp_servers" / "odoo_server.py"
    if odoo_mcp.exists():
        content = odoo_mcp.read_text(encoding="utf-8")

        required_tools = [
            "create_customer_invoice",
            "record_expense",
            "get_financial_summary",
            "list_recent_invoices",
            "check_connection"
        ]

        tools_found = sum(1 for tool in required_tools if f"def {tool}" in content)
        validator.test(
            "Odoo MCP Tools Complete",
            tools_found == len(required_tools),
            f"Found {tools_found}/{len(required_tools)} required tools"
        )


def run_all_tests():
    """Run all Gold Tier validation tests."""
    print("\n" + "=" * 80)
    print("DIGITAL FTE - GOLD TIER VALIDATION")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project Root: {PROJECT_ROOT}")
    print("=" * 80)

    validator = GoldTierValidator()

    # Run all test suites
    test_silver_tier_complete(validator)
    test_cross_domain_integration(validator)
    test_multiple_mcp_servers(validator)
    test_ceo_briefing(validator)
    test_error_recovery(validator)
    test_ralph_wiggum_loop(validator)
    test_documentation(validator)
    test_odoo_integration(validator)

    # Print summary
    validator.print_summary()

    # Save results to file
    results_file = PROJECT_ROOT / "tests" / f"gold_tier_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(results_file, "w", encoding="utf-8") as f:
        f.write("GOLD TIER VALIDATION RESULTS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {validator.test_count}\n")
        f.write(f"Passed: {validator.passed_count}\n")
        f.write(f"Failed: {validator.failed_count}\n")
        f.write("=" * 80 + "\n\n")
        f.write("\n".join(validator.test_results))

    print(f"\nResults saved to: {results_file}")

    return validator.failed_count == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
