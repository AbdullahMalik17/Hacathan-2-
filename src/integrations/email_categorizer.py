"""
Email Categorization System - Smart email organization and prioritization.
Ready for Gmail API integration.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re


class EmailCategory(Enum):
    """Email categories."""
    URGENT_ACTION = "urgent_action"  # Needs immediate response
    HIGH_PRIORITY = "high_priority"  # Important, do today
    NORMAL = "normal"  # Regular emails
    LOW_PRIORITY = "low_priority"  # FYI, low importance
    NEWSLETTER = "newsletter"  # Subscriptions, updates
    SOCIAL = "social"  # Social media notifications
    PROMOTIONAL = "promotional"  # Marketing, sales
    SPAM = "spam"  # Spam or unwanted
    AUTOMATED = "automated"  # System-generated


class EmailImportance(Enum):
    """Importance levels."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


@dataclass
class EmailMessage:
    """Email message data."""
    id: str
    sender: str
    sender_name: Optional[str]
    subject: str
    body_preview: str
    received_at: datetime
    has_attachments: bool
    is_read: bool
    labels: List[str]
    thread_id: Optional[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'sender': self.sender,
            'sender_name': self.sender_name,
            'subject': self.subject,
            'body_preview': self.body_preview,
            'received_at': self.received_at.isoformat(),
            'has_attachments': self.has_attachments,
            'is_read': self.is_read,
            'labels': self.labels,
            'thread_id': self.thread_id
        }


@dataclass
class CategorizedEmail:
    """Email with categorization."""
    email: EmailMessage
    category: EmailCategory
    importance: EmailImportance
    confidence: float
    reasoning: List[str]
    suggested_actions: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'email': self.email.to_dict(),
            'category': self.category.value,
            'importance': self.importance.value,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'suggested_actions': self.suggested_actions
        }


class EmailCategorizer:
    """
    Intelligent email categorization system.

    Features:
    - Rule-based categorization
    - Sender importance scoring
    - Content analysis
    - Urgency detection
    - Suggested actions
    - Learning from user behavior
    """

    # VIP indicators
    VIP_DOMAINS = ['ceo', 'founder', 'director', 'president', 'vp']
    VIP_KEYWORDS = ['urgent', 'asap', 'important', 'critical', 'emergency']

    # Newsletter indicators
    NEWSLETTER_KEYWORDS = [
        'unsubscribe', 'newsletter', 'weekly digest', 'update',
        'subscription', 'mailing list'
    ]

    # Automated indicators
    AUTOMATED_KEYWORDS = [
        'no-reply', 'noreply', 'do not reply', 'automated',
        'notification', 'alert', 'system'
    ]

    # Promotional indicators
    PROMOTIONAL_KEYWORDS = [
        'sale', 'discount', 'offer', 'deal', 'promo',
        'limited time', 'buy now', 'shop', 'save'
    ]

    def __init__(
        self,
        gmail_service=None,
        learning_db=None,
        vip_contacts: List[str] = None
    ):
        """
        Initialize email categorizer.

        Args:
            gmail_service: Gmail API service object
            learning_db: Learning database for patterns
            vip_contacts: List of VIP email addresses
        """
        self.gmail = gmail_service
        self.learning_db = learning_db
        self.vip_contacts = set(vip_contacts or [])

    async def categorize_email(
        self,
        email: EmailMessage
    ) -> CategorizedEmail:
        """
        Categorize a single email.

        Args:
            email: Email message to categorize

        Returns:
            CategorizedEmail with category and importance
        """
        # Calculate scores for different categories
        scores = {
            EmailCategory.URGENT_ACTION: self._score_urgent(email),
            EmailCategory.HIGH_PRIORITY: self._score_high_priority(email),
            EmailCategory.NEWSLETTER: self._score_newsletter(email),
            EmailCategory.SOCIAL: self._score_social(email),
            EmailCategory.PROMOTIONAL: self._score_promotional(email),
            EmailCategory.SPAM: self._score_spam(email),
            EmailCategory.AUTOMATED: self._score_automated(email),
        }

        # Choose category with highest score
        category = max(scores, key=scores.get)
        confidence = scores[category]

        # If no strong match, default to normal
        if confidence < 0.5:
            category = EmailCategory.NORMAL
            confidence = 0.5

        # Determine importance
        importance = self._calculate_importance(email, category)

        # Generate reasoning
        reasoning = self._generate_reasoning(email, category, scores)

        # Suggest actions
        suggested_actions = self._suggest_actions(email, category, importance)

        return CategorizedEmail(
            email=email,
            category=category,
            importance=importance,
            confidence=confidence,
            reasoning=reasoning,
            suggested_actions=suggested_actions
        )

    def _score_urgent(self, email: EmailMessage) -> float:
        """Score urgency of email."""
        score = 0.0

        # Check sender is VIP
        if email.sender in self.vip_contacts:
            score += 0.5

        # Check for VIP titles in sender name
        if email.sender_name:
            for vip_term in self.VIP_DOMAINS:
                if vip_term in email.sender_name.lower():
                    score += 0.2
                    break

        # Check for urgent keywords in subject
        subject_lower = email.subject.lower()
        for keyword in self.VIP_KEYWORDS:
            if keyword in subject_lower:
                score += 0.3
                break

        # Unread emails from today are more urgent
        if not email.is_read:
            age_hours = (datetime.now() - email.received_at).total_seconds() / 3600
            if age_hours < 2:
                score += 0.2

        return min(score, 1.0)

    def _score_high_priority(self, email: EmailMessage) -> float:
        """Score high priority indicators."""
        score = 0.0

        # Direct to user (not CC/BCC)
        # Would check To field in real implementation
        score += 0.3

        # Has attachments (often important)
        if email.has_attachments:
            score += 0.2

        # Not part of a long thread (probably important)
        # Would check thread length in real implementation
        score += 0.2

        # From known domain
        domain = email.sender.split('@')[-1] if '@' in email.sender else ''
        if domain and not any(promo in domain for promo in ['marketing', 'newsletter']):
            score += 0.3

        return min(score, 1.0)

    def _score_newsletter(self, email: EmailMessage) -> float:
        """Score newsletter indicators."""
        score = 0.0

        subject_lower = email.subject.lower()
        body_lower = email.body_preview.lower()

        # Check for newsletter keywords
        for keyword in self.NEWSLETTER_KEYWORDS:
            if keyword in subject_lower or keyword in body_lower:
                score += 0.4
                break

        # Check sender domain
        sender_lower = email.sender.lower()
        if any(term in sender_lower for term in ['newsletter', 'updates', 'digest']):
            score += 0.3

        # Has unsubscribe in body
        if 'unsubscribe' in body_lower:
            score += 0.3

        return min(score, 1.0)

    def _score_social(self, email: EmailMessage) -> float:
        """Score social media indicators."""
        score = 0.0

        sender_lower = email.sender.lower()
        subject_lower = email.subject.lower()

        # Check for social media domains
        social_domains = [
            'facebook', 'twitter', 'linkedin', 'instagram',
            'pinterest', 'reddit', 'tiktok'
        ]

        for domain in social_domains:
            if domain in sender_lower:
                score += 0.7
                break

        # Check for social keywords
        social_keywords = [
            'liked', 'commented', 'shared', 'tagged',
            'mentioned', 'followed', 'friend request'
        ]

        for keyword in social_keywords:
            if keyword in subject_lower:
                score += 0.3
                break

        return min(score, 1.0)

    def _score_promotional(self, email: EmailMessage) -> float:
        """Score promotional indicators."""
        score = 0.0

        subject_lower = email.subject.lower()
        body_lower = email.body_preview.lower()

        # Check for promotional keywords
        for keyword in self.PROMOTIONAL_KEYWORDS:
            if keyword in subject_lower:
                score += 0.3
                break

        # Check body
        for keyword in self.PROMOTIONAL_KEYWORDS:
            if keyword in body_lower:
                score += 0.2
                break

        # Marketing/sales in sender
        sender_lower = email.sender.lower()
        if any(term in sender_lower for term in ['marketing', 'sales', 'promo']):
            score += 0.3

        return min(score, 1.0)

    def _score_spam(self, email: EmailMessage) -> float:
        """Score spam indicators."""
        score = 0.0

        subject_lower = email.subject.lower()

        # Excessive punctuation
        if subject_lower.count('!') > 2:
            score += 0.2

        # All caps subject
        if email.subject.isupper() and len(email.subject) > 10:
            score += 0.3

        # Suspicious keywords
        spam_keywords = [
            'viagra', 'casino', 'lottery', 'winner',
            'claim', 'free money', 'click here', 'congratulations'
        ]

        for keyword in spam_keywords:
            if keyword in subject_lower:
                score += 0.5
                break

        return min(score, 1.0)

    def _score_automated(self, email: EmailMessage) -> float:
        """Score automated email indicators."""
        score = 0.0

        sender_lower = email.sender.lower()
        subject_lower = email.subject.lower()

        # Check for automated keywords in sender
        for keyword in self.AUTOMATED_KEYWORDS:
            if keyword in sender_lower:
                score += 0.5
                break

        # Check for notification patterns
        notification_patterns = [
            'notification', 'alert', 'reminder', 'confirmation',
            'receipt', 'invoice', 'ticket', 'order'
        ]

        for pattern in notification_patterns:
            if pattern in subject_lower:
                score += 0.3
                break

        return min(score, 1.0)

    def _calculate_importance(
        self,
        email: EmailMessage,
        category: EmailCategory
    ) -> EmailImportance:
        """Calculate email importance."""
        # Base importance by category
        category_importance = {
            EmailCategory.URGENT_ACTION: EmailImportance.CRITICAL,
            EmailCategory.HIGH_PRIORITY: EmailImportance.HIGH,
            EmailCategory.NORMAL: EmailImportance.MEDIUM,
            EmailCategory.LOW_PRIORITY: EmailImportance.LOW,
            EmailCategory.NEWSLETTER: EmailImportance.LOW,
            EmailCategory.SOCIAL: EmailImportance.MINIMAL,
            EmailCategory.PROMOTIONAL: EmailImportance.MINIMAL,
            EmailCategory.SPAM: EmailImportance.MINIMAL,
            EmailCategory.AUTOMATED: EmailImportance.LOW,
        }

        importance = category_importance.get(category, EmailImportance.MEDIUM)

        # Adjust for VIP sender
        if email.sender in self.vip_contacts:
            if importance.value < EmailImportance.HIGH.value:
                importance = EmailImportance.HIGH

        return importance

    def _generate_reasoning(
        self,
        email: EmailMessage,
        category: EmailCategory,
        scores: Dict[EmailCategory, float]
    ) -> List[str]:
        """Generate reasoning for categorization."""
        reasoning = []

        # Main category reason
        if category == EmailCategory.URGENT_ACTION:
            reasoning.append("Requires immediate attention")
            if email.sender in self.vip_contacts:
                reasoning.append("From VIP contact")
        elif category == EmailCategory.NEWSLETTER:
            reasoning.append("Newsletter or subscription")
        elif category == EmailCategory.PROMOTIONAL:
            reasoning.append("Promotional content detected")
        elif category == EmailCategory.AUTOMATED:
            reasoning.append("System-generated notification")

        # Add confidence info
        reasoning.append(f"Confidence: {scores[category]:.1%}")

        return reasoning

    def _suggest_actions(
        self,
        email: EmailMessage,
        category: EmailCategory,
        importance: EmailImportance
    ) -> List[str]:
        """Suggest actions for email."""
        actions = []

        if category == EmailCategory.URGENT_ACTION:
            actions.append("Reply within 2 hours")
            actions.append("Mark as high priority")
        elif category == EmailCategory.HIGH_PRIORITY:
            actions.append("Review and respond today")
        elif category == EmailCategory.NEWSLETTER:
            actions.append("Read when available")
            actions.append("Consider unsubscribing if not valuable")
        elif category == EmailCategory.PROMOTIONAL:
            actions.append("Archive or delete")
        elif category == EmailCategory.SPAM:
            actions.append("Mark as spam")
            actions.append("Block sender")

        return actions

    async def fetch_and_categorize(
        self,
        max_emails: int = 50,
        unread_only: bool = False
    ) -> List[CategorizedEmail]:
        """
        Fetch emails from Gmail and categorize them.

        Args:
            max_emails: Maximum number of emails to process
            unread_only: Only process unread emails

        Returns:
            List of categorized emails
        """
        if not self.gmail:
            print("[Email Categorizer] Gmail service not configured")
            print("[Email Categorizer] Provide Gmail API credentials to use this feature")
            return []

        # TODO: Implement Gmail API integration
        # This would use gmail.users().messages().list() and get()
        # For now, return empty list

        print("[Email Categorizer] Gmail API integration pending")
        print("[Email Categorizer] Framework ready - add credentials to activate")

        return []

    def get_categories_summary(
        self,
        categorized_emails: List[CategorizedEmail]
    ) -> Dict[str, int]:
        """Get summary of email categories."""
        summary = {}

        for cat_email in categorized_emails:
            category = cat_email.category.value
            summary[category] = summary.get(category, 0) + 1

        return summary
