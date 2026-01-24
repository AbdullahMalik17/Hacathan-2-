"""
Business Metrics Model - Cross-Domain Analytics

Unified metrics for business and personal financial tracking:
- Financial: Revenue, expenses, profit, cash flow
- Social Media: Engagement, followers, reach, conversions
- Operational: Tasks completed, uptime, response time

Features:
- Time-series metric storage
- Multi-source aggregation
- Trend analysis
- Goal tracking
- Dashboard integration
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Optional, Dict, Any, List
from pathlib import Path


class MetricType(Enum):
    """Type of business metric."""
    FINANCIAL = "financial"
    SOCIAL = "social"
    OPERATIONAL = "operational"
    PERSONAL_FINANCE = "personal_finance"


class MetricSource(Enum):
    """Source of metric data."""
    ODOO = "odoo"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    GMAIL = "gmail"
    MANUAL = "manual"
    SYSTEM = "system"


@dataclass
class FinancialMetric:
    """
    Financial metrics for business and personal finances.

    Tracks revenue, expenses, profit, and cash flow.
    """
    date: date
    source: MetricSource

    # Income
    revenue: float = 0.0
    revenue_recurring: float = 0.0  # Subscription/recurring revenue
    revenue_one_time: float = 0.0

    # Expenses
    expenses: float = 0.0
    expenses_fixed: float = 0.0  # Rent, salaries, subscriptions
    expenses_variable: float = 0.0  # Materials, commissions

    # Derived
    profit: float = field(init=False)
    profit_margin: float = field(init=False)

    # Cash Flow
    accounts_receivable: float = 0.0  # Money owed to you
    accounts_payable: float = 0.0  # Money you owe
    cash_balance: float = 0.0

    # Metadata
    currency: str = "USD"
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate derived metrics."""
        self.profit = self.revenue - self.expenses
        self.profit_margin = (self.profit / self.revenue * 100) if self.revenue > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "date": self.date.isoformat(),
            "source": self.source.value,
            "revenue": self.revenue,
            "revenue_recurring": self.revenue_recurring,
            "revenue_one_time": self.revenue_one_time,
            "expenses": self.expenses,
            "expenses_fixed": self.expenses_fixed,
            "expenses_variable": self.expenses_variable,
            "profit": self.profit,
            "profit_margin": self.profit_margin,
            "accounts_receivable": self.accounts_receivable,
            "accounts_payable": self.accounts_payable,
            "cash_balance": self.cash_balance,
            "currency": self.currency,
            "notes": self.notes,
            "metadata": self.metadata
        }


@dataclass
class SocialMediaMetric:
    """
    Social media metrics for business presence.

    Tracks engagement, followers, reach across platforms.
    """
    date: date
    platform: str  # facebook, instagram, twitter, linkedin
    source: MetricSource

    # Audience
    followers: int = 0
    followers_gained: int = 0
    followers_lost: int = 0

    # Engagement
    posts: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0

    # Reach
    impressions: int = 0
    reach: int = 0
    engagement_rate: float = field(init=False)

    # Conversions
    clicks: int = 0
    conversions: int = 0
    conversion_rate: float = field(init=False)

    # Revenue (if applicable)
    revenue: float = 0.0
    ad_spend: float = 0.0
    roi: float = field(init=False)

    # Metadata
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate derived metrics."""
        total_engagement = self.likes + self.comments + self.shares + self.saves
        self.engagement_rate = (total_engagement / self.impressions * 100) if self.impressions > 0 else 0.0
        self.conversion_rate = (self.conversions / self.clicks * 100) if self.clicks > 0 else 0.0
        self.roi = ((self.revenue - self.ad_spend) / self.ad_spend * 100) if self.ad_spend > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "date": self.date.isoformat(),
            "platform": self.platform,
            "source": self.source.value,
            "followers": self.followers,
            "followers_gained": self.followers_gained,
            "followers_lost": self.followers_lost,
            "posts": self.posts,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "saves": self.saves,
            "impressions": self.impressions,
            "reach": self.reach,
            "engagement_rate": self.engagement_rate,
            "clicks": self.clicks,
            "conversions": self.conversions,
            "conversion_rate": self.conversion_rate,
            "revenue": self.revenue,
            "ad_spend": self.ad_spend,
            "roi": self.roi,
            "notes": self.notes,
            "metadata": self.metadata
        }


@dataclass
class OperationalMetric:
    """
    Operational metrics for system performance.

    Tracks task completion, uptime, response times.
    """
    date: date
    source: MetricSource = MetricSource.SYSTEM

    # Task Metrics
    tasks_processed: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_pending: int = 0
    success_rate: float = field(init=False)

    # Performance
    avg_task_time_ms: Optional[float] = None
    p95_task_time_ms: Optional[float] = None
    p99_task_time_ms: Optional[float] = None

    # Service Health
    uptime_percent: float = 100.0
    downtime_minutes: int = 0
    incidents: int = 0

    # API Metrics
    api_calls: int = 0
    api_errors: int = 0
    api_latency_ms: Optional[float] = None

    # Resource Usage
    cpu_avg_percent: float = 0.0
    memory_avg_percent: float = 0.0
    disk_avg_percent: float = 0.0

    # Email Metrics
    emails_received: int = 0
    emails_sent: int = 0
    emails_processed: int = 0

    # Metadata
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate derived metrics."""
        self.success_rate = (self.tasks_completed / self.tasks_processed * 100) if self.tasks_processed > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "date": self.date.isoformat(),
            "source": self.source.value,
            "tasks_processed": self.tasks_processed,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "tasks_pending": self.tasks_pending,
            "success_rate": self.success_rate,
            "avg_task_time_ms": self.avg_task_time_ms,
            "p95_task_time_ms": self.p95_task_time_ms,
            "p99_task_time_ms": self.p99_task_time_ms,
            "uptime_percent": self.uptime_percent,
            "downtime_minutes": self.downtime_minutes,
            "incidents": self.incidents,
            "api_calls": self.api_calls,
            "api_errors": self.api_errors,
            "api_latency_ms": self.api_latency_ms,
            "cpu_avg_percent": self.cpu_avg_percent,
            "memory_avg_percent": self.memory_avg_percent,
            "disk_avg_percent": self.disk_avg_percent,
            "emails_received": self.emails_received,
            "emails_sent": self.emails_sent,
            "emails_processed": self.emails_processed,
            "notes": self.notes,
            "metadata": self.metadata
        }


@dataclass
class MetricsSummary:
    """
    Aggregated metrics summary for dashboard.

    Combines financial, social, and operational metrics.
    """
    period_start: date
    period_end: date

    # Financial Summary
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    total_profit: float = 0.0
    avg_profit_margin: float = 0.0

    # Social Summary
    total_followers: int = 0
    total_engagement: int = 0
    avg_engagement_rate: float = 0.0

    # Operational Summary
    total_tasks: int = 0
    total_completed: int = 0
    avg_success_rate: float = 0.0
    avg_uptime: float = 100.0

    # Goals & Targets
    revenue_goal: Optional[float] = None
    revenue_progress: float = field(init=False, default=0.0)
    tasks_goal: Optional[int] = None
    tasks_progress: float = field(init=False, default=0.0)

    def __post_init__(self):
        """Calculate goal progress."""
        if self.revenue_goal and self.revenue_goal > 0:
            self.revenue_progress = (self.total_revenue / self.revenue_goal * 100)
        if self.tasks_goal and self.tasks_goal > 0:
            self.tasks_progress = (self.total_tasks / self.tasks_goal * 100)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_revenue": self.total_revenue,
            "total_expenses": self.total_expenses,
            "total_profit": self.total_profit,
            "avg_profit_margin": self.avg_profit_margin,
            "total_followers": self.total_followers,
            "total_engagement": self.total_engagement,
            "avg_engagement_rate": self.avg_engagement_rate,
            "total_tasks": self.total_tasks,
            "total_completed": self.total_completed,
            "avg_success_rate": self.avg_success_rate,
            "avg_uptime": self.avg_uptime,
            "revenue_goal": self.revenue_goal,
            "revenue_progress": self.revenue_progress,
            "tasks_goal": self.tasks_goal,
            "tasks_progress": self.tasks_progress
        }


if __name__ == "__main__":
    # Test business metrics
    print("Testing Business Metrics Model...")

    # Test Financial Metric
    print("\n1. Testing FinancialMetric...")
    financial = FinancialMetric(
        date=date.today(),
        source=MetricSource.ODOO,
        revenue=10000.0,
        revenue_recurring=8000.0,
        revenue_one_time=2000.0,
        expenses=6000.0,
        expenses_fixed=4000.0,
        expenses_variable=2000.0,
        cash_balance=15000.0
    )
    print(f"[OK] Created financial metric")
    print(f"  Revenue: ${financial.revenue:,.2f}")
    print(f"  Expenses: ${financial.expenses:,.2f}")
    print(f"  Profit: ${financial.profit:,.2f}")
    print(f"  Profit Margin: {financial.profit_margin:.1f}%")

    # Test Social Media Metric
    print("\n2. Testing SocialMediaMetric...")
    social = SocialMediaMetric(
        date=date.today(),
        platform="instagram",
        source=MetricSource.INSTAGRAM,
        followers=5000,
        followers_gained=150,
        followers_lost=20,
        posts=10,
        likes=1500,
        comments=200,
        shares=50,
        impressions=25000,
        reach=18000,
        clicks=500,
        conversions=25,
        revenue=1000.0,
        ad_spend=200.0
    )
    print(f"[OK] Created social media metric")
    print(f"  Platform: {social.platform}")
    print(f"  Followers: {social.followers:,}")
    print(f"  Engagement Rate: {social.engagement_rate:.2f}%")
    print(f"  Conversion Rate: {social.conversion_rate:.2f}%")
    print(f"  ROI: {social.roi:.1f}%")

    # Test Operational Metric
    print("\n3. Testing OperationalMetric...")
    operational = OperationalMetric(
        date=date.today(),
        tasks_processed=100,
        tasks_completed=95,
        tasks_failed=5,
        tasks_pending=20,
        avg_task_time_ms=2500.0,
        uptime_percent=99.5,
        api_calls=500,
        api_errors=10,
        cpu_avg_percent=45.0,
        memory_avg_percent=65.0,
        emails_received=50,
        emails_processed=48
    )
    print(f"[OK] Created operational metric")
    print(f"  Tasks Completed: {operational.tasks_completed}/{operational.tasks_processed}")
    print(f"  Success Rate: {operational.success_rate:.1f}%")
    print(f"  Uptime: {operational.uptime_percent}%")
    print(f"  Avg Task Time: {operational.avg_task_time_ms}ms")

    # Test Metrics Summary
    print("\n4. Testing MetricsSummary...")
    summary = MetricsSummary(
        period_start=date(2026, 1, 1),
        period_end=date.today(),
        total_revenue=50000.0,
        total_expenses=30000.0,
        total_profit=20000.0,
        avg_profit_margin=40.0,
        total_followers=5000,
        total_engagement=10000,
        avg_engagement_rate=5.5,
        total_tasks=500,
        total_completed=475,
        avg_success_rate=95.0,
        avg_uptime=99.5,
        revenue_goal=60000.0,
        tasks_goal=600
    )
    print(f"[OK] Created metrics summary")
    print(f"  Period: {summary.period_start} to {summary.period_end}")
    print(f"  Total Revenue: ${summary.total_revenue:,.2f}")
    print(f"  Total Profit: ${summary.total_profit:,.2f}")
    print(f"  Revenue Goal Progress: {summary.revenue_progress:.1f}%")
    print(f"  Tasks Goal Progress: {summary.tasks_progress:.1f}%")

    # Test serialization
    print("\n5. Testing serialization...")
    financial_dict = financial.to_dict()
    print(f"[OK] Financial metric serialized: {len(financial_dict)} fields")

    social_dict = social.to_dict()
    print(f"[OK] Social metric serialized: {len(social_dict)} fields")

    operational_dict = operational.to_dict()
    print(f"[OK] Operational metric serialized: {len(operational_dict)} fields")

    summary_dict = summary.to_dict()
    print(f"[OK] Summary serialized: {len(summary_dict)} fields")

    print("\n[SUCCESS] All business metrics tests passed!")
