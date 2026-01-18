"""
Task Data Model - Cross-Domain Foundation

Unified task representation with domain classification:
- Personal: Individual tasks (emails, appointments, personal finances)
- Business: Professional tasks (invoices, client work, social media)
- Both: Tasks spanning both domains

Features:
- Domain classification
- Task dependencies and priorities
- Rich metadata
- Status tracking
- Audit trail integration
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pathlib import Path


class TaskDomain(Enum):
    """Task domain classification."""
    PERSONAL = "personal"
    BUSINESS = "business"
    BOTH = "both"  # Cross-domain tasks


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskSource(Enum):
    """Where the task originated."""
    GMAIL = "gmail"
    WHATSAPP = "whatsapp"
    MANUAL = "manual"
    SYSTEM = "system"
    ODOO = "odoo"
    SOCIAL_MEDIA = "social_media"


@dataclass
class TaskDependency:
    """Represents a dependency between tasks."""
    task_id: str
    dependency_type: str  # "blocks", "requires", "related"
    description: Optional[str] = None


@dataclass
class Task:
    """
    Unified task model for cross-domain operations.

    Attributes:
        id: Unique task identifier
        title: Human-readable task title
        description: Detailed task description
        domain: Task domain (personal, business, both)
        priority: Task priority level
        status: Current task status
        source: Where the task came from

        # Timestamps
        created_at: When task was created
        updated_at: When task was last updated
        due_date: Optional deadline
        completed_at: When task was completed

        # Context
        source_file: Path to source document
        agent: Agent assigned to task
        tags: List of tags for categorization
        metadata: Additional context data

        # Dependencies
        dependencies: Tasks this depends on
        blocked_by: Tasks blocking this task

        # Business Context
        business_value: Estimated business value (e.g., revenue, cost savings)
        client: Related client/customer
        project: Related project

        # Personal Context
        personal_category: Category (health, finance, family, etc.)

        # Tracking
        retry_count: Number of retry attempts
        error_message: Last error if failed
    """

    # Core fields
    id: str
    title: str
    description: str
    domain: TaskDomain
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    source: TaskSource = TaskSource.MANUAL

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Context
    source_file: Optional[Path] = None
    agent: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Dependencies
    dependencies: List[TaskDependency] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)

    # Business Context
    business_value: Optional[float] = None
    client: Optional[str] = None
    project: Optional[str] = None

    # Personal Context
    personal_category: Optional[str] = None

    # Tracking
    retry_count: int = 0
    error_message: Optional[str] = None

    def add_dependency(self, task_id: str, dependency_type: str = "requires", description: str = None):
        """Add a task dependency."""
        dep = TaskDependency(
            task_id=task_id,
            dependency_type=dependency_type,
            description=description
        )
        self.dependencies.append(dep)
        self.updated_at = datetime.now()

    def is_blocked(self) -> bool:
        """Check if task is blocked by dependencies."""
        return len(self.blocked_by) > 0 or self.status == TaskStatus.BLOCKED

    def can_execute(self) -> bool:
        """Check if task can be executed."""
        return (
            self.status == TaskStatus.PENDING and
            not self.is_blocked() and
            (self.due_date is None or self.due_date > datetime.now())
        )

    def mark_completed(self):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def mark_failed(self, error: str):
        """Mark task as failed with error."""
        self.status = TaskStatus.FAILED
        self.error_message = error
        self.retry_count += 1
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "domain": self.domain.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "source": self.source.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "source_file": str(self.source_file) if self.source_file else None,
            "agent": self.agent,
            "tags": self.tags,
            "metadata": self.metadata,
            "dependencies": [
                {
                    "task_id": dep.task_id,
                    "dependency_type": dep.dependency_type,
                    "description": dep.description
                }
                for dep in self.dependencies
            ],
            "blocked_by": self.blocked_by,
            "business_value": self.business_value,
            "client": self.client,
            "project": self.project,
            "personal_category": self.personal_category,
            "retry_count": self.retry_count,
            "error_message": self.error_message
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        # Parse dependencies
        dependencies = []
        for dep_data in data.get("dependencies", []):
            dependencies.append(TaskDependency(
                task_id=dep_data["task_id"],
                dependency_type=dep_data["dependency_type"],
                description=dep_data.get("description")
            ))

        # Parse datetimes
        created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        updated_at = datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now()
        due_date = datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None
        completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None

        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            domain=TaskDomain(data["domain"]),
            priority=TaskPriority(data.get("priority", "medium")),
            status=TaskStatus(data.get("status", "pending")),
            source=TaskSource(data.get("source", "manual")),
            created_at=created_at,
            updated_at=updated_at,
            due_date=due_date,
            completed_at=completed_at,
            source_file=Path(data["source_file"]) if data.get("source_file") else None,
            agent=data.get("agent"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            dependencies=dependencies,
            blocked_by=data.get("blocked_by", []),
            business_value=data.get("business_value"),
            client=data.get("client"),
            project=data.get("project"),
            personal_category=data.get("personal_category"),
            retry_count=data.get("retry_count", 0),
            error_message=data.get("error_message")
        )


if __name__ == "__main__":
    # Test the task model
    print("Testing Task Model...")

    # Create a business task
    business_task = Task(
        id="task_001",
        title="Create invoice for client",
        description="Generate and send invoice for Project X",
        domain=TaskDomain.BUSINESS,
        priority=TaskPriority.HIGH,
        source=TaskSource.ODOO,
        client="Acme Corp",
        project="Project X",
        business_value=5000.0,
        tags=["invoice", "accounting", "urgent"]
    )

    print(f"[OK] Created business task: {business_task.title}")
    print(f"  Domain: {business_task.domain.value}")
    print(f"  Priority: {business_task.priority.value}")
    print(f"  Can execute: {business_task.can_execute()}")

    # Create a personal task
    personal_task = Task(
        id="task_002",
        title="Schedule dentist appointment",
        description="Book annual checkup",
        domain=TaskDomain.PERSONAL,
        priority=TaskPriority.LOW,
        source=TaskSource.GMAIL,
        personal_category="health",
        tags=["health", "appointment"]
    )

    print(f"[OK] Created personal task: {personal_task.title}")

    # Create a cross-domain task
    cross_task = Task(
        id="task_003",
        title="Prepare tax documents",
        description="Gather personal and business tax documents",
        domain=TaskDomain.BOTH,
        priority=TaskPriority.URGENT,
        source=TaskSource.MANUAL,
        tags=["taxes", "deadline", "cross-domain"]
    )

    cross_task.add_dependency("task_001", "requires", "Need invoice records")

    print(f"[OK] Created cross-domain task: {cross_task.title}")
    print(f"  Dependencies: {len(cross_task.dependencies)}")

    # Test serialization
    task_dict = business_task.to_dict()
    print(f"[OK] Serialized to dict: {len(task_dict)} fields")

    restored_task = Task.from_dict(task_dict)
    print(f"[OK] Deserialized from dict: {restored_task.title}")

    # Test status changes
    business_task.mark_completed()
    print(f"[OK] Marked as completed: {business_task.status.value}")

    personal_task.mark_failed("API timeout")
    print(f"[OK] Marked as failed: {personal_task.status.value}, retry count: {personal_task.retry_count}")

    print("\n[SUCCESS] All task model tests passed!")
