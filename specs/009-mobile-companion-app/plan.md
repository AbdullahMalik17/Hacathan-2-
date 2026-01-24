# Implementation Plan: Abdullah Junior Mobile Companion App

## Overview

This document outlines the architecture and implementation strategy for the Abdullah Junior mobile companion app.

---

## Architecture Decision Records

### ADR-001: Framework Selection - Expo with Development Build

**Context:** Need to choose between bare React Native and Expo for the mobile framework.

**Decision:** Use Expo SDK 54 with Development Build (not Expo Go).

**Rationale:**
- Expo's `expo-notifications` can retrieve native FCM tokens via `getDevicePushTokenAsync()`
- EAS Build provides cloud-based iOS/Android builds without local tooling
- Development builds allow native module integration when needed
- 80% faster iteration compared to bare React Native
- Aligns with the web-first, rapid development philosophy of the project

**Consequences:**
- (+) Faster development and deployment
- (+) No need for Xcode/Android Studio for most features
- (-) Slightly larger app bundle size
- (-) Some native modules require development builds

**Alternatives Considered:**
1. Bare React Native - More control, but slower iteration
2. Flutter - Different language (Dart), would break team's TypeScript expertise

---

### ADR-002: State Management - Zustand + TanStack Query

**Context:** Need state management for UI state and server cache.

**Decision:** Use Zustand for client state, TanStack Query for server state.

**Rationale:**
- Zustand is 1.2KB (vs Redux Toolkit ~12KB), perfect for mobile
- Zustand's persist middleware integrates seamlessly with AsyncStorage
- TanStack Query handles caching, background refetch, and optimistic updates
- Clear separation: Zustand = UI state, Query = server data

**Consequences:**
- (+) Minimal bundle size impact
- (+) Simple API with hooks
- (+) Built-in offline support via persist
- (-) Team must learn two patterns (acceptable tradeoff)

---

### ADR-003: UI Styling - NativeWind v4

**Context:** Need to style React Native components consistently with web frontend.

**Decision:** Use NativeWind v4 (Tailwind CSS for React Native).

**Rationale:**
- Direct 1:1 alignment with existing `/mnt/d/Hacathan_2/frontend/tailwind.config.ts`
- Same utility classes work across web and mobile
- Supports dark mode via `dark:` prefix
- Compiles to native StyleSheet for performance

**Consequences:**
- (+) Design system consistency
- (+) Familiar API for team
- (+) Smaller bundle than component libraries
- (-) Requires Babel/Metro configuration

---

### ADR-004: Push Notifications - Firebase Cloud Messaging

**Context:** Need reliable push notifications for both iOS and Android.

**Decision:** Use Firebase Cloud Messaging (FCM) via expo-notifications.

**Rationale:**
- FCM is the industry standard with >99% delivery SLA
- Single API works for both iOS (via APNs) and Android
- Free tier is generous (unlimited notifications)
- Firebase Admin SDK integrates easily with Python backend

**Consequences:**
- (+) Reliable, battle-tested infrastructure
- (+) Native notification handling (background, killed state)
- (+) Analytics included
- (-) Requires Google account and Firebase project setup
- (-) Must add firebase-admin to backend dependencies

---

### ADR-005: Fallback Channel - Telegram Bot

**Context:** Need a backup notification channel for reliability.

**Decision:** Implement Telegram bot as secondary notification channel.

**Rationale:**
- 2-3 hours implementation time
- Works without app installation (good for quick testing)
- Inline buttons enable approve/reject without opening app
- Telegram's infrastructure is independent of FCM

**Consequences:**
- (+) Redundant notification path
- (+) Quick testing without app build
- (+) Additional user preference option
- (-) Requires separate bot registration
- (-) User must have Telegram installed

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MOBILE APP                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     Expo Router (Navigation)                 │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │   │
│  │  │Dashboard │ │Approvals │ │  Chat    │ │ Settings │       │   │
│  │  │  Tab     │ │   Tab    │ │   Tab    │ │   Tab    │       │   │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │   │
│  └───────┼────────────┼────────────┼────────────┼──────────────┘   │
│          │            │            │            │                   │
│  ┌───────▼────────────▼────────────▼────────────▼──────────────┐   │
│  │                    TanStack Query (Cache)                    │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────▼──────────────────────────────────┐   │
│  │                    Zustand Stores                            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐             │   │
│  │  │ Offline    │  │ Notif.     │  │ Theme      │             │   │
│  │  │ Queue      │  │ Prefs      │  │ Store      │             │   │
│  │  └────────────┘  └────────────┘  └────────────┘             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────▼──────────────────────────────────┐   │
│  │                    API Service (Axios)                       │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
└─────────────────────────────┼───────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    API Server (:8000)                        │   │
│  │  /api/tasks  /api/dashboard  /api/notifications  /api/chat  │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────▼──────────────────────────────────┐   │
│  │              Notification Service                            │   │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐  │   │
│  │  │ Web Push       │  │ FCM (Firebase) │  │ Telegram Bot  │  │   │
│  │  │ (Existing)     │  │ (New)          │  │ (New)         │  │   │
│  │  └────────────────┘  └────────────────┘  └───────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                             │                                       │
│  ┌──────────────────────────▼──────────────────────────────────┐   │
│  │                    Obsidian Vault                            │   │
│  │  /Needs_Action  /Pending_Approval  /Approved  /Done         │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Screen Components

```
app/
├── _layout.tsx                 # Root: QueryClient, Zustand, Theme providers
├── (tabs)/
│   ├── _layout.tsx             # Tab bar with 4 tabs + FAB
│   ├── index.tsx               # Dashboard: Stats + Activity feed
│   ├── approvals.tsx           # Approvals: Swipeable list
│   ├── chat.tsx                # Chat: Message list + input
│   └── settings.tsx            # Settings: Notifications, theme, server
├── approval/[id].tsx           # Detail: Full task view + actions
└── task/[id].tsx               # Task detail (from activity feed)
```

### Shared Components

```
components/
├── ui/
│   ├── Button.tsx              # Primary, secondary, ghost variants
│   ├── Card.tsx                # Dark card with border
│   ├── Badge.tsx               # Priority, status badges
│   ├── Input.tsx               # Text input with dark styling
│   ├── LoadingSkeleton.tsx     # Animated placeholder
│   └── Toast.tsx               # Success/error notifications
├── agent/
│   ├── AgentAvatar.tsx         # Animated pulsing avatar
│   ├── AgentTypingIndicator.tsx# Three bouncing dots
│   ├── AgentStatusPulse.tsx    # Online/offline indicator
│   └── AgentMessage.tsx        # Chat bubble with animations
├── approvals/
│   ├── ApprovalCard.tsx        # Task card content
│   ├── SwipeableRow.tsx        # Gesture handler wrapper
│   ├── ApprovalActions.tsx     # Approve/reject buttons
│   └── PriorityBadge.tsx       # Urgent/High/Medium/Low
└── dashboard/
    ├── StatsCard.tsx           # Metric with icon
    ├── ActivityFeed.tsx        # Scrolling activity log
    ├── QuickActions.tsx        # FAB with action menu
    └── AgentStatusCard.tsx     # System overview
```

---

## Data Flow

### Approval Flow

```
1. Orchestrator detects pending approval
   │
   ▼
2. Backend calls push_service.send_notification()
   │
   ├─► Web Push (existing PWA)
   ├─► FCM (mobile app)
   └─► Telegram Bot (fallback)
   │
   ▼
3. Mobile receives FCM notification
   │
   ├─ App foreground: In-app alert
   ├─ App background: System notification
   └─ App killed: System notification
   │
   ▼
4. User taps notification
   │
   ▼
5. App opens to /approval/[id] screen
   │
   ▼
6. User swipes right (approve)
   │
   ▼
7. Optimistic UI update (remove from list)
   │
   ▼
8. API call: POST /api/tasks/{id}/approve
   │
   ├─ Success: Confirm, invalidate queries
   └─ Failure: Rollback UI, show error toast
```

### Offline Flow

```
1. User swipes to approve while offline
   │
   ▼
2. Check network status
   │
   └─ Offline detected
      │
      ▼
3. Add to offline queue (Zustand + AsyncStorage)
   │
   ▼
4. Show "Pending sync" indicator on item
   │
   ▼
5. NetInfo detects network restored
   │
   ▼
6. processQueue() called automatically
   │
   ▼
7. For each queued action:
   ├─ Call API
   ├─ On success: Remove from queue
   └─ On failure: Increment retry count
   │
   ▼
8. Invalidate queries to refresh UI
```

---

## API Integration

### API Service Configuration

```typescript
// services/api.ts
const api = axios.create({
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// Dynamic base URL from AsyncStorage
api.interceptors.request.use(async (config) => {
  const baseUrl = await AsyncStorage.getItem('api_base_url') || DEFAULT_URL;
  config.baseURL = baseUrl;
  return config;
});

export const apiService = {
  // Dashboard
  getDashboard: () => api.get('/api/dashboard'),

  // Tasks
  getTasks: (folder: string, limit = 20) =>
    api.get('/api/tasks', { params: { folder, limit } }),
  getTask: (id: string) => api.get(`/api/tasks/${id}`),
  approveTask: (id: string, note?: string) =>
    api.post(`/api/tasks/${id}/approve`, { approved: true, note }),
  rejectTask: (id: string, note?: string) =>
    api.post(`/api/tasks/${id}/approve`, { approved: false, note }),

  // Notifications
  registerPush: (token: string, device: string) =>
    api.post('/api/notifications/subscribe', { fcm_token: token, device_name: device }),

  // Health
  health: () => api.get('/api/health'),
};
```

### TanStack Query Hooks

```typescript
// hooks/useApprovals.ts
export function useApprovals() {
  return useQuery({
    queryKey: ['approvals'],
    queryFn: () => apiService.getTasks('Pending_Approval').then(r => r.data.tasks),
    refetchInterval: 30000,
    staleTime: 10000,
  });
}

export function useApproveTask() {
  const queryClient = useQueryClient();
  const { addAction } = useOfflineQueueStore();
  const isOnline = useNetworkStatus();

  return useMutation({
    mutationFn: async ({ taskId, note }) => {
      if (!isOnline) {
        addAction({ type: 'approve', payload: { taskId, note } });
        return { queued: true };
      }
      return apiService.approveTask(taskId, note);
    },
    onMutate: async ({ taskId }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['approvals'] });
      const previous = queryClient.getQueryData(['approvals']);
      queryClient.setQueryData(['approvals'], (old) =>
        old?.filter(t => t.id !== taskId)
      );
      return { previous };
    },
    onError: (_, __, context) => {
      queryClient.setQueryData(['approvals'], context?.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] });
    },
  });
}
```

---

## Backend Modifications

### 1. FCM Support in Push Service

**File:** `src/notifications/push_service.py`

```python
# Add to existing PushNotificationService class

async def send_fcm_notification(
    self,
    fcm_token: str,
    notification: NotificationPayload
) -> Dict[str, Any]:
    """Send notification via Firebase Cloud Messaging."""
    try:
        from firebase_admin import messaging

        message = messaging.Message(
            notification=messaging.Notification(
                title=notification.title,
                body=notification.body,
            ),
            data={k: str(v) for k, v in (notification.data or {}).items()},
            token=fcm_token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    icon='notification_icon',
                    color='#2563eb',
                    channel_id='approvals' if notification.tag == 'approval' else 'default',
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        badge=1,
                        sound='default',
                    )
                )
            )
        )

        response = messaging.send(message)
        self.logger.info(f"FCM notification sent: {response}")
        return {"success": True, "message_id": response}

    except Exception as e:
        self.logger.error(f"FCM send failed: {e}")
        return {"success": False, "error": str(e)}
```

### 2. Firebase Initialization

**New File:** `src/notifications/firebase_config.py`

```python
import firebase_admin
from firebase_admin import credentials
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

_firebase_initialized = False

def init_firebase():
    """Initialize Firebase Admin SDK."""
    global _firebase_initialized
    if _firebase_initialized:
        return True

    cred_path = Path("config/firebase-service-account.json")
    if not cred_path.exists():
        logger.warning("Firebase credentials not found. FCM disabled.")
        return False

    try:
        cred = credentials.Certificate(str(cred_path))
        firebase_admin.initialize_app(cred)
        _firebase_initialized = True
        logger.info("Firebase Admin SDK initialized")
        return True
    except Exception as e:
        logger.error(f"Firebase init failed: {e}")
        return False
```

### 3. Telegram Bot Integration

**New File:** `src/notifications/telegram_bot.py`

```python
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token)
        self._app: Optional[Application] = None

    async def send_approval_request(
        self,
        task_id: str,
        title: str,
        description: str,
        priority: str = "medium"
    ):
        """Send approval request with inline buttons."""
        priority_emoji = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{task_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{task_id}")
            ]
        ])

        text = (
            f"🔔 *Approval Required*\n\n"
            f"{priority_emoji} *{title}*\n\n"
            f"{description[:200]}{'...' if len(description) > 200 else ''}"
        )

        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    async def send_digest(self, pending_count: int, completed_today: int):
        """Send daily digest summary."""
        text = (
            f"📊 *Daily Digest*\n\n"
            f"⏳ Pending approvals: {pending_count}\n"
            f"✅ Completed today: {completed_today}\n\n"
            f"Use /pending to see details."
        )
        await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode="Markdown")
```

---

## Deployment (Fly.io)

### Why Fly.io?
- **Free tier**: 3 shared VMs, 160GB bandwidth/month
- **Easy deploy**: Single command (`fly deploy`)
- **Auto HTTPS**: Free SSL certificates
- **Global edge**: Deploy close to users
- **No credit card** required for free tier

### Fly.io Setup

1. **Install Fly CLI:**
   ```bash
   # Windows (PowerShell)
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

   # Linux/Mac
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Create fly.toml:**
   ```toml
   app = "abdullah-junior-api"
   primary_region = "ord"  # Chicago, or pick closest

   [build]
     dockerfile = "Dockerfile"

   [http_service]
     internal_port = 8000
     force_https = true
     auto_start_machines = true
     auto_stop_machines = true

   [env]
     FTE_ROLE = "cloud"
   ```

4. **Launch app:**
   ```bash
   fly launch --name abdullah-junior-api
   ```

5. **Set secrets:**
   ```bash
   fly secrets set TELEGRAM_BOT_TOKEN=xxx
   fly secrets set TELEGRAM_CHAT_ID=xxx
   fly secrets set ANTHROPIC_API_KEY=xxx
   ```

6. **Deploy:**
   ```bash
   fly deploy
   ```

7. **Your API is live:**
   ```
   https://abdullah-junior-api.fly.dev
   ```

### Firebase Setup

1. Create Firebase project at console.firebase.google.com
2. Add Android app with package name `com.abdullahjunior.mobile`
3. Add iOS app with bundle ID `com.abdullahjunior.mobile`
4. Download `google-services.json` and `GoogleService-Info.plist`
5. Generate service account key for backend
6. Enable Cloud Messaging API

---

## Testing Strategy

### Unit Tests

- API service methods (mock axios)
- Zustand store actions
- Utility functions (formatters, validators)

### Integration Tests

- FCM token retrieval on device
- API calls with real backend
- Notification tap navigation

### E2E Tests

1. **Happy Path**: Notification → Tap → Approve → Done
2. **Offline Mode**: Approve offline → Come online → Sync
3. **Error Recovery**: API error → Rollback → Retry

### Device Matrix

| Device | OS Version | Test Priority |
|--------|------------|---------------|
| Pixel 7 | Android 14 | P0 |
| Samsung S23 | Android 13 | P1 |
| iPhone 14 | iOS 17 | P0 |
| iPhone 12 | iOS 16 | P1 |

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Foundation | 3-4 days | Project setup, base components, navigation |
| Core Features | 4-5 days | Dashboard, approvals list, API integration |
| Push Notifications | 3-4 days | FCM setup, backend integration, tap handling |
| Enhanced UX | 3-4 days | Swipe gestures, animations, chat, offline |
| Polish | 2-3 days | Error handling, accessibility, testing |
| **Total** | **15-20 days** | Production-ready app |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| FCM delivery delays | Telegram bot fallback |
| iOS App Store rejection | Follow HIG; prepare justification docs |
| Expo SDK bugs | Pin to stable version; have bare RN fallback plan |
| Backend API changes | Version endpoints; maintain backwards compatibility |
