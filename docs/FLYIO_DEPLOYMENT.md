# Fly.io Deployment Guide - Abdullah Junior Backend

Deploy the Digital FTE backend to Fly.io for mobile app connectivity.

## Prerequisites

1. Install Fly CLI: https://fly.io/docs/hands-on/install-flyctl/
2. Create Fly.io account: https://fly.io/signup
3. Firebase service account configured

## Quick Deploy (5 minutes)

### Step 1: Login to Fly.io

```bash
fly auth login
```

### Step 2: Launch Application

```bash
# First-time deployment
fly launch --name abdullah-junior-api --region iad --no-deploy

# Or use existing config
fly deploy
```

### Step 3: Set Secrets

```bash
# Required: Firebase (for push notifications)
fly secrets set FIREBASE_SERVICE_ACCOUNT="$(cat config/firebase-service-account.json)"

# Optional: Telegram bot (fallback notifications)
fly secrets set TELEGRAM_BOT_TOKEN="your_bot_token"
fly secrets set TELEGRAM_CHAT_ID="your_chat_id"

# Optional: Social media APIs
fly secrets set META_ACCESS_TOKEN="your_meta_token"
fly secrets set TWITTER_API_KEY="your_key"
fly secrets set TWITTER_API_SECRET="your_secret"
```

### Step 4: Deploy

```bash
fly deploy
```

### Step 5: Verify

```bash
# Check status
fly status

# View logs
fly logs

# Test health endpoint
curl https://abdullah-junior-api.fly.dev/api/health
```

---

## Configuration

### App Name

The default app name is `abdullah-junior-api`. To change it:

1. Edit `fly.toml`: `app = "your-app-name"`
2. Re-run `fly launch`

### Region

Default region is `iad` (US East Virginia). For lower latency:

- Europe: `lhr` (London) or `ams` (Amsterdam)
- Asia: `sin` (Singapore) or `nrt` (Tokyo)
- US West: `sea` (Seattle) or `lax` (Los Angeles)

```bash
# Deploy to specific region
fly deploy --region lhr
```

### Scaling

Free tier includes:
- 3 shared VMs
- 160GB outbound bandwidth/month
- Automatic sleep when idle

To scale:

```bash
# Scale up (more memory)
fly scale memory 1024

# Scale out (more instances)
fly scale count 2

# View current scale
fly scale show
```

---

## Connect Mobile App

After deployment, update the mobile app's backend URL:

1. Open Settings in the mobile app
2. Enter: `https://abdullah-junior-api.fly.dev`
3. Test connection

Or set in `mobile/services/api.ts`:

```typescript
const DEFAULT_BASE_URL = 'https://abdullah-junior-api.fly.dev';
```

---

## Monitoring

### View Logs

```bash
# Live logs
fly logs

# Filter by level
fly logs --level error
```

### Dashboard

Visit: https://fly.io/apps/abdullah-junior-api

### Health Check

```bash
# Automatic health checks every 30s
curl https://abdullah-junior-api.fly.dev/api/health
```

---

## Troubleshooting

### App won't start

```bash
# Check deployment logs
fly logs --instance <instance-id>

# SSH into container
fly ssh console
```

### Secrets not working

```bash
# List secrets
fly secrets list

# Unset and reset
fly secrets unset FIREBASE_SERVICE_ACCOUNT
fly secrets set FIREBASE_SERVICE_ACCOUNT="$(cat config/firebase-service-account.json)"
```

### SSL/HTTPS issues

Fly.io provides automatic HTTPS. If issues:

```bash
# Check certificates
fly certs show

# Add custom domain
fly certs add yourdomain.com
```

---

## Cost Estimation

Fly.io Free Tier (Hobby Plan):
- 3 shared-cpu-1x VMs (256MB each)
- 160GB outbound bandwidth
- Automatic sleep when idle

For Abdullah Junior (light usage):
- **$0/month** on free tier
- Wakes from sleep in ~3 seconds on first request

---

## Useful Commands

```bash
# Status
fly status

# Open in browser
fly open

# SSH access
fly ssh console

# Restart
fly apps restart

# Scale down (stop billing)
fly scale count 0

# Destroy (delete everything)
fly apps destroy abdullah-junior-api
```

---

## Custom Domain (Optional)

```bash
# Add custom domain
fly certs add api.abdullahjunior.com

# Follow DNS instructions shown
# Add CNAME record: api.abdullahjunior.com -> abdullah-junior-api.fly.dev
```
