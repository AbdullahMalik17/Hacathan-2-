"""
Demo: Follow-up Tracker
Shows how the system tracks and reminds about follow-ups.
"""

import asyncio
from datetime import datetime, timedelta

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.intelligence.followup_tracker import (
    FollowUpTracker,
    FollowUpType,
    FollowUpStatus,
    Priority
)


async def demo_basic_followups():
    """Demo basic follow-up creation and management."""
    print("\n" + "="*70)
    print("FOLLOW-UP TRACKER - BASIC OPERATIONS")
    print("="*70)

    tracker = FollowUpTracker()

    # Create various follow-ups
    print("\n[Creating] Sample follow-ups...")

    # Meeting follow-up (due in 2 days)
    meeting_followup = tracker.create_followup(
        type=FollowUpType.MEETING,
        title="Send meeting notes to team",
        description="Share notes from Q1 planning meeting",
        due_date=datetime.now() + timedelta(days=2),
        priority=Priority.HIGH,
        related_to="meeting_123",
        context={'attendees': 5, 'topics': ['Q1 goals', 'Budget']}
    )

    # Email follow-up (due today)
    email_followup = tracker.create_followup(
        type=FollowUpType.EMAIL,
        title="Reply to client proposal",
        description="Respond to John Doe's proposal request",
        due_date=datetime.now() + timedelta(hours=2),
        priority=Priority.URGENT,
        related_to="email_456"
    )

    # Task follow-up (overdue)
    task_followup = tracker.create_followup(
        type=FollowUpType.TASK,
        title="Review completed sprint tasks",
        description="Verify all sprint tasks are properly closed",
        due_date=datetime.now() - timedelta(days=1),  # Overdue
        priority=Priority.NORMAL,
        related_to="sprint_789"
    )

    print(f"[Created] {len(tracker.followups)} follow-ups")

    # Show pending follow-ups
    pending = tracker.get_pending_followups()
    print(tracker.format_followup_list(pending, "Pending Follow-ups"))

    # Show overdue
    overdue = tracker.get_overdue_followups()
    if overdue:
        print(tracker.format_followup_list(overdue, "Overdue Follow-ups"))

    # Show due today
    due_today = tracker.get_due_today()
    if due_today:
        print(tracker.format_followup_list(due_today, "Due Today"))

    # Complete a follow-up
    print("\n[Action] Completing follow-up...")
    tracker.complete_followup(meeting_followup.id)
    print(f"[Completed] {meeting_followup.title}")

    # Show stats
    stats = tracker.get_stats()
    print("\n" + "="*70)
    print("Follow-up Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Overdue: {stats['overdue']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Completion rate: {stats['completion_rate']:.1%}")
    print("="*70)


async def demo_auto_detection():
    """Demo automatic follow-up detection."""
    print("\n\n" + "="*70)
    print("AUTOMATIC FOLLOW-UP DETECTION")
    print("="*70)

    tracker = FollowUpTracker()

    print("\n[Analyzing] Recent meetings, emails, and tasks...")

    # Simulate meeting data
    meeting_data = {
        'id': 'meeting_001',
        'title': 'Weekly Team Sync',
        'date': (datetime.now() - timedelta(days=2)).isoformat(),
        'attendees': ['Alice', 'Bob', 'Charlie'],
        'has_action_items': True
    }

    # Simulate email data
    email_data = {
        'id': 'email_002',
        'sender': 'ceo@company.com',
        'subject': 'Q1 Budget Approval',
        'date': (datetime.now() - timedelta(days=1)).isoformat(),
        'importance': 'high',
        'replied': False
    }

    # Simulate task data
    task_data = {
        'id': 'task_003',
        'title': 'Complete API integration',
        'status': 'completed',
        'description': 'Integration done, follow up with testing team',
        'completed_date': datetime.now().isoformat()
    }

    # Auto-detect follow-ups
    detected = await tracker.auto_detect_followups(
        meeting_data=meeting_data,
        email_data=email_data,
        task_data=task_data
    )

    print(f"\n[Detected] {len(detected)} follow-up opportunities")

    if detected:
        print(tracker.format_followup_list(detected, "Auto-Detected Follow-ups"))


async def demo_reminders():
    """Demo reminder system."""
    print("\n\n" + "="*70)
    print("REMINDER SYSTEM")
    print("="*70)

    tracker = FollowUpTracker()

    # Create some due follow-ups
    print("\n[Creating] Follow-ups due today...")

    tracker.create_followup(
        type=FollowUpType.EMAIL,
        title="Follow up with client",
        description="Check on proposal status",
        due_date=datetime.now(),  # Due now
        priority=Priority.HIGH
    )

    tracker.create_followup(
        type=FollowUpType.MEETING,
        title="Schedule next meeting",
        description="Plan next sprint planning meeting",
        due_date=datetime.now() - timedelta(hours=1),  # Overdue
        priority=Priority.URGENT
    )

    # Send reminders
    print("\n[Sending] Reminders for due follow-ups...")
    reminded = await tracker.send_reminders()

    print(f"\n[Sent] {len(reminded)} reminders")

    # Show updated stats
    stats = tracker.get_stats()
    print("\n" + "="*70)
    print("Updated Statistics:")
    print(f"  Pending: {stats['pending']}")
    print(f"  Overdue: {stats['overdue']}")
    print("="*70)


async def demo_features_overview():
    """Demo key features of follow-up system."""
    print("\n\n" + "="*70)
    print("FOLLOW-UP TRACKER FEATURES")
    print("="*70)

    print("\nKey Features:")
    print("  1. Manual Follow-up Creation")
    print("     - Meeting follow-ups")
    print("     - Email follow-ups")
    print("     - Task follow-ups")
    print("     - Call/message follow-ups")

    print("\n  2. Automatic Detection")
    print("     - Meetings without follow-up notes")
    print("     - Important emails without replies")
    print("     - Completed tasks requiring verification")
    print("     - Action items from conversations")

    print("\n  3. Smart Reminders")
    print("     - Due today notifications")
    print("     - Overdue alerts")
    print("     - Priority-based urgency")
    print("     - Context-aware timing")

    print("\n  4. Priority Management")
    print("     - URGENT: Immediate attention")
    print("     - HIGH: Important, do today")
    print("     - NORMAL: This week")
    print("     - LOW: When available")

    print("\n  5. Context Tracking")
    print("     - Related items (meetings, emails)")
    print("     - Historical context")
    print("     - Completion tracking")
    print("     - Statistics and insights")

    print("\nIntegrations (Coming Soon):")
    print("  - Gmail API for email follow-ups")
    print("  - Google Calendar for meeting follow-ups")
    print("  - Task management systems")
    print("  - Slack/Teams notifications")


async def main():
    """Run all demos."""
    # Demo 1: Basic operations
    await demo_basic_followups()

    # Demo 2: Auto-detection
    await demo_auto_detection()

    # Demo 3: Reminders
    await demo_reminders()

    # Demo 4: Features overview
    await demo_features_overview()

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nThe Follow-up Tracker provides:")
    print("  - Never miss important follow-ups")
    print("  - Automatic detection of opportunities")
    print("  - Smart reminders at the right time")
    print("  - Priority-based organization")
    print("  - Full context for each follow-up")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
