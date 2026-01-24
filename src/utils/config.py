"""
Platinum Tier Configuration Module

Provides work-zone aware configuration loading for dual-agent architecture.
Supports CLOUD (draft-only) and LOCAL (full execution) work-zones.

Usage:
    from src.utils.config import load_config, WorkZone

    config = load_config()
    if config["work_zone"] == WorkZone.CLOUD:
        # Draft-only mode
        pass
"""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    # dotenv not installed, define a no-op function
    def load_dotenv(*args, **kwargs):
        pass


class WorkZone(Enum):
    """
    Work-zone enumeration for dual-agent architecture.

    CLOUD: Draft-only mode (24/7 VM)
        - Cannot execute sensitive actions
        - No MCP credentials
        - Creates drafts for human review

    LOCAL: Full execution mode (user's machine)
        - Can execute all actions
        - Has all MCP credentials
        - Approves and executes drafts
    """
    CLOUD = "cloud"
    LOCAL = "local"


class ConfigError(Exception):
    """Configuration error."""
    pass


def get_project_root() -> Path:
    """Get the project root directory."""
    # Navigate from src/utils/config.py to project root
    return Path(__file__).parent.parent.parent


def load_config(env_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load environment configuration based on WORK_ZONE.

    Args:
        env_path: Optional path to .env file. If not provided,
                  loads from project root .env or config/.env

    Returns:
        Dictionary with configuration values including:
        - work_zone: WorkZone enum
        - agent_id: Unique agent identifier
        - vault_path: Path to Obsidian vault
        - git settings
        - watcher settings
        - mcp settings
        - logging settings

    Raises:
        ConfigError: If required configuration is missing
    """
    # Load .env file
    if env_path:
        load_dotenv(env_path)
    else:
        # Try multiple locations
        project_root = get_project_root()
        env_locations = [
            project_root / ".env",
            project_root / "config" / ".env",
        ]

        for loc in env_locations:
            if loc.exists():
                load_dotenv(loc)
                break
        else:
            # No .env found, rely on environment variables
            pass

    # Parse work-zone
    work_zone_str = os.getenv("WORK_ZONE", "local").lower()
    try:
        work_zone = WorkZone(work_zone_str)
    except ValueError:
        # Default to local if invalid
        work_zone = WorkZone.LOCAL

    # Build configuration dictionary
    config = {
        # Work-zone configuration
        "work_zone": work_zone,
        "agent_id": os.getenv("AGENT_ID", f"{work_zone.value}-agent-001"),
        "agent_name": os.getenv("AGENT_NAME", f"{work_zone.value.title()} Agent"),

        # Vault & Git
        "vault_path": Path(os.getenv("VAULT_PATH", str(get_project_root() / "Vault"))),
        "git_remote": os.getenv("GIT_REMOTE", ""),
        "git_sync_interval": int(os.getenv("GIT_SYNC_INTERVAL", "30")),

        # Watchers
        "watchers": {
            "gmail": {
                "enabled": os.getenv("GMAIL_ENABLED", "false").lower() == "true",
                "poll_interval": int(os.getenv("GMAIL_POLL_INTERVAL", "300")),
            },
            "whatsapp": {
                "enabled": os.getenv("WHATSAPP_ENABLED", "false").lower() == "true",
                "poll_interval": int(os.getenv("WHATSAPP_POLL_INTERVAL", "60")),
            },
            "linkedin": {
                "enabled": os.getenv("LINKEDIN_ENABLED", "false").lower() == "true",
                "poll_interval": int(os.getenv("LINKEDIN_POLL_INTERVAL", "600")),
            },
            "filesystem": {
                "enabled": os.getenv("FILESYSTEM_ENABLED", "false").lower() == "true",
                "watch_path": os.getenv("FILESYSTEM_WATCH_PATH", ""),
            },
        },

        # MCP Servers
        "mcp_servers": {
            "email": {
                "enabled": os.getenv("EMAIL_MCP_ENABLED", "false").lower() == "true",
            },
            "odoo": {
                "enabled": os.getenv("ODOO_MCP_ENABLED", "false").lower() == "true",
                "url": os.getenv("ODOO_URL", ""),
                "db": os.getenv("ODOO_DB", ""),
                "username": os.getenv("ODOO_USERNAME", ""),
                "password": os.getenv("ODOO_PASSWORD", ""),
            },
            "meta_social": {
                "enabled": os.getenv("META_SOCIAL_MCP_ENABLED", "false").lower() == "true",
            },
            "twitter": {
                "enabled": os.getenv("TWITTER_MCP_ENABLED", "false").lower() == "true",
            },
            "whatsapp": {
                "enabled": os.getenv("WHATSAPP_MCP_ENABLED", "false").lower() == "true",
            },
        },

        # Orchestrator
        "max_concurrent_tasks": int(os.getenv("MAX_CONCURRENT_TASKS", "5")),
        "task_timeout": int(os.getenv("TASK_TIMEOUT", "300")),
        "poll_interval": int(os.getenv("POLL_INTERVAL", "30")),
        "max_iterations": int(os.getenv("MAX_ITERATIONS", "10")),

        # Rate limits
        "rate_limits": {
            "emails_per_hour": int(os.getenv("RATE_LIMIT_EMAILS_HOUR", "10")),
            "payments_per_hour": int(os.getenv("RATE_LIMIT_PAYMENTS_HOUR", "3")),
            "social_per_day": int(os.getenv("RATE_LIMIT_SOCIAL_DAY", "5")),
        },

        # Security
        "max_auto_approve_amount": float(os.getenv("MAX_AUTO_APPROVE_AMOUNT", "100")),
        "require_approval_new_recipients": os.getenv("REQUIRE_APPROVAL_NEW_RECIPIENTS", "true").lower() == "true",
        "dry_run": os.getenv("DRY_RUN", "false").lower() == "true",

        # Logging
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "audit_log_path": Path(os.getenv("AUDIT_LOG_PATH", str(get_project_root() / "Vault" / "Logs" / "audit"))),
        "health_log_path": Path(os.getenv("HEALTH_LOG_PATH", str(get_project_root() / "Vault" / "Logs" / "health"))),

        # Resources
        "memory_limit_mb": int(os.getenv("MEMORY_LIMIT_MB", "8192")),

        # AI
        "ai_model": os.getenv("AI_MODEL", "gemini-2.0-flash"),
    }

    return config


def get_work_zone() -> WorkZone:
    """
    Get current work-zone from environment.

    Returns:
        WorkZone enum (CLOUD or LOCAL)
    """
    work_zone_str = os.getenv("WORK_ZONE", "local").lower()
    try:
        return WorkZone(work_zone_str)
    except ValueError:
        return WorkZone.LOCAL


def is_cloud_mode() -> bool:
    """Check if running in cloud (draft-only) mode."""
    return get_work_zone() == WorkZone.CLOUD


def is_local_mode() -> bool:
    """Check if running in local (full execution) mode."""
    return get_work_zone() == WorkZone.LOCAL


def validate_config(config: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate configuration for consistency.

    Args:
        config: Configuration dictionary from load_config()

    Returns:
        (is_valid, list of errors)
    """
    errors = []

    # Check work-zone specific requirements
    if config["work_zone"] == WorkZone.CLOUD:
        # Cloud should NOT have MCP credentials enabled
        for mcp_name, mcp_config in config["mcp_servers"].items():
            if mcp_config.get("enabled", False):
                errors.append(f"MCP server '{mcp_name}' should be disabled in CLOUD work-zone")

    elif config["work_zone"] == WorkZone.LOCAL:
        # Local should have vault path accessible
        if not config["vault_path"].exists():
            errors.append(f"Vault path does not exist: {config['vault_path']}")

    # Common validations
    if not config["agent_id"]:
        errors.append("AGENT_ID is required")

    if config["git_sync_interval"] < 10:
        errors.append("GIT_SYNC_INTERVAL should be at least 10 seconds")

    return len(errors) == 0, errors


def print_config_summary(config: Dict[str, Any]) -> None:
    """Print a summary of the current configuration."""
    print("=" * 60)
    print("DIGITAL FTE CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Work-Zone:     {config['work_zone'].value.upper()}")
    print(f"Agent ID:      {config['agent_id']}")
    print(f"Agent Name:    {config['agent_name']}")
    print(f"Vault Path:    {config['vault_path']}")
    print(f"Dry Run:       {config['dry_run']}")
    print("-" * 60)
    print("WATCHERS:")
    for name, watcher in config["watchers"].items():
        status = "ENABLED" if watcher["enabled"] else "disabled"
        print(f"  {name:12} {status}")
    print("-" * 60)
    print("MCP SERVERS:")
    for name, mcp in config["mcp_servers"].items():
        status = "ENABLED" if mcp.get("enabled", False) else "disabled"
        print(f"  {name:12} {status}")
    print("=" * 60)


if __name__ == "__main__":
    # Test configuration loading
    print("Testing Configuration Module...")

    # Test default (local) mode
    print("\n1. Testing LOCAL mode (default)...")
    os.environ["WORK_ZONE"] = "local"
    config = load_config()
    print(f"   Work-zone: {config['work_zone']}")
    assert config["work_zone"] == WorkZone.LOCAL
    print("   [OK] Local mode loaded correctly")

    # Test cloud mode
    print("\n2. Testing CLOUD mode...")
    os.environ["WORK_ZONE"] = "cloud"
    config = load_config()
    print(f"   Work-zone: {config['work_zone']}")
    assert config["work_zone"] == WorkZone.CLOUD
    print("   [OK] Cloud mode loaded correctly")

    # Test helper functions
    print("\n3. Testing helper functions...")
    assert is_cloud_mode() == True
    os.environ["WORK_ZONE"] = "local"
    assert is_local_mode() == True
    print("   [OK] Helper functions work correctly")

    # Test invalid work-zone
    print("\n4. Testing invalid work-zone (should default to local)...")
    os.environ["WORK_ZONE"] = "invalid"
    config = load_config()
    assert config["work_zone"] == WorkZone.LOCAL
    print("   [OK] Invalid work-zone defaults to LOCAL")

    # Print config summary
    print("\n5. Configuration summary:")
    os.environ["WORK_ZONE"] = "local"
    config = load_config()
    print_config_summary(config)

    print("\n[SUCCESS] All configuration tests passed!")
