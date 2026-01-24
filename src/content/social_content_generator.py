"""
Social Media Content Generator

Generates platform-optimized content for:
- Facebook (longer posts with links)
- Instagram (visual focus, hashtags)
- Twitter (concise, threads)
- LinkedIn (already exists)

Features:
- Platform-specific formatting
- Hashtag optimization
- Content from CEO briefing
- Industry tips and insights
- Engagement content
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from jinja2 import Environment, FileSystemLoader

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configuration
VAULT_PATH = PROJECT_ROOT / "Vault"
TEMPLATES_DIR = PROJECT_ROOT / "src" / "templates" / "social"
CEO_BRIEFING_PATTERN = "CEO_Briefing_*.md"

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SocialContentGenerator")

# Ensure template directory
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


class SocialContentGenerator:
    """Generate platform-specific social media content."""

    def __init__(self):
        self.templates_dir = TEMPLATES_DIR
        self.vault_path = VAULT_PATH

    def _load_ceo_briefing(self, date: str = None) -> Dict:
        """Load latest CEO briefing data."""
        if date:
            briefing_file = self.vault_path / f"CEO_Briefing_{date}.md"
        else:
            # Find latest briefing
            briefings = sorted(self.vault_path.glob(CEO_BRIEFING_PATTERN))
            if not briefings:
                return {}
            briefing_file = briefings[-1]

        try:
            with open(briefing_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Parse briefing for key metrics
                # This is simplified - full implementation would parse markdown
                return {
                    "content": content,
                    "date": briefing_file.stem.replace("CEO_Briefing_", "")
                }
        except Exception as e:
            logger.error(f"Failed to load CEO briefing: {e}")
            return {}

    def _get_hashtags(self, platform: str, topic: str) -> List[str]:
        """Get platform-optimized hashtags."""
        # Base hashtags
        base_tags = {
            "business": ["Business", "Entrepreneurship", "Success"],
            "ai": ["AI", "Automation", "Technology", "Innovation"],
            "productivity": ["Productivity", "Efficiency", "WorkSmart"],
            "social_media": ["SocialMedia", "Marketing", "DigitalMarketing"],
        }

        # Platform-specific strategies
        if platform == "instagram":
            # Instagram allows and benefits from more hashtags
            tags = base_tags.get(topic, ["Business"])
            # Add trending tags
            tags.extend(["BusinessGrowth", "Motivation", "Goals"])
            return tags[:30]  # Max 30 hashtags on Instagram

        elif platform == "twitter":
            # Twitter: fewer, more targeted hashtags
            return base_tags.get(topic, ["Business"])[:3]

        elif platform == "facebook":
            # Facebook: minimal hashtags
            return base_tags.get(topic, ["Business"])[:2]

        elif platform == "linkedin":
            # LinkedIn: professional hashtags
            return base_tags.get(topic, ["Business", "Professional"])[:5]

        return []

    def generate_facebook_post(self, content_type: str, data: Dict = None) -> Dict:
        """
        Generate Facebook post.

        Args:
            content_type: 'business_update', 'tip', 'engagement', 'ceo_briefing'
            data: Optional data dictionary

        Returns:
            Dict with 'content', 'link', 'hashtags'
        """
        if content_type == "ceo_briefing":
            briefing = self._load_ceo_briefing(data.get("date") if data else None)
            if not briefing:
                return {"error": "No CEO briefing found"}

            # Extract key metrics (simplified)
            content = f"""📊 Weekly Business Update

This week's highlights:
• Automated processes running smoothly
• Key metrics tracking on schedule
• Strategic planning in progress

Check out the full briefing for detailed insights!

#Business #Automation #WeeklyUpdate"""

        elif content_type == "tip":
            tip_text = data.get("tip", "Stay focused on your goals") if data else "Stay focused on your goals"
            content = f"""💡 Business Tip

{tip_text}

What strategies are you using this week? Share in the comments!

#BusinessTips #Entrepreneurship"""

        elif content_type == "engagement":
            question = data.get("question", "What's your biggest business challenge?") if data else "What's your biggest business challenge?"
            content = f"""🤔 Question for You

{question}

Drop your thoughts in the comments - let's discuss!

#BusinessCommunity #Discussion"""

        else:
            content = data.get("content", "") if data else ""

        return {
            "content": content,
            "link": data.get("link") if data else None,
            "hashtags": self._get_hashtags("facebook", "business")
        }

    def generate_instagram_post(self, content_type: str, data: Dict = None) -> Dict:
        """
        Generate Instagram post (requires image).

        Args:
            content_type: 'quote', 'stat', 'tip', 'achievement'
            data: Optional data dictionary with 'image_url'

        Returns:
            Dict with 'caption', 'image_url', 'hashtags'
        """
        if content_type == "quote":
            quote = data.get("quote", "Success is a journey, not a destination") if data else "Success is a journey, not a destination"
            author = data.get("author", "Unknown") if data else "Unknown"

            caption = f""""{quote}"
- {author}

Follow for daily inspiration! 💪"""

        elif content_type == "stat":
            stat = data.get("stat", "3 hours saved per week with automation") if data else "3 hours saved per week"
            caption = f"""📈 This Week's Stats

{stat}

Automation is changing the game! 🚀"""

        elif content_type == "tip":
            tip = data.get("tip", "Automate repetitive tasks to focus on strategy") if data else "Automate to focus"
            caption = f"""💡 Pro Tip

{tip}

Save this for later! 📌"""

        else:
            caption = data.get("caption", "") if data else ""

        # Instagram requires images
        image_url = data.get("image_url") if data else None
        if not image_url:
            logger.warning("Instagram post requires image_url")

        hashtags = self._get_hashtags("instagram", "business")

        return {
            "caption": caption,
            "image_url": image_url,
            "hashtags": hashtags
        }

    def generate_twitter_post(self, content_type: str, data: Dict = None) -> Dict:
        """
        Generate Twitter post.

        Args:
            content_type: 'update', 'tip', 'thread', 'announcement'
            data: Optional data dictionary

        Returns:
            Dict with 'content' or 'tweets' (for threads)
        """
        if content_type == "update":
            update = data.get("update", "Making progress on automation goals") if data else "Making progress"
            content = f"""🚀 Quick Update

{update}

#Automation #Progress"""

        elif content_type == "tip":
            tip = data.get("tip", "Automate repetitive tasks") if data else "Automate tasks"
            content = f"""💡 Tip: {tip}

What are you automating this week?

#ProductivityTips"""

        elif content_type == "thread":
            # Return multiple tweets for a thread
            topics = data.get("topics", []) if data else []
            if not topics:
                topics = [
                    "Why automation matters",
                    "It saves time on repetitive tasks",
                    "It reduces human error",
                    "It scales with your business"
                ]

            tweets = [f"{i+1}/{len(topics)} {topic}" for i, topic in enumerate(topics)]
            return {"tweets": tweets, "is_thread": True}

        elif content_type == "announcement":
            announcement = data.get("announcement", "New feature launching soon") if data else "Big news coming"
            content = f"""📢 {announcement}

Stay tuned for updates!

#News #Updates"""

        else:
            content = data.get("content", "") if data else ""

        # Ensure within Twitter's 280 character limit
        if len(content) > 280:
            content = content[:277] + "..."
            logger.warning(f"Tweet truncated to 280 characters")

        return {
            "content": content,
            "hashtags": self._get_hashtags("twitter", "business")
        }

    def generate_cross_platform_campaign(self, campaign_type: str, data: Dict = None) -> Dict:
        """
        Generate coordinated content for all platforms.

        Args:
            campaign_type: 'weekly_update', 'product_launch', 'achievement'
            data: Campaign data

        Returns:
            Dict with content for each platform
        """
        campaign = {
            "facebook": None,
            "instagram": None,
            "twitter": None,
            "linkedin": None
        }

        if campaign_type == "weekly_update":
            # Generate from CEO briefing
            campaign["facebook"] = self.generate_facebook_post("ceo_briefing", data)
            campaign["instagram"] = self.generate_instagram_post("stat", data)
            campaign["twitter"] = self.generate_twitter_post("update", data)
            # LinkedIn already has weekly update template

        elif campaign_type == "achievement":
            achievement = data.get("achievement", "Reached new milestone") if data else "New milestone"

            campaign["facebook"] = self.generate_facebook_post("engagement", {
                "question": f"Excited to share: {achievement}! What milestones are you celebrating?"
            })

            campaign["instagram"] = self.generate_instagram_post("achievement", {
                "caption": f"🎉 {achievement}",
                "image_url": data.get("image_url") if data else None
            })

            campaign["twitter"] = self.generate_twitter_post("announcement", {
                "announcement": achievement
            })

        elif campaign_type == "tip":
            tip = data.get("tip") if data else "Focus on high-impact tasks"

            campaign["facebook"] = self.generate_facebook_post("tip", {"tip": tip})
            campaign["instagram"] = self.generate_instagram_post("tip", {
                "tip": tip,
                "image_url": data.get("image_url") if data else None
            })
            campaign["twitter"] = self.generate_twitter_post("tip", {"tip": tip})

        return campaign

    def save_to_queue(self, platform: str, content: Dict, filename: str = None) -> str:
        """Save generated content to LinkedIn_Queue or social media queue."""
        if not filename:
            filename = f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        # Determine queue path
        if platform == "linkedin":
            queue_path = self.vault_path / "LinkedIn_Queue"
        else:
            queue_path = self.vault_path / "Social_Queue" / platform
            queue_path.mkdir(parents=True, exist_ok=True)

        filepath = queue_path / filename

        # Format content as markdown
        if platform == "facebook":
            md_content = f"""---
platform: facebook
type: post
created: {datetime.now().isoformat()}
status: queued
---

# Facebook Post

{content.get('content', '')}

{f"**Link:** {content.get('link')}" if content.get('link') else ''}
"""

        elif platform == "instagram":
            md_content = f"""---
platform: instagram
type: post
created: {datetime.now().isoformat()}
status: queued
image_url: {content.get('image_url', '')}
---

# Instagram Post

## Caption
{content.get('caption', '')}

## Hashtags
{' '.join(['#' + tag for tag in content.get('hashtags', [])])}
"""

        elif platform == "twitter":
            if content.get("is_thread"):
                tweets_text = "\n\n".join([f"**Tweet {i+1}:** {t}" for i, t in enumerate(content.get('tweets', []))])
                md_content = f"""---
platform: twitter
type: thread
created: {datetime.now().isoformat()}
status: queued
---

# Twitter Thread

{tweets_text}
"""
            else:
                md_content = f"""---
platform: twitter
type: tweet
created: {datetime.now().isoformat()}
status: queued
---

# Tweet

{content.get('content', '')}
"""

        else:
            md_content = json.dumps(content, indent=2)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Saved {platform} content to {filepath}")
        return str(filepath)


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate social media content")
    parser.add_argument("--platform", choices=["facebook", "instagram", "twitter", "all"], required=True)
    parser.add_argument("--type", required=True, help="Content type")
    parser.add_argument("--data", help="JSON data for content generation")
    parser.add_argument("--save", action="store_true", help="Save to queue")

    args = parser.parse_args()

    generator = SocialContentGenerator()

    if args.data:
        data = json.loads(args.data)
    else:
        data = None

    if args.platform == "facebook":
        result = generator.generate_facebook_post(args.type, data)
    elif args.platform == "instagram":
        result = generator.generate_instagram_post(args.type, data)
    elif args.platform == "twitter":
        result = generator.generate_twitter_post(args.type, data)
    elif args.platform == "all":
        result = generator.generate_cross_platform_campaign(args.type, data)

    print(json.dumps(result, indent=2))

    if args.save and args.platform != "all":
        filepath = generator.save_to_queue(args.platform, result)
        print(f"\nSaved to: {filepath}")
