#!/usr/bin/env python3
"""
End-to-End Test for Gold Phase Upgrade
Tests all critical workflows and integration points.
"""

import os
import sys
import time
import json
import shutil
from pathlib import Path
from datetime import datetime

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
APPROVED_PATH = VAULT_PATH / "Approved"
DONE_PATH = VAULT_PATH / "Done"
LINKEDIN_QUEUE_PATH = VAULT_PATH / "LinkedIn_Queue"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"

# Test results
test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def log(message, level="INFO"):
    """Log test message."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_vault_structure():
    """Test 1: Verify Vault directory structure exists."""
    log("Test 1: Checking Vault structure...")

    required_dirs = [
        NEEDS_ACTION_PATH,
        APPROVED_PATH,
        DONE_PATH,
        PENDING_APPROVAL_PATH,
        LINKEDIN_QUEUE_PATH,
        VAULT_PATH / "Logs"
    ]

    for path in required_dirs:
        if not path.exists():
            test_results["failed"].append(f"Missing directory: {path}")
            log(f"FAIL: Missing directory: {path}", "ERROR")
            return False

    test_results["passed"].append("Vault structure complete")
    log("PASS: Vault structure complete", "SUCCESS")
    return True

def test_skills_exist():
    """Test 2: Verify all agent skills exist."""
    log("Test 2: Checking agent skills...")

    required_skills = [
        "watching-gmail",
        "watching-whatsapp",
        "watching-filesystem",
        "digital-fte-orchestrator",
        "generating-ceo-briefing",
        "sending-emails",
        "posting-linkedin",
        "managing-services"
    ]

    skills_path = PROJECT_ROOT / ".claude" / "skills"
    missing_skills = []

    for skill in required_skills:
        skill_dir = skills_path / skill
        skill_md = skill_dir / "SKILL.md"

        if not skill_md.exists():
            missing_skills.append(skill)
            log(f"FAIL: Missing skill: {skill}", "ERROR")

    if missing_skills:
        test_results["failed"].append(f"Missing skills: {', '.join(missing_skills)}")
        return False

    test_results["passed"].append(f"All {len(required_skills)} skills exist")
    log(f"PASS: All {len(required_skills)} skills verified", "SUCCESS")
    return True

def test_linkedin_module():
    """Test 3: Verify LinkedIn module files exist."""
    log("Test 3: Checking LinkedIn module...")

    required_files = [
        PROJECT_ROOT / "src" / "linkedin" / "__init__.py",
        PROJECT_ROOT / "src" / "linkedin" / "linkedin_poster.py",
        PROJECT_ROOT / "src" / "linkedin" / "content_generator.py",
        PROJECT_ROOT / "src" / "linkedin" / "linkedin_scheduler.py",
        PROJECT_ROOT / "config" / "linkedin_config.json"
    ]

    missing_files = []
    for file_path in required_files:
        if not file_path.exists():
            missing_files.append(str(file_path))
            log(f"FAIL: Missing file: {file_path}", "ERROR")

    if missing_files:
        test_results["failed"].append(f"Missing LinkedIn files: {len(missing_files)}")
        return False

    test_results["passed"].append("LinkedIn module complete")
    log("PASS: LinkedIn module files verified", "SUCCESS")
    return True

def test_linkedin_config():
    """Test 4: Verify LinkedIn configuration is valid JSON."""
    log("Test 4: Validating LinkedIn configuration...")

    config_file = PROJECT_ROOT / "config" / "linkedin_config.json"

    try:
        with open(config_file, "r") as f:
            config = json.load(f)

        # Validate required fields
        required_fields = ["posting_schedule", "rate_limits", "approval_required"]
        for field in required_fields:
            if field not in config:
                test_results["failed"].append(f"LinkedIn config missing field: {field}")
                log(f"FAIL: Missing config field: {field}", "ERROR")
                return False

        test_results["passed"].append("LinkedIn config valid")
        log("PASS: LinkedIn configuration valid", "SUCCESS")
        return True

    except json.JSONDecodeError as e:
        test_results["failed"].append(f"Invalid LinkedIn config JSON: {e}")
        log(f"FAIL: Invalid JSON in linkedin_config.json", "ERROR")
        return False

def test_linkedin_scheduler():
    """Test 5: Test LinkedIn scheduler can run."""
    log("Test 5: Testing LinkedIn scheduler...")

    try:
        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from linkedin.linkedin_scheduler import run_scheduler

        # Run in test mode (doesn't actually schedule)
        success = run_scheduler(test_mode=True)

        if success:
            test_results["passed"].append("LinkedIn scheduler runs successfully")
            log("PASS: LinkedIn scheduler test mode", "SUCCESS")
            return True
        else:
            test_results["failed"].append("LinkedIn scheduler failed")
            log("FAIL: LinkedIn scheduler returned False", "ERROR")
            return False

    except Exception as e:
        test_results["failed"].append(f"LinkedIn scheduler error: {e}")
        log(f"FAIL: LinkedIn scheduler exception: {e}", "ERROR")
        return False

def test_service_manager():
    """Test 6: Test service manager status command."""
    log("Test 6: Testing service manager...")

    import subprocess

    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "src" / "service_manager.py"), "--status"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # Verify all skills listed in output
            output = result.stdout
            skills = ["watching-gmail", "watching-filesystem", "watching-whatsapp", "digital-fte-orchestrator"]

            for skill in skills:
                if skill not in output:
                    test_results["warnings"].append(f"Skill {skill} not in service manager")
                    log(f"WARN: Skill {skill} not listed in service manager", "WARNING")

            test_results["passed"].append("Service manager status command works")
            log("PASS: Service manager --status command", "SUCCESS")
            return True
        else:
            test_results["failed"].append(f"Service manager failed with code {result.returncode}")
            log(f"FAIL: Service manager exited with code {result.returncode}", "ERROR")
            return False

    except Exception as e:
        test_results["failed"].append(f"Service manager error: {e}")
        log(f"FAIL: Service manager exception: {e}", "ERROR")
        return False

def test_orchestrator_imports():
    """Test 7: Test orchestrator can be imported."""
    log("Test 7: Testing orchestrator imports...")

    try:
        sys.path.insert(0, str(PROJECT_ROOT / "src"))
        from orchestrator import DigitalFTEOrchestrator

        # Create instance (doesn't start loop)
        orch = DigitalFTEOrchestrator(max_iterations=1, poll_interval=1, dry_run=True)

        test_results["passed"].append("Orchestrator imports and initializes")
        log("PASS: Orchestrator can be imported and initialized", "SUCCESS")
        return True

    except Exception as e:
        test_results["failed"].append(f"Orchestrator import error: {e}")
        log(f"FAIL: Orchestrator import exception: {e}", "ERROR")
        return False

def test_task_file_workflow():
    """Test 8: Test task file workflow (create → detect)."""
    log("Test 8: Testing task file workflow...")

    # Create test task file
    test_file = NEEDS_ACTION_PATH / f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"

    try:
        with open(test_file, "w") as f:
            f.write("---\n")
            f.write("source: e2e_test\n")
            f.write("priority: low\n")
            f.write("---\n\n")
            f.write("# Test Task\n\n")
            f.write("This is an automated test task.\n")

        # Verify file exists
        if not test_file.exists():
            test_results["failed"].append("Could not create test task file")
            log("FAIL: Test task file not created", "ERROR")
            return False

        # Verify can be read
        content = test_file.read_text()
        if "Test Task" not in content:
            test_results["failed"].append("Test task file content invalid")
            log("FAIL: Test task file content invalid", "ERROR")
            return False

        # Clean up
        test_file.unlink()

        test_results["passed"].append("Task file workflow works")
        log("PASS: Task file create/read workflow", "SUCCESS")
        return True

    except Exception as e:
        # Clean up on error
        if test_file.exists():
            test_file.unlink()

        test_results["failed"].append(f"Task workflow error: {e}")
        log(f"FAIL: Task workflow exception: {e}", "ERROR")
        return False

def print_summary():
    """Print test summary."""
    log("")
    log("=" * 60)
    log("TEST SUMMARY")
    log("=" * 60)

    total_tests = len(test_results["passed"]) + len(test_results["failed"])
    log(f"Total Tests: {total_tests}")
    log(f"Passed: {len(test_results['passed'])}")
    log(f"Failed: {len(test_results['failed'])}")
    log(f"Warnings: {len(test_results['warnings'])}")

    if test_results["failed"]:
        log("")
        log("FAILED TESTS:", "ERROR")
        for failure in test_results["failed"]:
            log(f"  - {failure}", "ERROR")

    if test_results["warnings"]:
        log("")
        log("WARNINGS:", "WARNING")
        for warning in test_results["warnings"]:
            log(f"  - {warning}", "WARNING")

    log("=" * 60)

    # Return exit code
    return 0 if len(test_results["failed"]) == 0 else 1

def main():
    """Run all tests."""
    log("Starting End-to-End Gold Phase Tests")
    log("=" * 60)

    tests = [
        test_vault_structure,
        test_skills_exist,
        test_linkedin_module,
        test_linkedin_config,
        test_linkedin_scheduler,
        test_service_manager,
        test_orchestrator_imports,
        test_task_file_workflow
    ]

    for test in tests:
        try:
            test()
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            log(f"CRITICAL: Test crashed: {e}", "ERROR")
            test_results["failed"].append(f"Test crashed: {test.__name__}")

    return print_summary()

if __name__ == "__main__":
    sys.exit(main())
