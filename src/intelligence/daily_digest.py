"""
Daily Digest Generator - Morning briefings and evening summaries.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class DigestType(Enum):
    """Type of digest."""
    MORNING_BRIEFING = "morning"
    EVENING_SUMMARY = "evening"
    CUSTOM = "custom"


class Priority(Enum):
    """Priority levels for digest items."""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class DigestItem:
    """Single item in a digest."""
    category: str
    title: str
    description: str
    priority: Priority
    action_required: bool
    deadline: Optional[datetime]
    metadata: Dict[str, Any]

    def __str__(self) -> str:
        """Format item for display."""
        priority_marker = {
            Priority.URGENT: "[URGENT]",
            Priority.HIGH: "[HIGH]",
            Priority.NORMAL: "",
            Priority.LOW: "[LOW]"
        }

        marker = priority_marker[self.priority]
        action = " [ACTION]" if self.action_required else ""
        deadline_str = f" (Due: {self.deadline.strftime('%I:%M %p')})" if self.deadline else ""

        return f"{marker}{action} {self.title}{deadline_str}"


@dataclass
class DailyDigest:
    """Complete daily digest."""
    type: DigestType
    date: datetime
    items: List[DigestItem]
    summary: str
    action_count: int
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'type': self.type.value,
            'date': self.date.isoformat(),
            'summary': self.summary,
            'action_count': self.action_count,
            'items_by_category': self._group_by_category(),
            'total_items': len(self.items)
        }

    def _group_by_category(self) -> Dict[str, List[str]]:
        """Group items by category."""
        grouped: Dict[str, List[str]] = {}

        for item in self.items:
            if item.category not in grouped:
                grouped[item.category] = []
            grouped[item.category].append(str(item))

        return grouped


class DailyDigestGenerator:
    """
    Generate morning briefings and evening summaries.

    Morning briefing focuses on:
    - Urgent emails
    - Today's calendar
    - Important notifications
    - Priority tasks

    Evening summary focuses on:
    - Today's accomplishments
    - Pending tasks
    - Tomorrow's preparation
    - Follow-up opportunities
    """

    def __init__(
        self,
        email_service=None,
        calendar_service=None,
        task_manager=None,
        learning_db=None
    ):
        """
        Initialize digest generator.

        Args:
            email_service: Email service for fetching emails
            calendar_service: Calendar service for events
            task_manager: Task management system
            learning_db: Learning database for patterns
        """
        self.email = email_service
        self.calendar = calendar_service
        self.tasks = task_manager
        self.learning_db = learning_db

    async def generate_morning_briefing(
        self,
        date: datetime = None
    ) -> DailyDigest:
        """
        Generate morning briefing.

        Includes:
        - Urgent/important emails
        - Today's calendar
        - Weather/commute (if configured)
        - Priority tasks for today
        - Reminders and follow-ups

        Args:
            date: Date for briefing (defaults to today)

        Returns:
            DailyDigest with morning briefing
        """
        if date is None:
            date = datetime.now()

        items: List[DigestItem] = []

        # 1. Urgent emails
        email_items = await self._get_urgent_emails()
        items.extend(email_items)

        # 2. Today's calendar
        calendar_items = await self._get_todays_calendar(date)
        items.extend(calendar_items)

        # 3. Priority tasks
        task_items = await self._get_priority_tasks(date)
        items.extend(task_items)

        # 4. Follow-ups due today
        followup_items = await self._get_due_followups(date)
        items.extend(followup_items)

        # 5. Contextual reminders
        reminder_items = await self._get_contextual_reminders(date)
        items.extend(reminder_items)

        # Count action items
        action_count = sum(1 for item in items if item.action_required)

        # Generate summary
        summary = self._generate_morning_summary(items, action_count)

        return DailyDigest(
            type=DigestType.MORNING_BRIEFING,
            date=date,
            items=items,
            summary=summary,
            action_count=action_count,
            metadata={
                'generated_at': datetime.now().isoformat(),
                'categories': list(set(item.category for item in items))
            }
        )

    async def generate_evening_summary(
        self,
        date: datetime = None
    ) -> DailyDigest:
        """
        Generate evening summary.

        Includes:
        - Today's accomplishments
        - Completed tasks
        - Pending items
        - Tomorrow's prep
        - Follow-up opportunities

        Args:
            date: Date for summary (defaults to today)

        Returns:
            DailyDigest with evening summary
        """
        if date is None:
            date = datetime.now()

        items: List[DigestItem] = []

        # 1. Today's accomplishments
        accomplishment_items = await self._get_accomplishments(date)
        items.extend(accomplishment_items)

        # 2. Pending tasks
        pending_items = await self._get_pending_tasks(date)
        items.extend(pending_items)

        # 3. Tomorrow's preview
        tomorrow = date + timedelta(days=1)
        tomorrow_items = await self._get_tomorrows_preview(tomorrow)
        items.extend(tomorrow_items)

        # 4. Follow-up opportunities
        followup_opps = await self._get_followup_opportunities(date)
        items.extend(followup_opps)

        # 5. Weekly wrap-up (if Friday)
        if date.weekday() == 4:  # Friday
            weekly_items = await self._get_weekly_wrapup(date)
            items.extend(weekly_items)

        # Count action items
        action_count = sum(1 for item in items if item.action_required)

        # Generate summary
        summary = self._generate_evening_summary(items, action_count, date)

        return DailyDigest(
            type=DigestType.EVENING_SUMMARY,
            date=date,
            items=items,
            summary=summary,
            action_count=action_count,
            metadata={
                'generated_at': datetime.now().isoformat(),
                'categories': list(set(item.category for item in items))
            }
        )

    async def _get_urgent_emails(self) -> List[DigestItem]:
        """Get urgent/important emails."""
        items = []

        # TODO: Integrate with real email service
        # For now, return placeholder showing the structure

        # Example:
        # - Unread emails from VIPs
        # - Emails with "urgent" keywords
        # - Emails requiring response

        return items

    async def _get_todays_calendar(self, date: datetime) -> List[DigestItem]:
        """Get today's calendar events."""
        items = []

        # TODO: Integrate with real calendar service

        # Example placeholder: Create a sample meeting
        now = datetime.now()
        if 8 <= now.hour < 18:  # During work hours
            items.append(DigestItem(
                category="Calendar",
                title=f"Events scheduled for {date.strftime('%A, %B %d')}",
                description="Check calendar for today's meetings",
                priority=Priority.NORMAL,
                action_required=True,
                deadline=None,
                metadata={'type': 'calendar_check'}
            ))

        return items

    async def _get_priority_tasks(self, date: datetime) -> List[DigestItem]:
        """Get priority tasks for today."""
        items = []

        # TODO: Integrate with task management system

        # Example: Daily tasks
        items.append(DigestItem(
            category="Tasks",
            title="Review priority tasks for today",
            description="Plan your day's work",
            priority=Priority.HIGH,
            action_required=True,
            deadline=None,
            metadata={'type': 'daily_planning'}
        ))

        return items

    async def _get_due_followups(self, date: datetime) -> List[DigestItem]:
        """Get follow-ups due today."""
        items = []

        # TODO: Integrate with follow-up tracker
        # Example: Follow-ups from meetings, emails, tasks

        return items

    async def _get_contextual_reminders(self, date: datetime) -> List[DigestItem]:
        """Get contextual reminders based on patterns."""
        items = []

        if not self.learning_db:
            return items

        # TODO: Query learned patterns
        # Example: "You usually send weekly report on Fridays"

        return items

    async def _get_accomplishments(self, date: datetime) -> List[DigestItem]:
        """Get today's accomplishments."""
        items = []

        # TODO: Track completed tasks from task manager

        # Placeholder
        items.append(DigestItem(
            category="Accomplishments",
            title="Review today's completed work",
            description="Reflect on what you accomplished",
            priority=Priority.NORMAL,
            action_required=False,
            deadline=None,
            metadata={'type': 'reflection'}
        ))

        return items

    async def _get_pending_tasks(self, date: datetime) -> List[DigestItem]:
        """Get pending tasks."""
        items = []

        # TODO: Query pending tasks
        # Placeholder
        items.append(DigestItem(
            category="Pending",
            title="Review incomplete tasks",
            description="Tasks that need attention",
            priority=Priority.HIGH,
            action_required=True,
            deadline=None,
            metadata={'type': 'pending_review'}
        ))

        return items

    async def _get_tomorrows_preview(self, tomorrow: datetime) -> List[DigestItem]:
        """Get preview of tomorrow's schedule."""
        items = []

        # TODO: Query tomorrow's calendar

        items.append(DigestItem(
            category="Tomorrow",
            title=f"Preview {tomorrow.strftime('%A, %B %d')}",
            description="Check tomorrow's calendar and priorities",
            priority=Priority.NORMAL,
            action_required=True,
            deadline=None,
            metadata={'type': 'tomorrow_preview'}
        ))

        return items

    async def _get_followup_opportunities(self, date: datetime) -> List[DigestItem]:
        """Get follow-up opportunities."""
        items = []

        # TODO: Detect follow-up opportunities
        # Example: Meetings without follow-up notes
        # Example: Emails without replies

        return items

    async def _get_weekly_wrapup(self, date: datetime) -> List[DigestItem]:
        """Get weekly wrap-up (Fridays)."""
        items = []

        items.append(DigestItem(
            category="Weekly",
            title="End of week wrap-up",
            description="Review this week's progress and plan next week",
            priority=Priority.HIGH,
            action_required=True,
            deadline=None,
            metadata={'type': 'weekly_wrapup'}
        ))

        return items

    def _generate_morning_summary(
        self,
        items: List[DigestItem],
        action_count: int
    ) -> str:
        """Generate morning briefing summary."""
        urgent_count = sum(1 for item in items if item.priority == Priority.URGENT)
        high_count = sum(1 for item in items if item.priority == Priority.HIGH)

        summary = f"Good morning! Here's your briefing for today.\n"

        if urgent_count > 0:
            summary += f"\n[URGENT] {urgent_count} urgent item(s) need immediate attention."

        if high_count > 0:
            summary += f"\n[HIGH] {high_count} high-priority item(s) for today."

        if action_count > 0:
            summary += f"\n\nYou have {action_count} action item(s) requiring your attention."
        else:
            summary += f"\n\nNo urgent actions - have a productive day!"

        return summary

    def _generate_evening_summary(
        self,
        items: List[DigestItem],
        action_count: int,
        date: datetime
    ) -> str:
        """Generate evening summary."""
        accomplishment_count = sum(
            1 for item in items if item.category == "Accomplishments"
        )
        pending_count = sum(
            1 for item in items if item.category == "Pending"
        )

        summary = f"End of day summary for {date.strftime('%A, %B %d')}.\n"

        if accomplishment_count > 0:
            summary += f"\n[DONE] {accomplishment_count} accomplishment(s) today - great work!"

        if pending_count > 0:
            summary += f"\n[PENDING] {pending_count} item(s) need follow-up."

        if action_count > 0:
            summary += f"\n\nYou have {action_count} prep item(s) for tomorrow."

        # Friday special
        if date.weekday() == 4:
            summary += f"\n\n[WEEK END] Don't forget your weekly wrap-up!"

        return summary

    def format_digest(self, digest: DailyDigest) -> str:
        """
        Format digest for display.

        Args:
            digest: DailyDigest to format

        Returns:
            Formatted string ready for display
        """
        output = []

        # Header
        output.append("=" * 70)
        if digest.type == DigestType.MORNING_BRIEFING:
            output.append("MORNING BRIEFING")
        else:
            output.append("EVENING SUMMARY")
        output.append("=" * 70)

        # Date
        output.append(f"\n{digest.date.strftime('%A, %B %d, %Y')}")

        # Summary
        output.append(f"\n{digest.summary}")

        # Items by category
        output.append("\n" + "=" * 70)

        grouped = digest._group_by_category()
        for category, category_items in grouped.items():
            output.append(f"\n{category}:")
            for item in category_items:
                output.append(f"  {item}")

        # Footer
        output.append("\n" + "=" * 70)
        output.append(f"Total: {len(digest.items)} items, {digest.action_count} actions")
        output.append("=" * 70)

        return "\n".join(output)
