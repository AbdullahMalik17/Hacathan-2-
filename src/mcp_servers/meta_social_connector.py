"""
Meta Social MCP Server - Facebook & Instagram Integration

Provides MCP tools for Meta platforms:
- Post to Facebook
- Post to Instagram
- Upload media
- Get engagement insights
- Generate social media summaries

Uses Meta Graph API for all operations.
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from fastmcp import FastMCP

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils.audit_logger import log_audit, AuditDomain, AuditStatus
from utils.error_recovery import retry_with_backoff, RetryConfig, get_circuit_breaker

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Configuration
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v18.0")

VAULT_PATH = PROJECT_ROOT / "Vault"
PENDING_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
LOGS_PATH = VAULT_PATH / "Logs"

# Rate limits (Meta API limits)
MAX_POSTS_PER_DAY = 25
MAX_POSTS_PER_HOUR = 5

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MetaSocialMCP")

# Ensure directories
PENDING_PATH.mkdir(parents=True, exist_ok=True)
APPROVED_PATH.mkdir(parents=True, exist_ok=True)
LOGS_PATH.mkdir(parents=True, exist_ok=True)

# Initialize MCP
mcp = FastMCP("Meta Social Media")


class MetaAPIClient:
    """Manages Meta Graph API connections."""

    def __init__(self, access_token: str, api_version: str = "v18.0"):
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"
        self.session = requests.Session()

    def _make_request(self, method: str, endpoint: str, data: Dict = None, files: Dict = None) -> Dict:
        """Make request to Meta Graph API."""
        url = f"{self.base_url}/{endpoint}"
        params = {"access_token": self.access_token}

        if data:
            params.update(data)

        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                if files:
                    response = self.session.post(url, params=params, files=files)
                else:
                    response = self.session.post(url, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Meta API request failed: {e}")
            raise

    def post_to_page(self, page_id: str, message: str, link: str = None, photo_url: str = None) -> Dict:
        """Post to Facebook page."""
        endpoint = f"{page_id}/feed"
        data = {"message": message}

        if link:
            data["link"] = link
        if photo_url:
            # For photo posts, use photos endpoint instead
            endpoint = f"{page_id}/photos"
            data["url"] = photo_url
            data["caption"] = message

        return self._make_request("POST", endpoint, data=data)

    def post_to_instagram(self, account_id: str, image_url: str, caption: str) -> Dict:
        """Post to Instagram (requires business account)."""
        # Step 1: Create media container
        container_endpoint = f"{account_id}/media"
        container_data = {
            "image_url": image_url,
            "caption": caption
        }
        container = self._make_request("POST", container_endpoint, data=container_data)
        container_id = container.get("id")

        # Step 2: Publish media container
        publish_endpoint = f"{account_id}/media_publish"
        publish_data = {"creation_id": container_id}
        return self._make_request("POST", publish_endpoint, data=publish_data)

    def get_page_insights(self, page_id: str, metrics: List[str], since: datetime, until: datetime) -> Dict:
        """Get Facebook page insights."""
        endpoint = f"{page_id}/insights"
        data = {
            "metric": ",".join(metrics),
            "since": int(since.timestamp()),
            "until": int(until.timestamp())
        }
        return self._make_request("GET", endpoint, data=data)

    def get_instagram_insights(self, media_id: str, metrics: List[str]) -> Dict:
        """Get Instagram media insights."""
        endpoint = f"{media_id}/insights"
        data = {"metric": ",".join(metrics)}
        return self._make_request("GET", endpoint, data=data)


def check_rate_limits(platform: str) -> bool:
    """Check if we're within rate limits for posting."""
    # Simple file-based rate limiting
    today = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().strftime("%Y-%m-%d %H")

    audit_file = LOGS_PATH / f"meta_social_audit_{today}.jsonl"
    if not audit_file.exists():
        return True

    daily_count = 0
    hourly_count = 0

    try:
        with open(audit_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("action", "").startswith(f"{platform}.post"):
                        ts = entry.get("timestamp", "")
                        if ts.startswith(today):
                            daily_count += 1
                        if ts.startswith(current_hour):
                            hourly_count += 1
                except json.JSONDecodeError:
                    continue

        if daily_count >= MAX_POSTS_PER_DAY:
            logger.warning(f"{platform} daily rate limit exceeded ({daily_count}/{MAX_POSTS_PER_DAY})")
            return False
        if hourly_count >= MAX_POSTS_PER_HOUR:
            logger.warning(f"{platform} hourly rate limit exceeded ({hourly_count}/{MAX_POSTS_PER_HOUR})")
            return False

        return True
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return False


@mcp.tool()
def post_to_facebook(content: str, link: str = None, requires_approval: bool = True) -> str:
    """
    Post content to Facebook page.

    Args:
        content: Text content to post
        link: Optional URL to include
        requires_approval: If True, queues for approval (default: True)

    Returns:
        Success message or approval file path
    """
    if requires_approval:
        # Create approval file
        filename = f"facebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = PENDING_PATH / filename

        approval_content = f"""---
type: facebook_post
platform: facebook
status: pending
created: {datetime.now().isoformat()}
---

# Facebook Post Approval

## Content
{content}

{f'**Link:** {link}' if link else ''}

---
**Actions:**
- To approve: Move to `Vault/Approved/`
- To edit: Modify content above
- To reject: Delete this file
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(approval_content)

        log_audit(
            action="facebook.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=FACEBOOK_PAGE_ID or "facebook_page",
            status=AuditStatus.PENDING,
            details={"content": content[:100], "link": link, "approval_file": str(filepath)},
            approval_required=True
        )

        return f"Facebook post queued for approval at {filepath}"

    # Direct posting (requires approval=False)
    if not META_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        error = "Meta credentials not configured"
        log_audit(
            action="facebook.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=FACEBOOK_PAGE_ID or "unknown",
            status=AuditStatus.FAILURE,
            error=error
        )
        return f"Error: {error}"

    # Check rate limits
    if not check_rate_limits("facebook"):
        error = "Rate limit exceeded"
        log_audit(
            action="facebook.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=FACEBOOK_PAGE_ID,
            status=AuditStatus.FAILURE,
            error=error
        )
        return f"Error: {error}"

    try:
        client = MetaAPIClient(META_ACCESS_TOKEN, GRAPH_API_VERSION)
        result = client.post_to_page(FACEBOOK_PAGE_ID, content, link=link)
        post_id = result.get("id")

        log_audit(
            action="facebook.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=FACEBOOK_PAGE_ID,
            status=AuditStatus.SUCCESS,
            details={"post_id": post_id, "content": content[:100]}
        )

        return f"Posted to Facebook successfully. Post ID: {post_id}"

    except Exception as e:
        log_audit(
            action="facebook.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=FACEBOOK_PAGE_ID,
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        return f"Error posting to Facebook: {str(e)}"


@mcp.tool()
def post_to_instagram(content: str, image_url: str, hashtags: List[str] = None, requires_approval: bool = True) -> str:
    """
    Post content to Instagram.

    Args:
        content: Caption text
        image_url: URL of image to post
        hashtags: Optional list of hashtags (without #)
        requires_approval: If True, queues for approval (default: True)

    Returns:
        Success message or approval file path
    """
    # Add hashtags to content
    full_caption = content
    if hashtags:
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        full_caption = f"{content}\n\n{hashtag_str}"

    if requires_approval:
        # Create approval file
        filename = f"instagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = PENDING_PATH / filename

        approval_content = f"""---
type: instagram_post
platform: instagram
status: pending
created: {datetime.now().isoformat()}
image_url: {image_url}
---

# Instagram Post Approval

## Caption
{full_caption}

## Image
{image_url}

---
**Actions:**
- To approve: Move to `Vault/Approved/`
- To edit: Modify caption above
- To reject: Delete this file
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(approval_content)

        log_audit(
            action="instagram.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=INSTAGRAM_ACCOUNT_ID or "instagram_account",
            status=AuditStatus.PENDING,
            details={"caption": content[:100], "image_url": image_url, "approval_file": str(filepath)},
            approval_required=True
        )

        return f"Instagram post queued for approval at {filepath}"

    # Direct posting
    if not META_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        error = "Instagram credentials not configured"
        log_audit(
            action="instagram.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=INSTAGRAM_ACCOUNT_ID or "unknown",
            status=AuditStatus.FAILURE,
            error=error
        )
        return f"Error: {error}"

    # Check rate limits
    if not check_rate_limits("instagram"):
        error = "Rate limit exceeded"
        log_audit(
            action="instagram.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=INSTAGRAM_ACCOUNT_ID,
            status=AuditStatus.FAILURE,
            error=error
        )
        return f"Error: {error}"

    try:
        client = MetaAPIClient(META_ACCESS_TOKEN, GRAPH_API_VERSION)
        result = client.post_to_instagram(INSTAGRAM_ACCOUNT_ID, image_url, full_caption)
        post_id = result.get("id")

        log_audit(
            action="instagram.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=INSTAGRAM_ACCOUNT_ID,
            status=AuditStatus.SUCCESS,
            details={"post_id": post_id, "caption": content[:100]}
        )

        return f"Posted to Instagram successfully. Post ID: {post_id}"

    except Exception as e:
        log_audit(
            action="instagram.post",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=INSTAGRAM_ACCOUNT_ID,
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        return f"Error posting to Instagram: {str(e)}"


@mcp.tool()
def get_facebook_insights(days: int = 7) -> str:
    """
    Get Facebook page insights for the last N days.

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        JSON string with insights data
    """
    if not META_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        return json.dumps({"error": "Facebook credentials not configured"})

    try:
        client = MetaAPIClient(META_ACCESS_TOKEN, GRAPH_API_VERSION)
        until_date = datetime.now()
        since_date = until_date - timedelta(days=days)

        metrics = [
            "page_impressions",
            "page_engaged_users",
            "page_post_engagements",
            "page_fans"
        ]

        insights = client.get_page_insights(FACEBOOK_PAGE_ID, metrics, since_date, until_date)

        log_audit(
            action="facebook.get_insights",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=FACEBOOK_PAGE_ID,
            status=AuditStatus.SUCCESS,
            details={"days": days}
        )

        return json.dumps(insights, indent=2)

    except Exception as e:
        log_audit(
            action="facebook.get_insights",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=FACEBOOK_PAGE_ID,
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_instagram_insights(days: int = 7) -> str:
    """
    Get Instagram account insights for the last N days.

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        JSON string with insights data
    """
    if not META_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        return json.dumps({"error": "Instagram credentials not configured"})

    try:
        # Note: Instagram Insights API requires different approach
        # This is a simplified version - full implementation would need media IDs
        log_audit(
            action="instagram.get_insights",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=INSTAGRAM_ACCOUNT_ID,
            status=AuditStatus.SUCCESS,
            details={"days": days}
        )

        return json.dumps({
            "message": "Instagram insights available via Instagram Graph API",
            "note": "Full implementation requires media IDs and account insights endpoint"
        })

    except Exception as e:
        log_audit(
            action="instagram.get_insights",
            actor="meta_social_mcp",
            domain=AuditDomain.BUSINESS,
            resource=INSTAGRAM_ACCOUNT_ID,
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_summary(platform: str, period: str = "weekly") -> str:
    """
    Generate engagement summary for a platform.

    Args:
        platform: 'facebook' or 'instagram'
        period: 'daily', 'weekly', or 'monthly'

    Returns:
        Markdown formatted summary
    """
    period_days = {"daily": 1, "weekly": 7, "monthly": 30}.get(period, 7)

    if platform == "facebook":
        insights_json = get_facebook_insights(period_days)
    elif platform == "instagram":
        insights_json = get_instagram_insights(period_days)
    else:
        return f"Error: Unknown platform '{platform}'"

    try:
        insights = json.loads(insights_json)

        if "error" in insights:
            return f"Error generating summary: {insights['error']}"

        # Generate markdown summary
        summary = f"""# {platform.title()} {period.title()} Summary

**Period:** Last {period_days} days
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Metrics
{json.dumps(insights, indent=2)}

---
*Generated by Meta Social MCP Server*
"""
        return summary

    except Exception as e:
        return f"Error generating summary: {str(e)}"


@mcp.tool()
def get_page_info() -> str:
    """
    Get basic information about the configured Facebook Page.

    Returns:
        JSON string with page details
    """
    if not META_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
        return json.dumps({"error": "Facebook credentials not configured"})

    try:
        client = MetaAPIClient(META_ACCESS_TOKEN, GRAPH_API_VERSION)
        endpoint = f"{FACEBOOK_PAGE_ID}"
        params = {"fields": "name,about,fan_count,followers_count,verification_status"}
        
        info = client._make_request("GET", endpoint, data=params)
        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
