#!/usr/bin/env python3
"""Quick test for Facebook posting"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.mcp_servers.meta_social_connector import post_to_facebook

# Test post
result = post_to_facebook(
    content="Test post from Digital FTE - Phase 3 Social Media Integration complete! 🎉",
    requires_approval=True
)

print(result)
