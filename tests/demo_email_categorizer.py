"""
Demo: Email Categorization System
Shows intelligent email organization without needing Gmail API.
"""

import asyncio
from datetime import datetime, timedelta

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.email_categorizer import (
    EmailCategorizer,
    EmailMessage,
    EmailCategory,
    EmailImportance
)


def create_sample_emails() -> list:
    """Create sample emails for testing."""
    now = datetime.now()

    return [
        # Urgent email from CEO
        EmailMessage(
            id="1",
            sender="ceo@company.com",
            sender_name="Jane Doe, CEO",
            subject="URGENT: Q1 Budget Approval Needed ASAP",
            body_preview="We need your approval on the Q1 budget by end of day...",
            received_at=now - timedelta(hours=1),
            has_attachments=True,
            is_read=False,
            labels=[],
            thread_id="thread_1"
        ),

        # High priority client email
        EmailMessage(
            id="2",
            sender="john@client.com",
            sender_name="John Smith",
            subject="Re: Project Deliverables",
            body_preview="Thanks for the update. Can you send the final report...",
            received_at=now - timedelta(hours=3),
            has_attachments=False,
            is_read=False,
            labels=[],
            thread_id="thread_2"
        ),

        # Newsletter
        EmailMessage(
            id="3",
            sender="newsletter@techcrunch.com",
            sender_name="TechCrunch",
            subject="TechCrunch Daily: Top Stories This Week",
            body_preview="Your weekly digest of technology news. Unsubscribe anytime...",
            received_at=now - timedelta(days=1),
            has_attachments=False,
            is_read=False,
            labels=[],
            thread_id="thread_3"
        ),

        # Social notification
        EmailMessage(
            id="4",
            sender="notify@linkedin.com",
            sender_name="LinkedIn",
            subject="John Smith liked your post",
            body_preview="John Smith and 15 others liked your recent post about...",
            received_at=now - timedelta(hours=6),
            has_attachments=False,
            is_read=True,
            labels=[],
            thread_id="thread_4"
        ),

        # Promotional
        EmailMessage(
            id="5",
            sender="sales@store.com",
            sender_name="Store",
            subject="50% OFF SALE - Limited Time Only!",
            body_preview="Don't miss out! Save 50% on all items. Shop now...",
            received_at=now - timedelta(hours=12),
            has_attachments=False,
            is_read=False,
            labels=[],
            thread_id="thread_5"
        ),

        # Automated notification
        EmailMessage(
            id="6",
            sender="no-reply@github.com",
            sender_name="GitHub",
            subject="[Security] New device sign-in detected",
            body_preview="A new device signed in to your GitHub account...",
            received_at=now - timedelta(hours=2),
            has_attachments=False,
            is_read=False,
            labels=[],
            thread_id="thread_6"
        ),

        # Spam
        EmailMessage(
            id="7",
            sender="winner@lottery.com",
            sender_name="Lottery Winner",
            subject="CONGRATULATIONS!!! YOU WON $1,000,000!!!",
            body_preview="Click here to claim your prize now! Free money waiting...",
            received_at=now - timedelta(days=2),
            has_attachments=False,
            is_read=False,
            labels=[],
            thread_id="thread_7"
        ),

        # Normal work email
        EmailMessage(
            id="8",
            sender="colleague@company.com",
            sender_name="Alice Johnson",
            subject="Team Meeting Notes",
            body_preview="Attached are the notes from today's team meeting...",
            received_at=now - timedelta(hours=4),
            has_attachments=True,
            is_read=False,
            labels=[],
            thread_id="thread_8"
        ),
    ]


async def demo_email_categorization():
    """Demo email categorization."""
    print("\n" + "="*70)
    print("EMAIL CATEGORIZATION SYSTEM - DEMO")
    print("="*70)

    # Initialize categorizer
    categorizer = EmailCategorizer(
        gmail_service=None,  # Not needed for demo
        vip_contacts=["ceo@company.com", "john@client.com"]
    )

    print("\n[Initialized] Email Categorizer")
    print(f"VIP Contacts: {len(categorizer.vip_contacts)}")

    # Create sample emails
    sample_emails = create_sample_emails()
    print(f"\n[Created] {len(sample_emails)} sample emails")

    # Categorize each email
    print("\n" + "="*70)
    print("CATEGORIZATION RESULTS")
    print("="*70)

    categorized = []
    for email in sample_emails:
        result = await categorizer.categorize_email(email)
        categorized.append(result)

        # Display result
        print(f"\n[Email {email.id}] From: {email.sender}")
        print(f"Subject: {email.subject}")
        print(f"\nCategory: {result.category.value.upper().replace('_', ' ')}")
        print(f"Importance: {result.importance.name}")
        print(f"Confidence: {result.confidence:.1%}")

        print(f"\nReasoning:")
        for reason in result.reasoning:
            print(f"  - {reason}")

        if result.suggested_actions:
            print(f"\nSuggested Actions:")
            for action in result.suggested_actions:
                print(f"  - {action}")

        print("-" * 70)

    return categorized


async def demo_category_summary():
    """Demo category summary."""
    print("\n\n" + "="*70)
    print("CATEGORY SUMMARY")
    print("="*70)

    categorizer = EmailCategorizer(
        vip_contacts=["ceo@company.com", "john@client.com"]
    )

    sample_emails = create_sample_emails()
    categorized = []

    for email in sample_emails:
        result = await categorizer.categorize_email(email)
        categorized.append(result)

    # Get summary
    summary = categorizer.get_categories_summary(categorized)

    print(f"\nTotal Emails: {len(categorized)}")
    print("\nBreakdown by Category:")

    for category, count in sorted(summary.items(), key=lambda x: -x[1]):
        category_display = category.replace('_', ' ').title()
        print(f"  {category_display}: {count} email(s)")

    # By importance
    importance_counts = {}
    for cat_email in categorized:
        imp = cat_email.importance.name
        importance_counts[imp] = importance_counts.get(imp, 0) + 1

    print("\nBreakdown by Importance:")
    for importance in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "MINIMAL"]:
        count = importance_counts.get(importance, 0)
        if count > 0:
            print(f"  {importance}: {count} email(s)")


async def demo_features():
    """Demo system features."""
    print("\n\n" + "="*70)
    print("EMAIL CATEGORIZER FEATURES")
    print("="*70)

    print("\nCategories:")
    print("  1. URGENT ACTION - Needs immediate response")
    print("  2. HIGH PRIORITY - Important, do today")
    print("  3. NORMAL - Regular emails")
    print("  4. LOW PRIORITY - FYI, low importance")
    print("  5. NEWSLETTER - Subscriptions, updates")
    print("  6. SOCIAL - Social media notifications")
    print("  7. PROMOTIONAL - Marketing, sales")
    print("  8. SPAM - Spam or unwanted")
    print("  9. AUTOMATED - System-generated")

    print("\nImportance Levels:")
    print("  - CRITICAL (5): Must handle immediately")
    print("  - HIGH (4): Handle today")
    print("  - MEDIUM (3): Handle this week")
    print("  - LOW (2): Handle when available")
    print("  - MINIMAL (1): Optional reading")

    print("\nCategorization Factors:")
    print("  - Sender importance (VIP contacts)")
    print("  - Subject keywords (urgent, important, etc.)")
    print("  - Content analysis")
    print("  - Sender domain patterns")
    print("  - Time received (recency)")
    print("  - Attachment presence")
    print("  - Read/unread status")

    print("\nSuggested Actions:")
    print("  - Reply timeframes")
    print("  - Priority marking")
    print("  - Archive/delete suggestions")
    print("  - Unsubscribe recommendations")
    print("  - Spam reporting")

    print("\nIntegration (Coming Soon):")
    print("  - Gmail API for automatic processing")
    print("  - Learning from user corrections")
    print("  - Contact importance scoring")
    print("  - Auto-labeling and filtering")


async def main():
    """Run all demos."""
    # Demo 1: Email categorization
    await demo_email_categorization()

    # Demo 2: Category summary
    await demo_category_summary()

    # Demo 3: Features overview
    await demo_features()

    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\nThe Email Categorizer provides:")
    print("  - Intelligent email categorization")
    print("  - 9 distinct categories")
    print("  - 5 importance levels")
    print("  - VIP contact handling")
    print("  - Suggested actions")
    print("  - Framework ready for Gmail API")
    print("\nAdd Gmail API credentials to activate!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
