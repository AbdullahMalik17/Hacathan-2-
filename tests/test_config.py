"""
Tests for Platinum Tier Configuration Module

Tests work-zone configuration loading for dual-agent architecture.
"""

import os
import pytest
from pathlib import Path
import tempfile


# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import (
    WorkZone,
    load_config,
    get_work_zone,
    is_cloud_mode,
    is_local_mode,
    validate_config,
)


class TestWorkZoneEnum:
    """Tests for WorkZone enumeration."""

    def test_cloud_value(self):
        """Cloud work-zone should have correct value."""
        assert WorkZone.CLOUD.value == "cloud"

    def test_local_value(self):
        """Local work-zone should have correct value."""
        assert WorkZone.LOCAL.value == "local"

    def test_from_string_cloud(self):
        """Should create CLOUD from string."""
        assert WorkZone("cloud") == WorkZone.CLOUD

    def test_from_string_local(self):
        """Should create LOCAL from string."""
        assert WorkZone("local") == WorkZone.LOCAL

    def test_invalid_value_raises(self):
        """Invalid value should raise ValueError."""
        with pytest.raises(ValueError):
            WorkZone("invalid")


class TestLoadConfig:
    """Tests for configuration loading."""

    def test_default_work_zone_is_local(self, monkeypatch):
        """Default work-zone should be local."""
        monkeypatch.delenv("WORK_ZONE", raising=False)
        config = load_config()
        assert config["work_zone"] == WorkZone.LOCAL

    def test_cloud_work_zone_from_env(self, monkeypatch):
        """Should load CLOUD work-zone from environment."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        config = load_config()
        assert config["work_zone"] == WorkZone.CLOUD

    def test_local_work_zone_from_env(self, monkeypatch):
        """Should load LOCAL work-zone from environment."""
        monkeypatch.setenv("WORK_ZONE", "local")
        config = load_config()
        assert config["work_zone"] == WorkZone.LOCAL

    def test_invalid_work_zone_defaults_to_local(self, monkeypatch):
        """Invalid work-zone should default to LOCAL."""
        monkeypatch.setenv("WORK_ZONE", "invalid_value")
        config = load_config()
        assert config["work_zone"] == WorkZone.LOCAL

    def test_case_insensitive_work_zone(self, monkeypatch):
        """Work-zone should be case insensitive."""
        monkeypatch.setenv("WORK_ZONE", "CLOUD")
        config = load_config()
        assert config["work_zone"] == WorkZone.CLOUD

        monkeypatch.setenv("WORK_ZONE", "Cloud")
        config = load_config()
        assert config["work_zone"] == WorkZone.CLOUD

    def test_agent_id_from_env(self, monkeypatch):
        """Should load agent ID from environment."""
        monkeypatch.setenv("AGENT_ID", "test-agent-123")
        config = load_config()
        assert config["agent_id"] == "test-agent-123"

    def test_default_agent_id(self, monkeypatch):
        """Should generate default agent ID based on work-zone."""
        monkeypatch.delenv("AGENT_ID", raising=False)
        monkeypatch.setenv("WORK_ZONE", "cloud")
        config = load_config()
        assert "cloud" in config["agent_id"]

    def test_vault_path_from_env(self, monkeypatch):
        """Should load vault path from environment."""
        test_path = "/test/vault/path"
        monkeypatch.setenv("VAULT_PATH", test_path)
        config = load_config()
        assert config["vault_path"] == Path(test_path)

    def test_git_sync_interval_from_env(self, monkeypatch):
        """Should load git sync interval from environment."""
        monkeypatch.setenv("GIT_SYNC_INTERVAL", "60")
        config = load_config()
        assert config["git_sync_interval"] == 60

    def test_watchers_config(self, monkeypatch):
        """Should load watcher configuration."""
        monkeypatch.setenv("GMAIL_ENABLED", "true")
        monkeypatch.setenv("GMAIL_POLL_INTERVAL", "120")
        monkeypatch.setenv("WHATSAPP_ENABLED", "false")

        config = load_config()

        assert config["watchers"]["gmail"]["enabled"] == True
        assert config["watchers"]["gmail"]["poll_interval"] == 120
        assert config["watchers"]["whatsapp"]["enabled"] == False

    def test_mcp_servers_config(self, monkeypatch):
        """Should load MCP server configuration."""
        monkeypatch.setenv("EMAIL_MCP_ENABLED", "true")
        monkeypatch.setenv("ODOO_MCP_ENABLED", "false")

        config = load_config()

        assert config["mcp_servers"]["email"]["enabled"] == True
        assert config["mcp_servers"]["odoo"]["enabled"] == False

    def test_rate_limits_config(self, monkeypatch):
        """Should load rate limit configuration."""
        monkeypatch.setenv("RATE_LIMIT_EMAILS_HOUR", "20")
        monkeypatch.setenv("RATE_LIMIT_PAYMENTS_HOUR", "5")

        config = load_config()

        assert config["rate_limits"]["emails_per_hour"] == 20
        assert config["rate_limits"]["payments_per_hour"] == 5

    def test_dry_run_config(self, monkeypatch):
        """Should load dry run configuration."""
        monkeypatch.setenv("DRY_RUN", "true")
        config = load_config()
        assert config["dry_run"] == True

        monkeypatch.setenv("DRY_RUN", "false")
        config = load_config()
        assert config["dry_run"] == False


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_work_zone_cloud(self, monkeypatch):
        """get_work_zone should return CLOUD when set."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        assert get_work_zone() == WorkZone.CLOUD

    def test_get_work_zone_local(self, monkeypatch):
        """get_work_zone should return LOCAL when set."""
        monkeypatch.setenv("WORK_ZONE", "local")
        assert get_work_zone() == WorkZone.LOCAL

    def test_get_work_zone_default(self, monkeypatch):
        """get_work_zone should default to LOCAL."""
        monkeypatch.delenv("WORK_ZONE", raising=False)
        assert get_work_zone() == WorkZone.LOCAL

    def test_is_cloud_mode(self, monkeypatch):
        """is_cloud_mode should return True only in cloud mode."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        assert is_cloud_mode() == True
        assert is_local_mode() == False

    def test_is_local_mode(self, monkeypatch):
        """is_local_mode should return True only in local mode."""
        monkeypatch.setenv("WORK_ZONE", "local")
        assert is_local_mode() == True
        assert is_cloud_mode() == False


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_cloud_mode_with_mcp_enabled_is_invalid(self, monkeypatch):
        """Cloud mode should not have MCP servers enabled."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("EMAIL_MCP_ENABLED", "true")

        config = load_config()
        is_valid, errors = validate_config(config)

        assert is_valid == False
        assert any("MCP server" in e for e in errors)

    def test_cloud_mode_with_mcp_disabled_is_valid(self, monkeypatch):
        """Cloud mode with all MCP disabled should be valid."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("EMAIL_MCP_ENABLED", "false")
        monkeypatch.setenv("ODOO_MCP_ENABLED", "false")
        monkeypatch.setenv("META_SOCIAL_MCP_ENABLED", "false")
        monkeypatch.setenv("TWITTER_MCP_ENABLED", "false")
        monkeypatch.setenv("WHATSAPP_MCP_ENABLED", "false")
        monkeypatch.setenv("AGENT_ID", "test-agent")
        monkeypatch.setenv("GIT_SYNC_INTERVAL", "30")

        config = load_config()
        is_valid, errors = validate_config(config)

        assert is_valid == True
        assert len(errors) == 0

    def test_missing_agent_id_is_invalid(self, monkeypatch):
        """Missing agent ID should be invalid."""
        monkeypatch.setenv("WORK_ZONE", "local")
        monkeypatch.setenv("AGENT_ID", "")

        config = load_config()
        # Force empty agent_id
        config["agent_id"] = ""
        is_valid, errors = validate_config(config)

        assert is_valid == False
        assert any("AGENT_ID" in e for e in errors)

    def test_low_sync_interval_is_invalid(self, monkeypatch):
        """Sync interval less than 10 seconds should be invalid."""
        monkeypatch.setenv("WORK_ZONE", "local")
        monkeypatch.setenv("GIT_SYNC_INTERVAL", "5")
        monkeypatch.setenv("AGENT_ID", "test-agent")

        config = load_config()
        is_valid, errors = validate_config(config)

        assert is_valid == False
        assert any("GIT_SYNC_INTERVAL" in e for e in errors)


class TestCloudVsLocalConfig:
    """Tests for Cloud vs Local configuration differences."""

    def test_cloud_config_no_credentials(self, monkeypatch):
        """Cloud config should not have MCP enabled."""
        monkeypatch.setenv("WORK_ZONE", "cloud")
        # Simulate cloud environment (no credentials)
        monkeypatch.setenv("EMAIL_MCP_ENABLED", "false")
        monkeypatch.setenv("ODOO_MCP_ENABLED", "false")

        config = load_config()

        assert config["work_zone"] == WorkZone.CLOUD
        assert config["mcp_servers"]["email"]["enabled"] == False
        assert config["mcp_servers"]["odoo"]["enabled"] == False

    def test_local_config_with_credentials(self, monkeypatch):
        """Local config should have MCP enabled."""
        monkeypatch.setenv("WORK_ZONE", "local")
        monkeypatch.setenv("EMAIL_MCP_ENABLED", "true")
        monkeypatch.setenv("ODOO_MCP_ENABLED", "true")
        monkeypatch.setenv("ODOO_URL", "http://localhost:8069")

        config = load_config()

        assert config["work_zone"] == WorkZone.LOCAL
        assert config["mcp_servers"]["email"]["enabled"] == True
        assert config["mcp_servers"]["odoo"]["enabled"] == True

    def test_cloud_watchers_vs_local_watchers(self, monkeypatch):
        """Cloud and Local should have different watcher configurations."""
        # Cloud: Gmail enabled, Filesystem disabled
        monkeypatch.setenv("WORK_ZONE", "cloud")
        monkeypatch.setenv("GMAIL_ENABLED", "true")
        monkeypatch.setenv("FILESYSTEM_ENABLED", "false")

        cloud_config = load_config()
        assert cloud_config["watchers"]["gmail"]["enabled"] == True
        assert cloud_config["watchers"]["filesystem"]["enabled"] == False

        # Local: Gmail disabled, Filesystem enabled
        monkeypatch.setenv("WORK_ZONE", "local")
        monkeypatch.setenv("GMAIL_ENABLED", "false")
        monkeypatch.setenv("FILESYSTEM_ENABLED", "true")

        local_config = load_config()
        assert local_config["watchers"]["gmail"]["enabled"] == False
        assert local_config["watchers"]["filesystem"]["enabled"] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
