"""
Demo: Daily Digest - Morning Briefings and Evening Summaries
Shows how the system generates personalized digests.
"""

import asyncio
from datetime import datetime

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.intelligence.daily_digest import DailyDigestGenerator, DigestType
from src.storage.learning_db import LearningDatabase


async def demo_morning_briefing():
    """Demo morning briefing generation."""
    print("\n" + "="*70)
    print("MORNING BRIEFING DEMO")
    print("="*70)
    print("\nGenerating personalized morning briefing...")

    # Initialize
    db = LearningDatabase("Vault/Data/learning_demo.db")
    generator = DailyDigestGenerator(
        email_service=None,  # Would be Gmail API
        calendar_service=None,  # Would be Google Calendar API
        task_manager=None,  # Would be task management system
        learning_db=db
    )

    # Generate morning briefing
    briefing = await generator.generate_morning_briefing()

    # Format and display
    print("\n" + generator.format_digest(briefing))

    # Show metadata
    print("\nDigest Metadata:")
    digest_dict = briefing.to_dict()
    print(f"  Type: {digest_dict['type']}")
    print(f"  Total items: {digest_dict['total_items']}")
    print(f"  Action count: {digest_dict['action_count']}")
    print(f"  Categories: {', '.join(briefing.metadata.get('categories', []))}")

    # Cleanup
    db.close()


async def demo_evening_summary():
    """Demo evening summary generation."""
    print("\n" + "="*70)
    print("EVENING SUMMARY DEMO")
    print("="*70)
    print("\nGenerating end-of-day summary...")

    # Initialize
    db = LearningDatabase("Vault/Data/learning_demo.db")
    generator = DailyDigestGenerator(
        email_service=None,
        calendar_service=None,
        task_manager=None,
        learning_db=db
    )

    # Generate evening summary
    summary = await generator.generate_evening_summary()

    # Format and display
    print("\n" + generator.format_digest(summary))

    # Show metadata
    print("\nDigest Metadata:")
    digest_dict = summary.to_dict()
    print(f"  Type: {digest_dict['type']}")
    print(f"  Total items: {digest_dict['total_items']}")
    print(f"  Action count: {digest_dict['action_count']}")
    print(f"  Categories: {', '.join(summary.metadata.get('categories', []))}")

    # Cleanup
    db.close()


async def demo_digest_features():
    """Demo key features of digest system."""
    print("\n" + "="*70)
    print("DAILY DIGEST FEATURES")
    print("="*70)

    print("\nKey Features:")
    print("  1. Morning Briefings (8-9am)")
    print("     - Urgent emails and notifications")
    print("     - Today's calendar preview")
    print("     - Priority tasks for the day")
    print("     - Follow-ups due today")

    print("\n  2. Evening Summaries (5-6pm)")
    print("     - Today's accomplishments")
    print("     - Pending items")
    print("     - Tomorrow's preview")
    print("     - Follow-up opportunities")

    print("\n  3. Smart Categorization")
    print("     - Items grouped by category")
    print("     - Priority-based sorting")
    print("     - Action items highlighted")

    print("\n  4. Context-Aware")
    print("     - Friday includes weekly wrap-up")
    print("     - Learns from patterns")
    print("     - Adapts to user preferences")

    print("\n  5. Integrations (Coming Soon)")
    print("     - Gmail API for email analysis")
    print("     - Google Calendar for events")
    print("     - Task management systems")
    print("     - Follow-up tracker")

    print("\nDelivery Options:")
    print("  - Terminal notification")
    print("  - Email digest")
    print("  - Mobile notification")
    print("  - Desktop notification")


async def main():
    """Run all demos."""
    # Demo 1: Morning briefing
    await demo_morning_briefing()

    print("\n\n")

    # Demo 2: Evening summary
    await demo_evening_summary()

    print("\n\n")

    # Demo 3: Features overview
    await demo_digest_features()

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nThe Daily Digest system provides:")
    print("  - Automated morning briefings")
    print("  - End-of-day summaries")
    print("  - Smart prioritization")
    print("  - Context-aware content")
    print("  - Actionable insights")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
