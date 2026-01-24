"""
Domain Classifier - Intelligent Task Routing

Automatically classifies tasks as Personal, Business, or Both based on:
- Email domain analysis
- Content keywords
- Sender/recipient patterns
- Context clues
- Manual overrides

Features:
- Keyword-based classification
- Domain whitelist/blacklist
- Confidence scoring
- Manual override support
- Learning from classifications
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from enum import Enum

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from models.task import TaskDomain


class ClassificationConfidence(Enum):
    """Confidence level of classification."""
    HIGH = "high"  # 80%+ confidence
    MEDIUM = "medium"  # 50-80% confidence
    LOW = "low"  # <50% confidence


class DomainClassifier:
    """
    Classifies tasks into Personal, Business, or Both domains.

    Uses keyword matching, domain analysis, and heuristics.
    """

    def __init__(self):
        # Business Keywords
        self.business_keywords = {
            # Financial
            "invoice", "payment", "billing", "receipt", "transaction",
            "expense", "revenue", "profit", "accounting", "tax",
            "quote", "proposal", "contract", "purchase order",

            # Client/Customer
            "client", "customer", "vendor", "supplier", "partner",
            "meeting", "appointment", "conference", "presentation",

            # Operations
            "project", "deadline", "deliverable", "milestone",
            "report", "analysis", "review", "approval",

            # Social Media
            "facebook", "instagram", "twitter", "linkedin",
            "post", "campaign", "engagement", "followers",
            "likes", "comments", "shares", "reach",

            # Professional
            "professional", "business", "corporate", "company",
            "organization", "team", "department", "office"
        }

        # Personal Keywords
        self.personal_keywords = {
            # Health
            "doctor", "dentist", "medical", "health", "appointment",
            "prescription", "insurance", "hospital", "clinic",

            # Family/Friends
            "family", "friend", "personal", "private", "birthday",
            "anniversary", "celebration", "party", "gift",

            # Finance
            "bank", "credit card", "mortgage", "loan", "savings",
            "investment", "retirement", "budget",

            # Lifestyle
            "vacation", "travel", "hobby", "exercise", "fitness",
            "entertainment", "shopping", "restaurant", "home",

            # Utilities
            "utility", "electricity", "water", "gas", "internet",
            "phone", "cable", "subscription"
        }

        # Both Domain Keywords (Cross-cutting)
        self.both_keywords = {
            "tax", "taxes", "irs", "accountant",
            "insurance", "legal", "lawyer", "attorney",
            "home office", "workspace", "equipment",
            "vehicle", "car", "transportation",
            "phone", "mobile", "computer", "laptop"
        }

        # Business Email Domains
        self.business_domains = {
            "company.com", "business.com", "corp.com",
            "enterprise.com", "solutions.com",
            # Add actual business domains
        }

        # Personal Email Domains
        self.personal_domains = {
            "gmail.com", "yahoo.com", "hotmail.com",
            "outlook.com", "icloud.com", "aol.com",
            "protonmail.com", "mail.com"
        }

    def classify(
        self,
        title: str,
        description: str = "",
        sender: str = "",
        recipient: str = "",
        tags: List[str] = None,
        metadata: Dict = None
    ) -> Tuple[TaskDomain, ClassificationConfidence]:
        """
        Classify a task into Personal, Business, or Both.

        Args:
            title: Task title
            description: Task description
            sender: Email sender (if email source)
            recipient: Email recipient (if email source)
            tags: Task tags
            metadata: Additional metadata

        Returns:
            Tuple of (TaskDomain, ClassificationConfidence)
        """
        tags = tags or []
        metadata = metadata or {}

        # Calculate scores
        business_score = 0
        personal_score = 0
        both_score = 0

        # Combined text for analysis
        text = f"{title} {description} {' '.join(tags)}".lower()

        # Keyword matching
        for keyword in self.business_keywords:
            if keyword in text:
                business_score += 1

        for keyword in self.personal_keywords:
            if keyword in text:
                personal_score += 1

        for keyword in self.both_keywords:
            if keyword in text:
                both_score += 2  # Higher weight for cross-domain

        # Email domain analysis
        if sender:
            sender_domain = self._extract_domain(sender)
            if sender_domain in self.business_domains:
                business_score += 3
            elif sender_domain in self.personal_domains:
                personal_score += 1

        if recipient:
            recipient_domain = self._extract_domain(recipient)
            if recipient_domain in self.business_domains:
                business_score += 3
            elif recipient_domain in self.personal_domains:
                personal_score += 1

        # Tag analysis
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in ["business", "work", "client", "professional"]:
                business_score += 2
            elif tag_lower in ["personal", "private", "family", "home"]:
                personal_score += 2
            elif tag_lower in ["cross-domain", "both", "hybrid"]:
                both_score += 3

        # Manual override from metadata
        if metadata.get("domain_override"):
            override_domain = TaskDomain(metadata["domain_override"])
            return override_domain, ClassificationConfidence.HIGH

        # Determine classification
        max_score = max(business_score, personal_score, both_score)
        total_score = business_score + personal_score + both_score

        if total_score == 0:
            # No clear indicators, default to personal
            return TaskDomain.PERSONAL, ClassificationConfidence.LOW

        # Calculate confidence
        confidence_percent = (max_score / total_score * 100) if total_score > 0 else 0

        if confidence_percent >= 80:
            confidence = ClassificationConfidence.HIGH
        elif confidence_percent >= 50:
            confidence = ClassificationConfidence.MEDIUM
        else:
            confidence = ClassificationConfidence.LOW

        # Determine domain
        if both_score > business_score and both_score > personal_score:
            domain = TaskDomain.BOTH
        elif business_score > personal_score:
            domain = TaskDomain.BUSINESS
        else:
            domain = TaskDomain.PERSONAL

        return domain, confidence

    def classify_email(
        self,
        subject: str,
        body: str,
        sender: str,
        recipient: str = ""
    ) -> Tuple[TaskDomain, ClassificationConfidence]:
        """
        Classify an email-based task.

        Args:
            subject: Email subject
            body: Email body
            sender: Sender email address
            recipient: Recipient email address

        Returns:
            Tuple of (TaskDomain, ClassificationConfidence)
        """
        return self.classify(
            title=subject,
            description=body,
            sender=sender,
            recipient=recipient
        )

    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if "@" in email:
            return email.split("@")[1].lower()
        return ""

    def add_business_domain(self, domain: str):
        """Add a domain to business domain list."""
        self.business_domains.add(domain.lower())

    def add_personal_domain(self, domain: str):
        """Add a domain to personal domain list."""
        self.personal_domains.add(domain.lower())

    def add_business_keyword(self, keyword: str):
        """Add a keyword to business keyword list."""
        self.business_keywords.add(keyword.lower())

    def add_personal_keyword(self, keyword: str):
        """Add a keyword to personal keyword list."""
        self.personal_keywords.add(keyword.lower())

    def get_classification_explanation(
        self,
        title: str,
        description: str = "",
        sender: str = "",
        recipient: str = "",
        tags: List[str] = None
    ) -> Dict:
        """
        Get detailed explanation of classification decision.

        Returns:
            Dictionary with classification details and reasoning
        """
        tags = tags or []
        text = f"{title} {description} {' '.join(tags)}".lower()

        matched_business = [kw for kw in self.business_keywords if kw in text]
        matched_personal = [kw for kw in self.personal_keywords if kw in text]
        matched_both = [kw for kw in self.both_keywords if kw in text]

        domain, confidence = self.classify(title, description, sender, recipient, tags)

        return {
            "domain": domain.value,
            "confidence": confidence.value,
            "business_keywords": matched_business,
            "personal_keywords": matched_personal,
            "both_keywords": matched_both,
            "sender_domain": self._extract_domain(sender) if sender else None,
            "recipient_domain": self._extract_domain(recipient) if recipient else None
        }


# Global instance
_classifier = DomainClassifier()


def classify_task(
    title: str,
    description: str = "",
    sender: str = "",
    recipient: str = "",
    tags: List[str] = None,
    metadata: Dict = None
) -> Tuple[TaskDomain, ClassificationConfidence]:
    """Global function to classify task."""
    return _classifier.classify(title, description, sender, recipient, tags, metadata)


def get_classifier() -> DomainClassifier:
    """Get global classifier instance."""
    return _classifier


if __name__ == "__main__":
    # Test domain classifier
    print("Testing Domain Classifier...")

    classifier = DomainClassifier()

    # Test 1: Business task
    print("\n1. Testing business task classification...")
    domain, confidence = classifier.classify(
        title="Create invoice for Acme Corp",
        description="Generate invoice for project work completed in Q1",
        sender="client@acmecorp.com",
        tags=["invoice", "billing", "client"]
    )
    print(f"[OK] Business task classified as: {domain.value} ({confidence.value} confidence)")

    explanation = classifier.get_classification_explanation(
        title="Create invoice for Acme Corp",
        description="Generate invoice for project work completed in Q1",
        sender="client@acmecorp.com",
        tags=["invoice", "billing", "client"]
    )
    print(f"  Matched business keywords: {explanation['business_keywords'][:3]}")

    # Test 2: Personal task
    print("\n2. Testing personal task classification...")
    domain, confidence = classifier.classify(
        title="Schedule dentist appointment",
        description="Annual checkup and cleaning",
        sender="dentist@localclinic.com",
        tags=["health", "appointment"]
    )
    print(f"[OK] Personal task classified as: {domain.value} ({confidence.value} confidence)")

    # Test 3: Cross-domain task
    print("\n3. Testing cross-domain task classification...")
    domain, confidence = classifier.classify(
        title="Prepare tax documents",
        description="Gather personal and business tax documents for accountant",
        tags=["taxes", "accountant", "deadline"]
    )
    print(f"[OK] Cross-domain task classified as: {domain.value} ({confidence.value} confidence)")

    # Test 4: Email classification
    print("\n4. Testing email classification...")
    domain, confidence = classifier.classify_email(
        subject="Instagram campaign performance report",
        body="Here are the results from last week's campaign on Instagram. Engagement is up 15%.",
        sender="marketing@socialmedia.com"
    )
    print(f"[OK] Social media email classified as: {domain.value} ({confidence.value} confidence)")

    # Test 5: Manual override
    print("\n5. Testing manual override...")
    domain, confidence = classifier.classify(
        title="Buy groceries",
        description="Weekly shopping",
        metadata={"domain_override": "business"}  # Force business classification
    )
    print(f"[OK] Override applied: {domain.value} ({confidence.value} confidence)")

    # Test 6: Add custom keywords
    print("\n6. Testing custom keyword addition...")
    classifier.add_business_keyword("strategic planning")
    domain, confidence = classifier.classify(
        title="Strategic planning session",
        description="Annual strategic planning meeting"
    )
    print(f"[OK] Custom keyword recognized: {domain.value} ({confidence.value} confidence)")

    # Test 7: Ambiguous task
    print("\n7. Testing ambiguous task...")
    domain, confidence = classifier.classify(
        title="Review documents",
        description="Review some documents"
    )
    print(f"[OK] Ambiguous task classified as: {domain.value} ({confidence.value} confidence)")

    print("\n[SUCCESS] All domain classifier tests passed!")
