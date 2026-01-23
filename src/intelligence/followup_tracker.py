"""
Follow-up Tracker - Track and remind about pending follow-ups.
Automatically detects opportunities and reminds at the right time.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import hashlib


class FollowUpType(Enum):
    """Type of follow-up."""
    MEETING = "meeting"
    EMAIL = "email"
    TASK = "task"
    CALL = "call"
    MESSAGE = "message"
    CUSTOM = "custom"


class FollowUpStatus(Enum):
    """Status of follow-up."""
    PENDING = "pending"
    REMINDED = "reminded"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class Priority(Enum):
    """Priority level."""
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class FollowUpItem:
    """A single follow-up item."""
    id: str
    type: FollowUpType
    title: str
    description: str
    due_date: datetime
    priority: Priority
    status: FollowUpStatus
    related_to: Optional[str]  # Meeting ID, email ID, etc.
    context: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime]

    def is_overdue(self) -> bool:
        """Check if follow-up is overdue."""
        return datetime.now() > self.due_date and self.status == FollowUpStatus.PENDING

    def days_until_due(self) -> int:
        """Days until due (negative if overdue)."""
        delta = self.due_date - datetime.now()
        return delta.days

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat(),
            'priority': self.priority.value,
            'status': self.status.value,
            'related_to': self.related_to,
            'context': self.context,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_overdue': self.is_overdue(),
            'days_until_due': self.days_until_due()
        }


class FollowUpTracker:
    """
    Track and manage follow-ups automatically.

    Features:
    - Auto-detect follow-up opportunities
    - Smart reminders at the right time
    - Context-aware suggestions
    - Priority-based sorting
    - Integration with calendar, email, tasks
    """

    def __init__(
        self,
        storage_db=None,
        notification_service=None
    ):
        """
        Initialize follow-up tracker.

        Args:
            storage_db: Database for persistent storage
            notification_service: Service for sending reminders
        """
        self.storage = storage_db
        self.notifications = notification_service

        # In-memory follow-ups (would be in DB in production)
        self.followups: Dict[str, FollowUpItem] = {}

    def create_followup(
        self,
        type: FollowUpType,
        title: str,
        description: str,
        due_date: datetime,
        priority: Priority = Priority.NORMAL,
        related_to: str = None,
        context: Dict = None
    ) -> FollowUpItem:
        """
        Create a new follow-up item.

        Args:
            type: Type of follow-up
            title: Brief title
            description: Detailed description
            due_date: When follow-up is due
            priority: Priority level
            related_to: Related item ID (meeting, email, etc.)
            context: Additional context

        Returns:
            Created FollowUpItem
        """
        # Generate ID
        item_id = hashlib.md5(
            f"{type.value}_{title}_{datetime.now().timestamp()}".encode()
        ).hexdigest()[:12]

        followup = FollowUpItem(
            id=item_id,
            type=type,
            title=title,
            description=description,
            due_date=due_date,
            priority=priority,
            status=FollowUpStatus.PENDING,
            related_to=related_to,
            context=context or {},
            created_at=datetime.now(),
            completed_at=None
        )

        self.followups[item_id] = followup

        # Store in database
        if self.storage:
            self._store_followup(followup)

        return followup

    def complete_followup(self, followup_id: str):
        """Mark follow-up as completed."""
        if followup_id not in self.followups:
            raise ValueError(f"Follow-up {followup_id} not found")

        followup = self.followups[followup_id]
        followup.status = FollowUpStatus.COMPLETED
        followup.completed_at = datetime.now()

        # Update in database
        if self.storage:
            self._update_followup(followup)

    def cancel_followup(self, followup_id: str):
        """Cancel a follow-up."""
        if followup_id not in self.followups:
            raise ValueError(f"Follow-up {followup_id} not found")

        followup = self.followups[followup_id]
        followup.status = FollowUpStatus.CANCELLED

        # Update in database
        if self.storage:
            self._update_followup(followup)

    def get_pending_followups(
        self,
        type: FollowUpType = None,
        priority: Priority = None
    ) -> List[FollowUpItem]:
        """
        Get pending follow-ups with optional filters.

        Args:
            type: Filter by type
            priority: Filter by priority

        Returns:
            List of pending follow-ups
        """
        followups = [
            f for f in self.followups.values()
            if f.status == FollowUpStatus.PENDING
        ]

        if type:
            followups = [f for f in followups if f.type == type]

        if priority:
            followups = [f for f in followups if f.priority == priority]

        # Sort by due date and priority
        followups.sort(key=lambda f: (f.due_date, f.priority.value))

        return followups

    def get_overdue_followups(self) -> List[FollowUpItem]:
        """Get overdue follow-ups."""
        return [
            f for f in self.followups.values()
            if f.is_overdue()
        ]

    def get_due_today(self) -> List[FollowUpItem]:
        """Get follow-ups due today."""
        today = datetime.now().date()
        return [
            f for f in self.followups.values()
            if f.status == FollowUpStatus.PENDING and
            f.due_date.date() == today
        ]

    def get_due_this_week(self) -> List[FollowUpItem]:
        """Get follow-ups due this week."""
        today = datetime.now()
        week_end = today + timedelta(days=7)

        return [
            f for f in self.followups.values()
            if f.status == FollowUpStatus.PENDING and
            today <= f.due_date <= week_end
        ]

    async def auto_detect_followups(
        self,
        meeting_data: Dict = None,
        email_data: Dict = None,
        task_data: Dict = None
    ) -> List[FollowUpItem]:
        """
        Automatically detect follow-up opportunities.

        Analyzes various contexts to identify needed follow-ups.

        Args:
            meeting_data: Recent meeting data
            email_data: Recent email data
            task_data: Recent task data

        Returns:
            List of detected follow-up opportunities
        """
        detected = []

        # Detect from meetings
        if meeting_data:
            meeting_followups = await self._detect_meeting_followups(meeting_data)
            detected.extend(meeting_followups)

        # Detect from emails
        if email_data:
            email_followups = await self._detect_email_followups(email_data)
            detected.extend(email_followups)

        # Detect from tasks
        if task_data:
            task_followups = await self._detect_task_followups(task_data)
            detected.extend(task_followups)

        return detected

    async def _detect_meeting_followups(
        self,
        meeting_data: Dict
    ) -> List[FollowUpItem]:
        """
        Detect follow-ups from meetings.

        Looks for:
        - Meetings without follow-up notes
        - Action items assigned
        - Decisions requiring follow-up
        """
        followups = []

        # Example detection logic:
        # If meeting was more than 1 day ago and no follow-up exists
        meeting_date = datetime.fromisoformat(meeting_data.get('date', ''))
        if datetime.now() - meeting_date > timedelta(days=1):
            # Check if follow-up already exists
            existing = any(
                f.related_to == meeting_data.get('id')
                for f in self.followups.values()
            )

            if not existing:
                # Create follow-up suggestion
                followup = self.create_followup(
                    type=FollowUpType.MEETING,
                    title=f"Follow up on {meeting_data.get('title', 'meeting')}",
                    description="Review meeting notes and send follow-up",
                    due_date=datetime.now() + timedelta(days=2),
                    priority=Priority.NORMAL,
                    related_to=meeting_data.get('id'),
                    context={'meeting_data': meeting_data}
                )
                followups.append(followup)

        return followups

    async def _detect_email_followups(
        self,
        email_data: Dict
    ) -> List[FollowUpItem]:
        """
        Detect follow-ups from emails.

        Looks for:
        - Important emails without replies
        - Emails with questions
        - Pending requests
        """
        followups = []

        # Example detection logic:
        # Email from VIP without reply in 24h
        if email_data.get('importance') == 'high':
            sent_date = datetime.fromisoformat(email_data.get('date', ''))
            if datetime.now() - sent_date > timedelta(hours=24):
                followup = self.create_followup(
                    type=FollowUpType.EMAIL,
                    title=f"Reply to {email_data.get('sender', 'email')}",
                    description=f"Subject: {email_data.get('subject', '')}",
                    due_date=datetime.now() + timedelta(hours=2),
                    priority=Priority.HIGH,
                    related_to=email_data.get('id'),
                    context={'email_data': email_data}
                )
                followups.append(followup)

        return followups

    async def _detect_task_followups(
        self,
        task_data: Dict
    ) -> List[FollowUpItem]:
        """
        Detect follow-ups from tasks.

        Looks for:
        - Completed tasks requiring follow-up
        - Blocked tasks
        - Tasks with dependencies
        """
        followups = []

        # Example detection logic:
        # Completed task that mentions follow-up
        if task_data.get('status') == 'completed':
            if 'follow' in task_data.get('description', '').lower():
                followup = self.create_followup(
                    type=FollowUpType.TASK,
                    title=f"Follow up on {task_data.get('title', 'task')}",
                    description="Verify completion and outcomes",
                    due_date=datetime.now() + timedelta(days=1),
                    priority=Priority.NORMAL,
                    related_to=task_data.get('id'),
                    context={'task_data': task_data}
                )
                followups.append(followup)

        return followups

    async def send_reminders(self) -> List[FollowUpItem]:
        """
        Send reminders for due follow-ups.

        Returns:
            List of follow-ups that were reminded
        """
        reminded = []

        # Get follow-ups that need reminding
        due_today = self.get_due_today()
        overdue = self.get_overdue_followups()

        for followup in due_today + overdue:
            if followup.status != FollowUpStatus.REMINDED:
                # Send reminder
                await self._send_reminder(followup)
                followup.status = FollowUpStatus.REMINDED
                reminded.append(followup)

                # Update status
                if followup.is_overdue():
                    followup.status = FollowUpStatus.OVERDUE

        return reminded

    async def _send_reminder(self, followup: FollowUpItem):
        """Send reminder notification."""
        if self.notifications:
            # Send via notification service
            await self.notifications.send(
                title=f"Follow-up: {followup.title}",
                body=followup.description,
                priority=followup.priority.value
            )
        else:
            # Just log for now
            print(f"\n[REMINDER] {followup.title}")
            print(f"  Due: {followup.due_date.strftime('%I:%M %p')}")
            print(f"  Priority: {followup.priority.name}")
            print(f"  {followup.description}")

    def get_stats(self) -> Dict:
        """Get follow-up statistics."""
        pending = self.get_pending_followups()
        overdue = self.get_overdue_followups()
        completed = [
            f for f in self.followups.values()
            if f.status == FollowUpStatus.COMPLETED
        ]

        return {
            'total': len(self.followups),
            'pending': len(pending),
            'overdue': len(overdue),
            'completed': len(completed),
            'completion_rate': len(completed) / len(self.followups) if self.followups else 0
        }

    def _store_followup(self, followup: FollowUpItem):
        """Store follow-up in database."""
        # TODO: Implement database storage
        pass

    def _update_followup(self, followup: FollowUpItem):
        """Update follow-up in database."""
        # TODO: Implement database update
        pass

    def format_followup_list(
        self,
        followups: List[FollowUpItem],
        title: str = "Follow-ups"
    ) -> str:
        """Format follow-up list for display."""
        if not followups:
            return f"\n{title}: None\n"

        output = [f"\n{title}:"]
        output.append("=" * 70)

        for followup in followups:
            # Priority marker
            priority_marker = {
                Priority.URGENT: "[URGENT]",
                Priority.HIGH: "[HIGH]",
                Priority.NORMAL: "",
                Priority.LOW: "[LOW]"
            }[followup.priority]

            # Overdue marker
            overdue_marker = " [OVERDUE]" if followup.is_overdue() else ""

            # Days until due
            days = followup.days_until_due()
            if days == 0:
                due_str = " (Due today)"
            elif days < 0:
                due_str = f" ({abs(days)} days overdue)"
            else:
                due_str = f" (Due in {days} days)"

            output.append(f"\n{priority_marker}{overdue_marker} {followup.title}{due_str}")
            output.append(f"  {followup.description}")
            output.append(f"  Type: {followup.type.value} | Status: {followup.status.value}")

        output.append("\n" + "=" * 70)

        return "\n".join(output)
