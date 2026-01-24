# Social Media API Setup Guide

This guide covers setting up API access for Facebook, Instagram, and Twitter/X.

---

## Meta (Facebook & Instagram)

### Prerequisites
- Facebook account
- Facebook Page (for posting)
- Instagram Business Account (connected to Facebook Page)

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Select "Business" as app type
4. Fill in app details:
   - **App Name:** Digital FTE Social
   - **App Contact Email:** your_email@example.com
5. Click "Create App"

### Step 2: Add Products

1. In your app dashboard, click "Add Product"
2. Add **"Facebook Login"**
3. Add **"Instagram Basic Display"** or **"Instagram Graph API"**
4. Configure products as needed

### Step 3: Generate Access Token

1. Go to Tools → Graph API Explorer
2. Select your app
3. Add permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
4. Click "Generate Access Token"
5. Copy the token (save it securely)

### Step 4: Get Page ID and Instagram Account ID

**Facebook Page ID:**
1. Go to your Facebook Page
2. Click "About"
3. Scroll to "Page ID" (or use Graph API Explorer with `/me/accounts`)

**Instagram Account ID:**
1. In Graph API Explorer
2. Query: `/{page-id}?fields=instagram_business_account`
3. Copy the `instagram_business_account` ID

### Step 5: Make Token Long-Lived

Short-lived tokens expire in 1 hour. Convert to long-lived (60 days):

```bash
https://graph.facebook.com/oauth/access_token?
  grant_type=fb_exchange_token&
  client_id={app-id}&
  client_secret={app-secret}&
  fb_exchange_token={short-lived-token}
```

### Step 6: Configure Environment

Add to `.env`:
```env
META_ACCESS_TOKEN=your_long_lived_access_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id
GRAPH_API_VERSION=v18.0
```

---

## Twitter/X

### Prerequisites
- Twitter/X account
- Developer account (free tier available)

### Step 1: Apply for Developer Access

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Click "Sign up" for developer access
3. Complete the application:
   - **Primary use case:** Publish and curate Tweets
   - **Will you make Twitter content available to government?** No
4. Agree to terms and submit

### Step 2: Create App

1. Once approved, go to Developer Portal
2. Click "Projects & Apps" → "Create App"
3. Fill in app details:
   - **App Name:** Digital FTE Twitter
   - **Use case:** Making a bot
4. Click "Next"

### Step 3: Generate Keys and Tokens

1. In your app dashboard, go to "Keys and tokens" tab
2. Generate/copy these credentials:
   - **Consumer Key** (this is your API Key - save this)
   - **Consumer Secret** (this is your API Secret - save this)
   - **Bearer Token** (save this)
   - **Access Token** (save this)
   - **Access Token Secret** (save this)

**Note:** Twitter uses "Consumer Key/Secret" terminology, but our code refers to them as "API Key/Secret" for consistency.

### Step 4: Set App Permissions

1. Go to "Settings" tab
2. Under "App permissions":
   - Select "Read and Write"
   - Click "Save"
3. Regenerate tokens if permissions were changed

### Step 5: Enable OAuth 2.0 (Optional)

For advanced features:
1. Go to "Settings" tab
2. Scroll to "User authentication settings"
3. Click "Set up"
4. Configure OAuth 2.0 settings

### Step 6: Configure Environment

Add to `.env` (map Twitter's credentials to our variables):
```env
TWITTER_API_KEY=your_consumer_key_here
TWITTER_API_SECRET=your_consumer_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

**Credential Mapping:**
- Twitter's "Consumer Key" → `TWITTER_API_KEY`
- Twitter's "Consumer Secret" → `TWITTER_API_SECRET`
- Twitter's "Access Token" → `TWITTER_ACCESS_TOKEN`
- Twitter's "Access Token Secret" → `TWITTER_ACCESS_SECRET`
- Twitter's "Bearer Token" → `TWITTER_BEARER_TOKEN`

---

## Testing API Access

### Test Facebook

```bash
cd .claude/skills/posting-facebook
python scripts/verify.py
```

Expected: `✓ posting-facebook valid`

### Test Instagram

```bash
cd .claude/skills/posting-instagram
python scripts/verify.py
```

Expected: `✓ posting-instagram valid`

### Test Twitter

```bash
cd .claude/skills/posting-twitter
python scripts/verify.py
```

Expected: `✓ posting-twitter valid`

---

## Troubleshooting

### Facebook/Instagram

**Error: Invalid OAuth access token**
- Check token hasn't expired (60-day limit for long-lived tokens)
- Regenerate token in Graph API Explorer

**Error: (#200) The user hasn't authorized the application to perform this action**
- Check app permissions include required scopes
- Reauthorize app with updated permissions

**Instagram: Error creating media container**
- Ensure Instagram account is Business account
- Verify account is connected to Facebook Page
- Check image URL is publicly accessible

### Twitter

**Error: Unauthorized**
- Verify Bearer Token is correct
- Check API keys match your app
- Ensure app permissions are "Read and Write"

**Error: Rate limit exceeded**
- Wait for rate limit window to reset (15 minutes)
- Implement exponential backoff

**Error: 403 Forbidden**
- Check app is not suspended
- Verify developer account is in good standing

---

## Rate Limits Summary

### Facebook
- **Posts:** 25 per day, 5 per hour
- **API calls:** Varies by endpoint
- **Read:** Higher limits than write

### Instagram
- **Posts:** 25 per day, 5 per hour
- **Stories:** Different limits apply
- **API calls:** Similar to Facebook

### Twitter/X
- **Tweets:** 50 per day, 10 per hour (enforced by our system)
- **API calls:**
  - Free tier: 1,500 tweets/month
  - Basic tier: Higher limits available
- **Read operations:** Higher limits than write

---

## Security Best Practices

1. **Never commit tokens to git**
   - Keep `.env` in `.gitignore`
   - Use `.env.example` for templates

2. **Rotate tokens regularly**
   - Facebook: Regenerate every 60 days
   - Twitter: Rotate if compromised

3. **Use minimal permissions**
   - Only request scopes you need
   - Remove unused permissions

4. **Monitor usage**
   - Check audit logs regularly
   - Watch for unauthorized access

5. **Secure storage**
   - Store tokens in `.env` (local only)
   - Never log tokens
   - Never send tokens in error messages

---

## Resources

### Meta/Facebook
- [Graph API Documentation](https://developers.facebook.com/docs/graph-api)
- [Access Token Guide](https://developers.facebook.com/docs/facebook-login/guides/access-tokens)
- [Instagram API](https://developers.facebook.com/docs/instagram-api)

### Twitter
- [Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- [API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Authentication Guide](https://developer.twitter.com/en/docs/authentication/oauth-2-0)

---

**Last Updated:** 2026-01-18
**Maintainer:** Digital FTE Team
