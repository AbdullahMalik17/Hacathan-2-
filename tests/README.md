# Testing Guide

## Quick Start

### Test All APIs
```bash
python tests/test_social_media_apis.py
```

This will test:
- ✓ Facebook API authentication and permissions
- ✓ Instagram API and business account
- ✓ Twitter API v2 bearer token
- ✓ Odoo connection (if configured)

### Verify All Skills
```bash
python tests/verify_all_skills.py
```

This runs verification for:
- posting-facebook
- posting-instagram
- posting-twitter

## Individual Skill Tests

### Facebook
```bash
cd .claude/skills/posting-facebook
python scripts/verify.py
```

### Instagram
```bash
cd .claude/skills/posting-instagram
python scripts/verify.py
```

### Twitter
```bash
cd .claude/skills/posting-twitter
python scripts/verify.py
```

## Manual API Tests

### Test Facebook Posting (Dry Run)
```python
from src.mcp_servers.meta_social_connector import post_to_facebook

# This will create approval file, not post directly
result = post_to_facebook(
    content="Test post from Digital FTE",
    requires_approval=True
)
print(result)
```

### Test Instagram Posting (Dry Run)
```python
from src.mcp_servers.meta_social_connector import post_to_instagram

result = post_to_instagram(
    content="Test caption",
    image_url="https://picsum.photos/1080/1080",
    hashtags=["test", "automation"],
    requires_approval=True
)
print(result)
```

### Test Twitter Posting (Dry Run)
```python
from src.mcp_servers.twitter_connector import post_tweet

result = post_tweet(
    content="Test tweet from Digital FTE 🤖",
    requires_approval=True
)
print(result)
```

## Troubleshooting

### Facebook/Instagram Errors

**"Invalid OAuth access token"**
- Token may have expired (60-day limit)
- Regenerate in Facebook Developer Portal → Graph API Explorer

**"Permissions error"**
- Check app has required permissions:
  - `pages_manage_posts`
  - `pages_read_engagement`
  - `instagram_basic`
  - `instagram_content_publish`

### Twitter Errors

**"Unauthorized"**
- Verify Bearer Token in .env
- Check app permissions are "Read and Write"
- Regenerate tokens if needed

**"Rate limit exceeded"**
- Wait 15 minutes for reset
- Check rate limit status in Twitter Developer Portal

### Odoo Errors

**"Cannot connect to server"**
- Ensure Odoo is running: `docker ps | grep odoo`
- Start Odoo: `docker start odoo`
- Check URL: `http://localhost:8069`

**"Authentication failed"**
- Verify database name matches
- Check username/password in .env
- Default: admin/admin (change after first login)

## Expected Output

### Successful Test Run
```
╔══════════════════════════════════════════════════════════╗
║               API CONNECTION TEST SUITE                  ║
╚══════════════════════════════════════════════════════════╝

============================================================
  Testing Facebook API
============================================================

ℹ Access Token: EAA7N4cPMUCUBQScdq...
ℹ Page ID: 4167019210231845
ℹ API Version: v18.0

1. Validating access token...
✓ Token valid for: Your Page Name

2. Getting page information...
✓ Page: Your Page Name
✓ Has posting permissions

3. Checking required permissions...
✓ pages_manage_posts: granted
✓ pages_read_engagement: granted

✓ Facebook API test completed successfully

[... similar for Instagram and Twitter ...]

============================================================
  Test Summary
============================================================

✓ Facebook: PASSED
✓ Instagram: PASSED
✓ Twitter: PASSED
⚠ Odoo: SKIPPED (not configured)

Results: 3 passed, 0 failed, 1 skipped

✓ All configured APIs are working correctly!
```

## Next Steps

After all tests pass:

1. **Test Posting (with approval)**
   ```bash
   # Facebook
   python .claude/skills/posting-facebook/scripts/run.py --post "Test post"

   # Instagram
   python .claude/skills/posting-instagram/scripts/run.py \
     --post "Test caption" \
     --image "https://picsum.photos/1080/1080" \
     --hashtags "test,automation"

   # Twitter
   python .claude/skills/posting-twitter/scripts/run.py --post "Test tweet"
   ```

2. **Check Approval Files**
   ```bash
   ls Vault/Pending_Approval/
   ```

3. **Approve and Post**
   - Review content in `Vault/Pending_Approval/`
   - Move to `Vault/Approved/` to publish
   - Or delete to reject

## Resources

- [Setup Guide](../docs/setup/social-media-apis.md)
- [Facebook API Docs](https://developers.facebook.com/docs/graph-api)
- [Twitter API Docs](https://developer.twitter.com/en/docs/twitter-api)
