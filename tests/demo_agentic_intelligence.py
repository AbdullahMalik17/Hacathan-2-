"""
Demo: Agentic Intelligence Layer

This demo shows how the agent analyzes tasks and decides approach.
No API keys needed - uses rule-based analysis.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.intelligence.agentic_intelligence import AgenticIntelligence
from src.storage.learning_db import LearningDatabase


async def demo_task(intelligence: AgenticIntelligence, request: str):
    """Demo a single task."""
    print(f"\n{'='*70}")
    print(f"User Request: {request}")
    print(f"{'='*70}")

    # Get decision
    decision = await intelligence.decide(request)

    # Print explanation
    explanation = await intelligence.explain_decision(decision)
    print(explanation)

    # Print decision dict
    print(f"\nDecision Summary:")
    for key, value in decision.to_dict().items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")


async def main():
    """Run demo."""
    print("\n" + "="*70)
    print("AGENTIC INTELLIGENCE LAYER - DEMO")
    print("="*70)
    print("\nThis demo shows how the agent analyzes tasks and decides:")
    print("  - EXECUTE DIRECTLY (simple, safe tasks)")
    print("  - SPEC-DRIVEN (complex or risky tasks)")
    print("  - CLARIFICATION NEEDED (ambiguous tasks)")
    print("\n" + "="*70)

    # Initialize
    db = LearningDatabase("Vault/Data/learning_demo.db")
    intelligence = AgenticIntelligence(
        ai_client=None,  # No AI needed for demo
        history_db=db,
        handbook_rules={
            'auto_approve_max_amount': 100
        }
    )

    # Test cases
    test_cases = [
        # Simple tasks (should execute directly)
        "Send email to john@example.com saying hello",
        "Play my focus playlist on Spotify",
        "Schedule meeting with team tomorrow at 2pm",

        # Complex tasks (should create spec)
        "Build a multi-step sales pipeline in Odoo with automated follow-ups and reporting",
        "Create a comprehensive LinkedIn content series about AI trends",
        "Implement automated expense tracking system",

        # Risky tasks (should create spec)
        "Transfer $5000 to vendor account",
        "Post announcement about company restructuring on all social media",
        "Delete all archived emails older than 2 years",

        # Ambiguous tasks (should ask for clarification)
        "Handle that thing we discussed",
        "Do what we talked about yesterday",
        "Make it better",
    ]

    for request in test_cases:
        await demo_task(intelligence, request)
        await asyncio.sleep(0.5)  # Pause between demos

    # Summary
    print(f"\n{'='*70}")
    print("DEMO COMPLETE")
    print("="*70)
    print("\nKey Takeaways:")
    print("  1. Simple tasks -> Execute directly (fast, efficient)")
    print("  2. Complex tasks -> Create spec first (safe, organized)")
    print("  3. Risky tasks -> Create spec first (safety, approval)")
    print("  4. Ambiguous tasks -> Ask for clarification (no guessing)")
    print("\nThis intelligence layer enables true agentic behavior!")
    print("="*70 + "\n")

    # Cleanup
    db.close()


if __name__ == "__main__":
    asyncio.run(main())
