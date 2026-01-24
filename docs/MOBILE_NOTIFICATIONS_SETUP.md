# Mobile Notifications Setup Guide

This guide explains how to set up Abdullah Junior on your phone to receive proactive notifications from the Agentic Intelligence Layer.

## Quick Start

1. **Start the system:**
   ```powershell
   ./Start_Agentic_System.ps1
   ```

2. **Open the PWA on your phone:**
   - Navigate to `http://YOUR_PC_IP:3000` on your phone browser
   - Use Chrome on Android or Safari on iOS

3. **Install the PWA:**
   - **Android:** Tap "Add to Home Screen" in browser menu
   - **iOS:** Tap Share → "Add to Home Screen"

4. **Enable Notifications:**
   - When prompted, tap "Enable" to allow notifications
   - The system will register your device for push notifications

## What Notifications Will You Receive?

### 🧠 Proactive Suggestions
When the Agentic Intelligence detects opportunities:
- "Time for a LinkedIn post? Last post was 4 days ago"
- "Morning routine: Review calendar, check emails"
- "Meeting in 15 minutes - prepare notes?"

### ✅ Approval Requests
When tasks need your approval:
- High-risk tasks (financial, external communication)
- Complex multi-step tasks
- Actions requiring human judgment

### 📊 Daily Digest
Every morning at 9am:
- Summary of pending tasks
- Urgent items count
- Today's calendar overview

### 🎉 Task Completions
When approved tasks are finished:
- Confirmation of successful execution
- Brief result summary

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     YOUR PHONE                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         Abdullah Junior PWA                         │ │
│  │  • Receives push notifications                      │ │
│  │  • Quick approve/reject actions                     │ │
│  │  • Dashboard access                                 │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
                            │
                            │ Web Push (VAPID)
                            ▼
┌──────────────────────────────────────────────────────────┐
│                     YOUR PC                               │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         API Server (port 8000)                      │ │
│  │  • Push notification service                        │ │
│  │  • Task management API                              │ │
│  │  • Subscription management                          │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         Orchestrator + Agentic Intelligence         │ │
│  │  • Context Monitor (proactive suggestions)          │ │
│  │  • Complexity & Risk scoring                        │ │
│  │  • Approval decision making                         │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## VAPID Keys Setup

VAPID keys are required for web push authentication. The setup script generates these automatically:

```bash
python scripts/setup_push_notifications.py
```

This creates:
- `config/push_notifications/vapid_keys.json` - Server-side keys
- Adds `VAPID_PUBLIC_KEY` to `.env.local`
- Adds `NEXT_PUBLIC_VAPID_PUBLIC_KEY` to `frontend/.env.local`

## Testing Notifications

Send a test notification:

```bash
curl -X POST http://localhost:8000/api/notifications/test \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "body": "Hello from Abdullah Junior!"}'
```

Check subscription status:

```bash
curl http://localhost:8000/api/notifications/status
```

## Troubleshooting

### Notifications not appearing

1. **Check browser permissions:**
   - Go to browser settings → Notifications
   - Ensure the site is allowed

2. **Check subscription:**
   ```bash
   curl http://localhost:8000/api/notifications/status
   ```
   Should show `active: 1` or more

3. **Check VAPID keys:**
   - Verify `config/push_notifications/vapid_keys.json` exists
   - Verify `NEXT_PUBLIC_VAPID_PUBLIC_KEY` in `frontend/.env.local`

### "Push notifications not supported"

- **iOS Safari:** Push requires iOS 16.4+ and PWA must be installed
- **Android Chrome:** Should work in browser and PWA
- **Desktop browsers:** All modern browsers support push

### Phone can't connect to PC

1. **Check network:** Both devices must be on same network
2. **Check firewall:** Allow ports 3000 and 8000
3. **Find PC IP:**
   ```powershell
   ipconfig | findstr IPv4
   ```
4. **Use PC IP:** e.g., `http://192.168.1.100:3000`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/notifications/subscribe` | POST | Register device for push |
| `/api/notifications/unsubscribe` | POST | Remove device registration |
| `/api/notifications/test` | POST | Send test notification |
| `/api/notifications/status` | GET | Check subscription status |
| `/api/notifications/vapid-public-key` | GET | Get VAPID public key |
| `/api/tasks/{id}/approve` | POST | Approve a task |
| `/api/tasks/{id}/reject` | POST | Reject a task |

## Security Notes

- VAPID private key is stored server-side only
- Push subscriptions are device-specific
- All notifications require HTTPS in production
- Local development uses localhost exception

## Files Created

```
src/
├── notifications/
│   ├── __init__.py          # Module exports
│   ├── push_service.py      # Push notification service
│   └── api.py               # FastAPI endpoints
├── api_server.py            # Main API server
├── intelligence/
│   ├── context_monitor.py   # Proactive suggestion engine (enhanced)
│   └── agentic_intelligence.py  # Decision making layer
└── orchestrator.py          # Main orchestrator (enhanced)

config/
└── push_notifications/
    ├── vapid_keys.json      # VAPID key pair
    └── subscriptions.json   # Registered devices

frontend/
└── src/components/pwa/
    └── NotificationPrompt.tsx  # Subscription UI (enhanced)

scripts/
└── setup_push_notifications.py  # VAPID key generator
```

## Next Steps

1. **Customize notification thresholds** in `src/intelligence/context_monitor.py`
2. **Add more context monitors** (email, calendar integration)
3. **Configure daily digest time** (default: 9am)
4. **Set up production HTTPS** for real device deployment
