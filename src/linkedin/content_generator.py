"""
LinkedIn Content Generator - Digital FTE

This module generates LinkedIn posts from various sources:
- CEO Briefing reports (weekly metrics)
- Manual content queue
- Templates with variable substitution
"""

import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound
except ImportError:
    print("Jinja2 not installed. Run: pip install jinja2")

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "Vault"
TEMPLATES_PATH = PROJECT_ROOT / "src" / "templates" / "linkedin"
LINKEDIN_QUEUE_PATH = VAULT_PATH / "LinkedIn_Queue"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
LOGS_PATH = VAULT_PATH / "Logs"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ContentGenerator")


# Hashtag suggestions by topic
HASHTAG_SUGGESTIONS = {
    "automation": ["#AIAutomation", "#Automation", "#DigitalTransformation", "#Productivity"],
    "email": ["#EmailManagement", "#InboxZero", "#Productivity", "#WorkSmart"],
    "ai": ["#ArtificialIntelligence", "#AI", "#MachineLearning", "#FutureOfWork"],
    "productivity": ["#Productivity", "#WorkLifeBalance", "#Efficiency", "#TimeManagement"],
    "business": ["#Business", "#Entrepreneurship", "#SmallBusiness", "#Growth"],
    "tech": ["#Technology", "#TechNews", "#Innovation", "#DigitalAge"],
    "metrics": ["#DataDriven", "#Analytics", "#Metrics", "#Performance"],
    "workflow": ["#Workflow", "#ProcessAutomation", "#Efficiency", "#Operations"]
}

# Character limits
LINKEDIN_POST_LIMIT = 3000
IDEAL_POST_LENGTH = 1300  # Optimal for engagement


class ContentGenerator:
    """Generate LinkedIn posts from various sources."""

    def __init__(self):
        self.templates_path = TEMPLATES_PATH
        self.jinja_env = None
        self._init_jinja()

    def _init_jinja(self):
        """Initialize Jinja2 environment."""
        if self.templates_path.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_path)),
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            logger.warning(f"Templates path not found: {self.templates_path}")

    def from_ceo_briefing(self, briefing_path: Path = None) -> Optional[str]:
        """
        Extract key metrics from CEO Briefing and create a professional post.

        Args:
            briefing_path: Path to CEO Briefing file. If None, uses latest.

        Returns:
            Generated post content or None if no briefing found.
        """
        # Find latest CEO briefing if not specified
        if briefing_path is None:
            briefings = list(VAULT_PATH.glob("CEO_Briefing_*.md"))
            if not briefings:
                logger.warning("No CEO Briefing files found")
                return None
            briefing_path = max(briefings, key=lambda p: p.stat().st_mtime)

        if not briefing_path.exists():
            logger.error(f"Briefing file not found: {briefing_path}")
            return None

        try:
            content = briefing_path.read_text(encoding="utf-8")

            # Extract metrics from briefing
            metrics = self._extract_metrics(content)

            if not metrics:
                logger.warning("Could not extract metrics from briefing")
                return None

            # Generate post using template or fallback
            post = self._generate_metrics_post(metrics)

            return post

        except Exception as e:
            logger.error(f"Error processing briefing: {e}")
            return None

    def _extract_metrics(self, briefing_content: str) -> Dict[str, Any]:
        """Extract key metrics from CEO Briefing content."""
        metrics = {}

        # Extract total activities
        activity_match = re.search(r'Total Activities[:\s]*\*?\*?(\d+)', briefing_content)
        if activity_match:
            metrics["total_activities"] = int(activity_match.group(1))

        # Extract by source
        source_pattern = r'\|\s*(Gmail|WhatsApp|Filesystem|Orchestrator)\s*\|\s*(\d+)\s*\|'
        sources = re.findall(source_pattern, briefing_content)
        if sources:
            metrics["by_source"] = {src: int(count) for src, count in sources}

        # Extract pending items
        pending_match = re.search(r'Pending Items[:\s]*(\d+)', briefing_content, re.IGNORECASE)
        if pending_match:
            metrics["pending_items"] = int(pending_match.group(1))

        # Extract status
        if "System Online" in briefing_content:
            metrics["status"] = "healthy"
        elif "degraded" in briefing_content.lower():
            metrics["status"] = "degraded"
        else:
            metrics["status"] = "unknown"

        # Extract report date
        date_match = re.search(r'Report Date[:\s]*(\d{4}-\d{2}-\d{2})', briefing_content)
        if date_match:
            metrics["report_date"] = date_match.group(1)
        else:
            metrics["report_date"] = datetime.now().strftime("%Y-%m-%d")

        # Extract period
        period_match = re.search(r'Period[:\s]*(\d+)\s*days', briefing_content)
        if period_match:
            metrics["period_days"] = int(period_match.group(1))
        else:
            metrics["period_days"] = 7

        return metrics

    def _generate_metrics_post(self, metrics: Dict[str, Any]) -> str:
        """Generate LinkedIn post from extracted metrics."""
        # Try template first
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template("weekly_update.j2")
                return template.render(**metrics)
            except TemplateNotFound:
                pass

        # Fallback to hardcoded generation
        total = metrics.get("total_activities", 0)
        by_source = metrics.get("by_source", {})
        period = metrics.get("period_days", 7)

        post_lines = [
            f"Weekly AI Automation Update",
            "",
            f"This week, my Digital FTE (AI Employee) handled:",
            ""
        ]

        if by_source:
            for source, count in by_source.items():
                emoji = self._get_source_emoji(source)
                post_lines.append(f"{emoji} {count} {source} activities")

        if total > 0:
            hours_saved = round(total * 2 / 60, 1)  # Estimate 2 min per task
            post_lines.extend([
                "",
                f"Total: {total} automated tasks in {period} days",
                f"Estimated time saved: ~{hours_saved} hours",
                "",
                "The future of work is here - AI handling the mundane so we can focus on what matters.",
                ""
            ])

        # Add hashtags
        post_lines.append("#AIAutomation #Productivity #DigitalTransformation #FutureOfWork")

        return "\n".join(post_lines)

    def _get_source_emoji(self, source: str) -> str:
        """Get emoji for source type."""
        emojis = {
            "gmail": "📧",
            "whatsapp": "💬",
            "filesystem": "📁",
            "orchestrator": "🤖",
            "email": "📧"
        }
        return emojis.get(source.lower(), "📌")

    def from_template(self, template_name: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Render a Jinja2 template with provided variables.

        Args:
            template_name: Name of template file (e.g., "achievement.j2")
            variables: Dictionary of variables to pass to template

        Returns:
            Rendered content or None if template not found.
        """
        if not self.jinja_env:
            logger.error("Jinja2 environment not initialized")
            return None

        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**variables)
        except TemplateNotFound:
            logger.error(f"Template not found: {template_name}")
            return None
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return None

    def suggest_hashtags(self, content: str, max_hashtags: int = 5) -> List[str]:
        """
        Suggest relevant hashtags based on content.

        Args:
            content: Post content to analyze
            max_hashtags: Maximum number of hashtags to suggest

        Returns:
            List of suggested hashtags.
        """
        content_lower = content.lower()
        suggested = set()

        for topic, hashtags in HASHTAG_SUGGESTIONS.items():
            if topic in content_lower:
                suggested.update(hashtags[:2])

        # Always include core hashtags for Digital FTE content
        core_hashtags = ["#AI", "#Automation", "#Productivity"]
        suggested.update(core_hashtags)

        return list(suggested)[:max_hashtags]

    def validate_post(self, content: str) -> tuple[bool, List[str]]:
        """
        Validate post content for LinkedIn.

        Args:
            content: Post content to validate

        Returns:
            Tuple of (is_valid, list of warnings/errors)
        """
        issues = []

        # Check length
        if len(content) > LINKEDIN_POST_LIMIT:
            issues.append(f"Post exceeds {LINKEDIN_POST_LIMIT} character limit ({len(content)} chars)")

        if len(content) > IDEAL_POST_LENGTH:
            issues.append(f"Post may be too long for optimal engagement ({len(content)} chars, ideal: {IDEAL_POST_LENGTH})")

        # Check for empty content
        if not content.strip():
            issues.append("Post content is empty")

        # Check for hashtags
        hashtag_count = len(re.findall(r'#\w+', content))
        if hashtag_count == 0:
            issues.append("No hashtags found - consider adding 3-5 relevant hashtags")
        elif hashtag_count > 10:
            issues.append("Too many hashtags (>10) may look spammy")

        # Check for call-to-action
        cta_patterns = ['?', 'comment', 'share', 'thoughts', 'agree', 'let me know']
        has_cta = any(p in content.lower() for p in cta_patterns)
        if not has_cta:
            issues.append("Consider adding a call-to-action for better engagement")

        is_valid = not any("exceeds" in issue or "empty" in issue for issue in issues)

        return is_valid, issues

    def create_approval_file(self, content: str, source: str = "manual",
                            scheduled_time: datetime = None) -> Path:
        """
        Create a LinkedIn post file in Pending_Approval folder.

        Args:
            content: Post content
            source: Source of content (ceo_briefing, manual, template)
            scheduled_time: Optional scheduled posting time

        Returns:
            Path to created approval file.
        """
        PENDING_APPROVAL_PATH.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"LinkedIn_{timestamp}_{source}.md"
        filepath = PENDING_APPROVAL_PATH / filename

        scheduled_str = scheduled_time.isoformat() if scheduled_time else "null"

        # Validate content
        is_valid, issues = self.validate_post(content)

        file_content = f"""---
type: linkedin_post
source: {source}
scheduled: {scheduled_str}
status: pending_approval
created: {datetime.now().isoformat()}
valid: {is_valid}
---

## Proposed LinkedIn Post

{content}

---

## Validation

"""
        if issues:
            for issue in issues:
                file_content += f"- {issue}\n"
        else:
            file_content += "- All checks passed\n"

        file_content += """
---

## Actions
- [ ] Approve - Move to Approved/
- [ ] Edit - Modify content above
- [ ] Reject - Delete file
"""

        filepath.write_text(file_content, encoding="utf-8")
        logger.info(f"Created approval file: {filepath}")

        return filepath

    def process_queue(self) -> int:
        """
        Process manual posts from LinkedIn_Queue folder.

        Returns:
            Number of posts moved to Pending_Approval.
        """
        processed = 0

        for queue_file in LINKEDIN_QUEUE_PATH.glob("*.md"):
            if queue_file.name.startswith("."):
                continue

            try:
                content = queue_file.read_text(encoding="utf-8")

                # Extract content (after frontmatter)
                if "---" in content:
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        post_content = parts[2].strip()
                    else:
                        post_content = content
                else:
                    post_content = content

                # Create approval file
                self.create_approval_file(post_content, source="queue")

                # Remove from queue
                queue_file.unlink()
                logger.info(f"Processed queue file: {queue_file.name}")
                processed += 1

            except Exception as e:
                logger.error(f"Error processing {queue_file.name}: {e}")

        return processed

    def generate_weekly_post(self) -> Optional[Path]:
        """
        Generate weekly metrics post from latest CEO Briefing.

        Returns:
            Path to created approval file or None.
        """
        content = self.from_ceo_briefing()
        if content:
            return self.create_approval_file(content, source="ceo_briefing")
        return None


def main():
    """Main entry point for content generator."""
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Content Generator")
    parser.add_argument("--weekly", action="store_true",
                        help="Generate weekly metrics post from CEO Briefing")
    parser.add_argument("--process-queue", action="store_true",
                        help="Process manual posts from queue")
    parser.add_argument("--template", type=str,
                        help="Generate from template (provide template name)")
    parser.add_argument("--variables", type=str,
                        help="JSON string of template variables")
    args = parser.parse_args()

    generator = ContentGenerator()

    if args.weekly:
        result = generator.generate_weekly_post()
        if result:
            print(f"Created approval file: {result}")
        else:
            print("Failed to generate weekly post")

    elif args.process_queue:
        count = generator.process_queue()
        print(f"Processed {count} queue items")

    elif args.template:
        variables = json.loads(args.variables) if args.variables else {}
        content = generator.from_template(args.template, variables)
        if content:
            filepath = generator.create_approval_file(content, source="template")
            print(f"Created: {filepath}")
        else:
            print("Failed to generate from template")

    else:
        # Default: process queue and generate weekly if available
        queue_count = generator.process_queue()
        print(f"Processed {queue_count} queue items")

        result = generator.generate_weekly_post()
        if result:
            print(f"Generated weekly post: {result}")


if __name__ == "__main__":
    main()
