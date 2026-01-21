import os
import sys
import json
import subprocess
import shutil
import re
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

# Default settings
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Multi-agent fallback configuration
AI_AGENTS = [
    {
        "name": "gemini",
        "commands": [
            "gemini",
            "gemini.cmd",
            os.path.expandvars(r"%APPDATA%\\npm\\gemini.cmd"),
        ],
        "prompt_flag": "-p",
        "enabled": True
    },
    {
        "name": "claude",
        "commands": [
            "claude",
            "claude.cmd",
            os.path.expandvars(r"%APPDATA%\\npm\\claude.cmd"),
        ],
        "prompt_flag": "-p",
        "enabled": True
    },
    {
        "name": "codex",
        "commands": [
            "codex",
            "openai-codex",
        ],
        "prompt_flag": "-p",
        "enabled": True
    }
]

logger = logging.getLogger("AIAgentUtil")

def find_available_agents():
    """Find all available AI agents on the system."""
    available = []

    for agent in AI_AGENTS:
        if not agent["enabled"]:
            continue

        for cmd in agent["commands"]:
            cmd_path = shutil.which(cmd)
            if cmd_path:
                available.append({
                    "name": agent["name"],
                    "command": cmd_path,
                    "prompt_flag": agent["prompt_flag"]
                })
                break
            elif os.path.exists(cmd):
                available.append({
                    "name": agent["name"],
                    "command": cmd,
                    "prompt_flag": agent["prompt_flag"]
                })
                break
    return available

def invoke_agent(prompt: str, dry_run: bool = False) -> tuple[bool, str, str]:
    """
    Invoke an AI agent and return the response.
    Returns: (success, output_text, agent_name)
    """
    if dry_run:
        return True, "Dry run response", "dry_run"

    available_agents = find_available_agents()
    if not available_agents:
        logger.error("No agents available.")
        return False, "", "none"

    for ai_agent in available_agents:
        agent_name = ai_agent["name"]
        command = ai_agent["command"]
        prompt_flag = ai_agent["prompt_flag"]

        try:
            logger.info(f"Invoking {agent_name.upper()}...")
            
            cmd = [command, prompt]
            if prompt_flag:
                cmd = [command, prompt_flag, prompt]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(PROJECT_ROOT),
                shell=(os.name == 'nt'),
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                return True, output, agent_name
            else:
                logger.warning(f"{agent_name.upper()} failed (code {result.returncode})")

        except Exception as e:
            logger.warning(f"{agent_name.upper()} error: {e}")

    return False, "", "all_failed"
