#!/usr/bin/env python3
"""
Test Social Media Posting with Approval Workflow
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment
PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / "config" / ".env")

# Setup paths
VAULT_PATH = PROJECT_ROOT / "Vault"
PENDING_PATH = VAULT_PATH / "Pending_Approval"
PENDING_PATH.mkdir(parents=True, exist_ok=True)

def create_facebook_approval(content: str, link: str = None) -> str:
    """Create Facebook post approval file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"Facebook_{timestamp}_post.md"
    filepath = PENDING_PATH / filename

    # Create approval file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write("platform: Facebook\n")
        f.write(f"scheduled_for: {datetime.now().isoformat()}\n")
        f.write("priority: medium\n")
        f.write("---\n\n")
        f.write(f"# Facebook Post\n\n")
        f.write(f"**Content:**\n{content}\n\n")
        if link:
            f.write(f"**Link:** {link}\n\n")
        f.write("---\n\n")
        f.write("## Approval Instructions\n\n")
        f.write("- [APPROVE] Move to `Vault/Approved/` to post\n")
        f.write("- [REJECT] Delete this file to cancel\n")

    return str(filepath)

def create_twitter_approval(content: str) -> str:
    """Create Twitter post approval file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"Twitter_{timestamp}_tweet.md"
    filepath = PENDING_PATH / filename

    # Validate length
    char_count = len(content)
    if char_count > 280:
        return f"Error: Tweet too long ({char_count}/280 characters)"

    # Create approval file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("---\n")
        f.write("platform: Twitter\n")
        f.write(f"scheduled_for: {datetime.now().isoformat()}\n")
        f.write("priority: medium\n")
        f.write(f"character_count: {char_count}\n")
        f.write("---\n\n")
        f.write(f"# Twitter Post\n\n")
        f.write(f"**Tweet:**\n{content}\n\n")
        f.write(f"*({char_count}/280 characters)*\n\n")
        f.write("---\n\n")
        f.write("## Approval Instructions\n\n")
        f.write("- [APPROVE] Move to `Vault/Approved/` to post\n")
        f.write("- [REJECT] Delete this file to cancel\n")

    return str(filepath)

def main():
    print("\n" + "="*60)
    print("  TESTING SOCIAL MEDIA POSTING WORKFLOW")
    print("="*60 + "\n")

    # Test 1: Facebook Post
    print("[1] Testing Facebook posting with approval...")
    fb_content = """Exciting Update from Digital FTE!

Phase 3 of our Gold Tier upgrade is complete! We now have full social media integration:
- Facebook posting automation
- Instagram content management
- Twitter/X integration
- Odoo accounting system

Building the future of AI-powered business operations, one module at a time!

#AI #Automation #DigitalTransformation"""

    try:
        fb_file = create_facebook_approval(fb_content)
        print(f"[OK] Facebook approval created: {fb_file}")
        print(f"     Content preview: {fb_content[:80]}...")
    except Exception as e:
        print(f"[ERROR] Facebook test failed: {e}")

    # Test 2: Twitter Post
    print("\n[2] Testing Twitter posting with approval...")
    twitter_content = "Digital FTE Phase 3 complete! Now featuring Facebook, Instagram, Twitter automation + Odoo accounting. The future of AI-powered business ops is here! #AI #Automation"

    try:
        tw_file = create_twitter_approval(twitter_content)
        if tw_file.startswith("Error:"):
            print(f"[ERROR] {tw_file}")
        else:
            print(f"[OK] Twitter approval created: {tw_file}")
            print(f"     Content: {twitter_content}")
            print(f"     Length: {len(twitter_content)}/280 characters")
    except Exception as e:
        print(f"[ERROR] Twitter test failed: {e}")

    # Summary
    print("\n" + "="*60)
    print("  NEXT STEPS")
    print("="*60 + "\n")
    print("[OK] Approval files created in: Vault/Pending_Approval/")
    print("\nTo approve and post:")
    print("  1. Review the content in each approval file")
    print("  2. Move approved files to Vault/Approved/")
    print("  3. Or delete files to cancel")
    print("\nNote: This is the approval workflow - actual posting")
    print("      to social media happens when files are approved.")
    print()

if __name__ == "__main__":
    main()
