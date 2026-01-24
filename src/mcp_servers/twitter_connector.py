"""
Twitter/X MCP Server - Twitter Integration

Provides MCP tools for Twitter/X:
- Post tweets
- Upload media
- Create threads
- Get engagement insights
- Search mentions
- Generate summaries

Uses Twitter API v2 for all operations.
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
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

VAULT_PATH = PROJECT_ROOT / "Vault"
PENDING_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
LOGS_PATH = VAULT_PATH / "Logs"

# Rate limits
MAX_TWEETS_PER_DAY = 50
MAX_TWEETS_PER_HOUR = 10

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TwitterMCP")

# Ensure directories
PENDING_PATH.mkdir(parents=True, exist_ok=True)
APPROVED_PATH.mkdir(parents=True, exist_ok=True)
LOGS_PATH.mkdir(parents=True, exist_ok=True)

# Initialize MCP
mcp = FastMCP("Twitter/X")


class TwitterAPIClient:
    """Manages Twitter API v2 connections."""

    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        })

    def _make_request(self, method: str, endpoint: str, data: Dict = None, json_data: Dict = None) -> Dict:
        """Make request to Twitter API."""
        url = f"{self.base_url}/{endpoint}"

        try:
            if method == "GET":
                response = self.session.get(url, params=data)
            elif method == "POST":
                if json_data:
                    response = self.session.post(url, json=json_data)
                else:
                    response = self.session.post(url, data=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise

    def create_tweet(self, text: str, reply_to: str = None, media_ids: List[str] = None) -> Dict:
        """Create a tweet."""
        endpoint = "tweets"
        payload = {"text": text}

        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}

        if media_ids:
            payload["media"] = {"media_ids": media_ids}

        return self._make_request("POST", endpoint, json_data=payload)

    def upload_media(self, file_path: str) -> str:
        """Upload media to Twitter (requires different endpoint)."""
        # Note: Media upload uses v1.1 API
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"

        # This is a simplified version - full implementation would need OAuth 1.0a
        logger.warning("Media upload requires OAuth 1.0a - implement with tweepy library")
        return None

    def get_user_tweets(self, user_id: str, max_results: int = 10) -> Dict:
        """Get recent tweets from user."""
        endpoint = f"users/{user_id}/tweets"
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics"
        }
        return self._make_request("GET", endpoint, data=params)

    def search_mentions(self, query: str, max_results: int = 10) -> Dict:
        """Search for mentions."""
        endpoint = "tweets/search/recent"
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics,author_id"
        }
        return self._make_request("GET", endpoint, data=params)


def check_rate_limits() -> bool:
    """Check if we're within rate limits for posting."""
    today = datetime.now().strftime("%Y-%m-%d")
    current_hour = datetime.now().strftime("%Y-%m-%d %H")

    audit_file = LOGS_PATH / f"twitter_audit_{today}.jsonl"
    if not audit_file.exists():
        return True

    daily_count = 0
    hourly_count = 0

    try:
        with open(audit_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry.get("action") == "twitter.post":
                        ts = entry.get("timestamp", "")
                        if ts.startswith(today):
                            daily_count += 1
                        if ts.startswith(current_hour):
                            hourly_count += 1
                except json.JSONDecodeError:
                    continue

        if daily_count >= MAX_TWEETS_PER_DAY:
            logger.warning(f"Twitter daily rate limit exceeded ({daily_count}/{MAX_TWEETS_PER_DAY})")
            return False
        if hourly_count >= MAX_TWEETS_PER_HOUR:
            logger.warning(f"Twitter hourly rate limit exceeded ({hourly_count}/{MAX_TWEETS_PER_HOUR})")
            return False

        return True
    except Exception as e:
        logger.error(f"Rate limit check failed: {e}")
        return False


@mcp.tool()
def post_tweet(content: str, reply_to: str = None, requires_approval: bool = True) -> str:
    """
    Post a tweet.

    Args:
        content: Tweet text (max 280 characters)
        reply_to: Optional tweet ID to reply to
        requires_approval: If True, queues for approval (default: True)

    Returns:
        Success message or approval file path
    """
    # Validate length
    if len(content) > 280:
        return f"Error: Tweet too long ({len(content)} characters, max 280)"

    if requires_approval:
        # Create approval file
        filename = f"twitter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = PENDING_PATH / filename

        approval_content = f"""---
type: twitter_post
platform: twitter
status: pending
created: {datetime.now().isoformat()}
{f'reply_to: {reply_to}' if reply_to else ''}
---

# Twitter Post Approval

## Tweet
{content}

**Character count:** {len(content)}/280

{f'**Reply to:** {reply_to}' if reply_to else ''}

---
**Actions:**
- To approve: Move to `Vault/Approved/`
- To edit: Modify tweet text above
- To reject: Delete this file
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(approval_content)

        log_audit(
            action="twitter.post",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.PENDING,
            details={"content": content, "reply_to": reply_to, "approval_file": str(filepath)},
            approval_required=True
        )

        return f"Tweet queued for approval at {filepath}"

    # Direct posting
    if not TWITTER_BEARER_TOKEN:
        error = "Twitter credentials not configured"
        log_audit(
            action="twitter.post",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.FAILURE,
            error=error
        )
        return f"Error: {error}"

    # Check rate limits
    if not check_rate_limits():
        error = "Rate limit exceeded"
        log_audit(
            action="twitter.post",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.FAILURE,
            error=error
        )
        return f"Error: {error}"

    try:
        client = TwitterAPIClient(TWITTER_BEARER_TOKEN)
        result = client.create_tweet(content, reply_to=reply_to)

        tweet_data = result.get("data", {})
        tweet_id = tweet_data.get("id")

        log_audit(
            action="twitter.post",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.SUCCESS,
            details={"tweet_id": tweet_id, "content": content}
        )

        return f"Tweet posted successfully. ID: {tweet_id}"

    except Exception as e:
        log_audit(
            action="twitter.post",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        return f"Error posting tweet: {str(e)}"


@mcp.tool()
def create_thread(tweets: List[str], requires_approval: bool = True) -> str:
    """
    Create a Twitter thread (multiple connected tweets).

    Args:
        tweets: List of tweet texts (each max 280 characters)
        requires_approval: If True, queues for approval (default: True)

    Returns:
        Success message or approval file path
    """
    # Validate all tweets
    for i, tweet in enumerate(tweets):
        if len(tweet) > 280:
            return f"Error: Tweet {i+1} too long ({len(tweet)} characters, max 280)"

    if requires_approval:
        # Create approval file
        filename = f"twitter_thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = PENDING_PATH / filename

        thread_content = "\n\n".join([f"**Tweet {i+1}:**\n{tweet}" for i, tweet in enumerate(tweets)])

        approval_content = f"""---
type: twitter_thread
platform: twitter
status: pending
created: {datetime.now().isoformat()}
tweet_count: {len(tweets)}
---

# Twitter Thread Approval

## Thread ({len(tweets)} tweets)

{thread_content}

---
**Actions:**
- To approve: Move to `Vault/Approved/`
- To edit: Modify tweets above
- To reject: Delete this file
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(approval_content)

        log_audit(
            action="twitter.create_thread",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.PENDING,
            details={"tweet_count": len(tweets), "approval_file": str(filepath)},
            approval_required=True
        )

        return f"Twitter thread queued for approval at {filepath}"

    # Direct posting
    if not TWITTER_BEARER_TOKEN:
        return "Error: Twitter credentials not configured"

    try:
        client = TwitterAPIClient(TWITTER_BEARER_TOKEN)
        tweet_ids = []
        reply_to = None

        for i, tweet_text in enumerate(tweets):
            result = client.create_tweet(tweet_text, reply_to=reply_to)
            tweet_data = result.get("data", {})
            tweet_id = tweet_data.get("id")
            tweet_ids.append(tweet_id)
            reply_to = tweet_id  # Next tweet replies to this one

        log_audit(
            action="twitter.create_thread",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.SUCCESS,
            details={"tweet_count": len(tweets), "tweet_ids": tweet_ids}
        )

        return f"Thread posted successfully. {len(tweet_ids)} tweets. IDs: {', '.join(tweet_ids)}"

    except Exception as e:
        log_audit(
            action="twitter.create_thread",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        return f"Error posting thread: {str(e)}"


@mcp.tool()
def get_timeline_insights(days: int = 7) -> str:
    """
    Get Twitter timeline insights for the last N days.

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        JSON string with insights data
    """
    if not TWITTER_BEARER_TOKEN:
        return json.dumps({"error": "Twitter credentials not configured"})

    try:
        # Note: This would require user ID and proper implementation
        log_audit(
            action="twitter.get_insights",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.SUCCESS,
            details={"days": days}
        )

        return json.dumps({
            "message": "Twitter insights available via Twitter API v2",
            "note": "Full implementation requires user ID and metrics endpoint"
        })

    except Exception as e:
        log_audit(
            action="twitter.get_insights",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_mentions(query: str, max_results: int = 10) -> str:
    """
    Search for mentions or specific queries.

    Args:
        query: Search query (e.g., "@username" or "keyword")
        max_results: Maximum number of results (default: 10, max: 100)

    Returns:
        JSON string with search results
    """
    if not TWITTER_BEARER_TOKEN:
        return json.dumps({"error": "Twitter credentials not configured"})

    try:
        client = TwitterAPIClient(TWITTER_BEARER_TOKEN)
        results = client.search_mentions(query, max_results=min(max_results, 100))

        log_audit(
            action="twitter.search_mentions",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.SUCCESS,
            details={"query": query, "max_results": max_results}
        )

        return json.dumps(results, indent=2)

    except Exception as e:
        log_audit(
            action="twitter.search_mentions",
            actor="twitter_mcp",
            domain=AuditDomain.BUSINESS,
            resource="twitter_account",
            status=AuditStatus.FAILURE,
            error=str(e)
        )
        return json.dumps({"error": str(e)})


@mcp.tool()
def generate_summary(period: str = "weekly") -> str:
    """
    Generate Twitter engagement summary.

    Args:
        period: 'daily', 'weekly', or 'monthly'

    Returns:
        Markdown formatted summary
    """
    period_days = {"daily": 1, "weekly": 7, "monthly": 30}.get(period, 7)
    insights_json = get_timeline_insights(period_days)

    try:
        insights = json.loads(insights_json)

        if "error" in insights:
            return f"Error generating summary: {insights['error']}"

        # Generate markdown summary
        summary = f"""# Twitter {period.title()} Summary

**Period:** Last {period_days} days
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}

## Metrics
{json.dumps(insights, indent=2)}

---
*Generated by Twitter MCP Server*
"""
        return summary

    except Exception as e:
        return f"Error generating summary: {str(e)}"


@mcp.tool()
def get_user_info(username: str) -> str:
    """
    Get information about a Twitter user.

    Args:
        username: Twitter handle (without @)

    Returns:
        JSON string with user details
    """
    if not TWITTER_BEARER_TOKEN:
        return json.dumps({"error": "Twitter credentials not configured"})

    try:
        client = TwitterAPIClient(TWITTER_BEARER_TOKEN)
        endpoint = f"users/by/username/{username}"
        params = {"user.fields": "description,public_metrics,verified,created_at"}
        
        info = client._make_request("GET", endpoint, data=params)
        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    mcp.run()
